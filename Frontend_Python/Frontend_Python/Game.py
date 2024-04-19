"""
@package FantastycznaTriada
Dokumentacja dla modułu Game.

Zawiera klasy Node, Indicator i Overworld, oraz zmienne globalne 
level_1, level_2, level_3 ktore zawieraja 
informacje o pozycji przycisku danego poziomu, ktory poziom jest odblokowany po nim, 
oraz grafiki przyciskow reprzentujacych poziom
Zawiera rowniez liste levels ktora zawiera powyzsze zmienne.
"""

import pygame
from time import sleep
import os

"""
Zmienne globalne z informacjami na temat przyciskow kierujacych do poszczegolnych poziomow
"""

level_1 = {'position':(600,150), 'unlock':1, 'image_path_unlocked':'/Assets/nodes/node_1.jpg','image_path_locked':'/Assets/nodes/node_1.jpg'}
level_2 = {'position':(600,350), 'unlock':2, 'image_path_unlocked':'/Assets/nodes/node_2.jpg','image_path_locked':'/Assets/nodes/node_2_not.jpg'}
level_3 = {'position':(600,550), 'unlock':2, 'image_path_unlocked':'/Assets/nodes/node_3.jpg','image_path_locked':'/Assets/nodes/node_3_not.jpg'}

levels = {
    0: level_1,
    1: level_2,
    2: level_3
    }

class Node(pygame.sprite.Sprite):
    """
    Klasa reprezentujaca przyciski na ekranie wyboru poziomu i ekranie startowym
    
    Parametry:
    - pos - pozycja
    - status - czy poziom jest odblokowany czy nie
    - image_path_1 - sciezka do grafiki odblokowanego przycisku
    - image_path_2 - sciezka do grafiki zablokowanego przycisku
    """
    def __init__(self,pos, status, image_path_1, image_path_2):
        super().__init__()
        
        if status == 'available':
           self.image = pygame.image.load((os.path.dirname(__file__) + image_path_1))
        else:
           self.image = pygame.image.load((os.path.dirname(__file__) + image_path_2))

        self.rect = self.image.get_rect(center = pos)

class Indicator(pygame.sprite.Sprite):
    """
    Klasa reprezentujaca strzalke wyboru

    Parametry:
    - pos - pozycja strzalki
    """
    def __init__(self,pos):
         super().__init__()
         self.image = pygame.image.load((os.path.dirname(__file__) + '/Assets/arrow-right.png'))
         self.rect = self.image.get_rect(center = pos)

class Overworld:
    """
    Klasa reprezentujaca ekran wyboru poziomu:
    
    Parametry:
    - start_level - obecny poziom
    - max_level - najwyzszy odblokowany poziom
    - surface - ekran wyjsciowy
    - create_level - metoda polimorficzna z klasy Game, tworzaca poziom
    """
    def __init__(self, start_level, max_level, surface, create_level):
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.image = pygame.image.load((os.path.dirname(__file__) + '/Assets/overworld_background.png'))
        self.create_level = create_level

        self.setup_nodes()
        self.setup_indicator()

    def setup_nodes(self):
        """
        Metoda tworzaca wektor przyciskow na podstawie danych w wektorze level
        """
        self.nodes = pygame.sprite.Group()
        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                 node_sprite = Node(node_data['position'], 'available', node_data['image_path_unlocked'], node_data['image_path_locked'])
                 self.nodes.add(node_sprite)
            else:
                node_sprite = Node(node_data['position'], 'locked', node_data['image_path_unlocked'], node_data['image_path_locked'])
                self.nodes.add(node_sprite)

    def setup_indicator(self):
        """
        Metoda tworzaca strzalke w pozycji obecnego poziomu
        """
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Indicator(((self.nodes.sprites()[self.current_level].rect.x - 50),self.nodes.sprites()[self.current_level].rect.y +50) )
        self.icon.add(icon_sprite)

    def input(self, time):
        """
        Metoda pobierajaca dane o wcisnietych przyciskach, oraz blokujaca zbyt 
        szybkie wczytanie przycisku enter z ekranu startowego

        Parametry:
        - time - czas wcisniecia enter na ekranie startowym
        """
        keys = pygame.key.get_pressed()

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_DOWN] and not self.down_pressed and self.current_level < self.max_level:
            self.current_level += 1
            self.down_pressed = True
        elif keys[pygame.K_UP] and not self.up_pressed and self.current_level > 0:
            self.current_level -= 1
            self.up_pressed = True
        elif keys[pygame.K_RETURN] and current_time-time > 3500:
            self.create_level(self.current_level)

        if not keys[pygame.K_DOWN]:
            self.down_pressed = False
        if not keys[pygame.K_UP]:
            self.up_pressed = False

    def update_indicator(self):
        """
        Metoda zmieniajaca polozenie strzalki po zmianie obecnie wybranego poziomu
        """
        self.icon.sprite.rect.center = ((self.nodes.sprites()[self.current_level].rect.x - 50),self.nodes.sprites()[self.current_level].rect.y +50)
        

    def run(self, time):
        """
        Metoda zajmujaca sie odswiezaniem ekranu w petli
        
        Parametry:
        - time - czas wcisniecia enter na ekranie startowym
        """
        self.display_surface.blit(self.image,(0,0))
        self.nodes.draw(self.display_surface)
        self.input(time)
        self.update_indicator()
        self.icon.draw(self.display_surface)