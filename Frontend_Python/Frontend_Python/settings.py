"""
@package FantastycznaTriada
Dokumentacja dla modułu settings.

Modul ten zawiera funkcje pomocnicze i zmienne globalne potrzebne do funkcjonowania programu
Zmienne globalne:
- poziom - obiekt klasy backend.Poziom() ktory zezwala na korzystanie z funkcji dostepnych w module backend
- level_1, level_2, level_3 - listy ze sciezkami do rozkladow poziomow i grafiki tla
"""


import pygame
import os
from os import walk
import asyncio
import backend

poziom = backend.Poziom()


directory = os.path.dirname(__file__)

level_1 = {
    'terrain':(directory + '/Assets/Level_1/FT_Level_1._terrain.csv'),
    'player':(directory + '/Assets/Level_1/FT_Level_1._playere.csv'),
    'enemies':(directory + '/Assets/Level_1/FT_Level_1._enemiese.csv'),
    'background':(directory + '/Assets/Backgrounds/background_level1.png')
    }

level_2 = {
    'terrain':(directory + '/Assets/Level_1/FT_Level_1._terrain.csv'),
    'player':(directory + '/Assets/Level_1/FT_Level_1._playere.csv'),
    'enemies':(directory + '/Assets/Level_1/FT_Level_1._enemiese.csv'),
    'background':(directory + '/Assets/Backgrounds/background_level2.png')
    }

level_3 = {
    'terrain':(directory + '/Assets/Level_1/FT_Level_1._terrain.csv'),
    'player':(directory + '/Assets/Level_1/FT_Level_1._playere.csv'),
    'enemies':(directory + '/Assets/Level_1/FT_Level_1._enemiese.csv'),
    'background':(directory + '/Assets/Backgrounds/background_level3.png')
    }

async def process_layout(layout_name, layout_path, result_container):
    """
    Funkcja asynchroniczna, która odczytuje plik CSV z określonej ścieżki, 
    przetwarza go na listę i przypisuje wynik do kontenera wynikowego o nazwie "result_container" pod kluczem "layout_name".
    
    Parametry:
    - layout_name - nazwa rozkladu
    - layout_path - sciezka do pliku rozkladu
    - result_container - kontener wynikowy
    """
    result = poziom.read_csv_to_numpy(layout_path)
    result = result.tolist()
    result_container[layout_name] = result

async def process_level_data(level_data):
    """
    Funkcja asynchroniczna, ktora przetwarza dane poziomu gry. 
    Tworzy kontenery dla układu terenu, układu gracza i układu przeciwników. 
    Następnie tworzy listę zadań, gdzie każde zadanie jest 
    wywołaniem funkcji "process_layout" 
    dla odpowiedniego typu układu (teren, gracz, przeciwnicy) 
    i przypisuje wynik do odpowiedniego kontenera. 
    Następnie, przy użyciu "await asyncio.gather(*tasks)", czeka na zakończenie 
    wszystkich zadań i zwraca kontenery z przetworzonymi 
    układami terenu, gracza i przeciwników.

    Parametry:
    - level_data - lista sciezek do plikow csv kazdego rozkladu

    Zwraca:
    - terrain_layout, player_layout, enemy_layout - kontenery z konkretnymi rozkladami w formie int array
    """
    terrain_layout = {}
    player_layout = {}
    enemy_layout = {}

    tasks = []

    tasks.append(process_layout('terrain', level_data['terrain'], terrain_layout))
    tasks.append(process_layout('player', level_data['player'], player_layout))
    tasks.append(process_layout('enemies', level_data['enemies'], enemy_layout))

    await asyncio.gather(*tasks)

    return terrain_layout, player_layout, enemy_layout

def import_all_graphics(path):
    """
    
    Funkcja służy do wczytania wszystkich grafik z danego katalogu. 
    Przechodzi przez pliki w podanej ścieżce, wczytuje obrazy przy użyciu 
    biblioteki Pygame i dodaje je do listy "tiles"

    Parametry:
    - path - sciezka do folderu z plikami
    
    Zwraca:
    - tiles - kontener z grafikami z folderu
    """
    tiles = []
   
    for file in os.listdir(path):
        dir = os.path.join(path, file)
        if os.path.isfile(dir):
            new_surf = pygame.Surface((poziom.tile_size,poziom.tile_size))
            new_surf = pygame.image.load(dir)
            tiles.append(new_surf)
    return tiles
            

def import_folder(path):
    """
    Funkcja służy do wczytania wszystkich obrazów z danego katalogu. 
    Przechodzi przez pliki w podanej ścieżce, wczytuje obrazy 
    przy użyciu biblioteki Pygame,
    konwertuje je na format z przezroczystością 
    (convert_alpha()) i dodaje je do listy "surface_list"

    Parametry:
    - path - sciezka do folderu
    
    Zwraca:
    - surface_list - kontener grafik
    """
    surface_list = []

    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list