"""
@package FantastycznaTriada
Dokumentacja dla modułu Tiles.

Zawiera wszystkie klasy odpowiedzialne za obiekty wypisywane na ekran (oprocz klasy Player):
- Tile
- StaticTile
- AnimatedTile
- Weapon
- Enemy
- Background
Wszystkie powyższe klasy z wyjatkiem Background sa dziedziczone po klasie 
pygame.sprite.Sprite co nadaje im funkcjonalnosc wypisania na ekran
"""


import pygame
import os
import settings
from random import randint
from settings import level_1, level_2, level_3



class Tile(pygame.sprite.Sprite):
    """
    Prosta klasa opisujaca obiekt wypisywalny na ekran

    Parametry:
    - pos - pozycja obiektu
    - size - rozmiar obiektu
    """
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = pos)

    def update(self, x_shift):
        """ zmiana pozycji obiektu w zaleznosci od poruszania sie tla """
        self.rect.x += x_shift


class StaticTile(Tile):
    """
    Klasa dziedziczaca po klasie Tile, dodaje funkcjonalnosc wlasnej grafiki

    Parametry:
    - size - rozmiar
    - x,y - pozycja obiektu
    - surface - warstwa z grafika obiektu
    """
    def __init__(self,size,x,y,surface):
        super().__init__((x,y),size)
        self.image = surface



class AnimatedTile(Tile):
    """
    Klasa dziedziczaca po klasie Tile, dodaje funkcjonalnosc wlasnej animowanej grafiki

    Parametry:
    - size - rozmiar
    - x,y - pozycja obiektu
    - path - sciezka do folderu z grafika animacji
    """
    def __init__(self,size,x,y,path):
        super().__init__((x,y),size)
        self.frames = settings.import_all_graphics(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        """
        Metoda, ktora iteruje po wektorze klatek i wypisuje je na ekran
        """
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self,shift):
        """
        Metoda ktora odpowiada za animacje oraz przesuniecie obiektu w zaleznosci od przesuniecia tla
        
        Parametry:
        - shift - predkosc przesuniecia tla
        """
        self.animate()
        self.rect.x += shift

class Weapon(AnimatedTile):
    """
    Klasa dziedziczaca po AnimatedTile, reprezentuje bron postaci

    Parametry:
    - size - rozmiar obiektu
    - x,y - pozycja obiektu
    - level_id - numer poziomu
    """
    def __init__(self, size, x, y, level_id):
        if level_id == 1:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/Sword_Animation_1/'))
        elif level_id == 2:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/Sword_Animation_2/'))
        elif level_id == 3:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/Sword_Animation_3/'))

        self.facing_right = True
        self.rect.x = x
        self.rect.y = y + 10

    def update(self, shift, facing_right, frame_index):
        """
        Metoda ktora aktualizuje pozycje miecza (w zaleznosci czy gracz zwrocony jest w prawo czy w lewo)
        oraz aktualizuje animacje (index klatki animacji jest trzymany w metodzie klasy Level)

        Parametry:
        - facing_right - czy gracz jest zwrocony w lewo czy nie
        - frame_index - klatka animacji
        """
        self.frame_index = frame_index
        self.facing_right = facing_right
       
        if self.facing_right:
            self.rect.x += 50  
        else:
            self.rect.x -= 50 
        
        self.rect.x += shift
        self.animate()

    def animate(self):
        """
        Metoda ktora implementuje animacje, oraz obrocenie miecza w zaleznosci od kierunku w jaki jest skierowany
        """
        self.image = self.frames[int(self.frame_index)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
       

      

class Enemy(AnimatedTile):
    """
    Klasa dziedziczaca po AnimatedTile, reprezentuje przeciwnika

    Parametry:
    - size - rozmiar obiektu
    - x,y - pozycja obiektu
    - level_id - numer poziomu
    """

    def __init__(self,size,x,y, level_id):
        if level_id == 1:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/slimes/Level_1/'))
        elif level_id == 2:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/slimes/Level_2/'))
        elif level_id == 3:
            super().__init__(size,x,y,(os.path.dirname(__file__) + '/Assets/slimes/Level_3/'))
        self.rect.y += size - self.image.get_size()[1] + 3
        self.speed = randint(3,5)

    def move(self):
        """
        Metoda odpowiadajaca za ruch przeciwnika
        """
        self.rect.x += self.speed

    def reverse_image(self):
        """
        Metoda odpowiadająca za obrocenie grafiki przeciwnika jesli idzie on w lewo
        """
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        """
        Metoda zmieniajaca kierunek ruchu przeciwnika
        """
        self.speed *= -1

    def update(self,shift):
        """
        Metoda ktora odpowiada za animacje, ruch oraz przesuniecie obiektu w zaleznosci od przesuniecia tla
        
        Parametry:
        - shift - predkosc przesuniecia tla
        """
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()



class Background:
    """
    Klasa odpowiadajaca za tlo poziomu

    Parametry:
    - background_path - sciezka do grafiki poziomu
    - horizon - poziom horyzontu
    """
    def __init__(self, background_path, horizon):
        
        self.background = pygame.image.load(background_path)
        self.background2 = self.background.copy()
        self.horizon = horizon
        self.x = 0
        self.x2 = self.background.get_width()

        self.filter = pygame.Surface((self.background.get_width(), self.background.get_height()),pygame.SRCALPHA)
        self.filter.fill((128, 128, 160, 20))

    def draw(self,surface):
        """
        Metoda wypisujaca tlo wraz z filtrem rozmazujacym na ekran

        Parametry:
        - surface - ekran wyjsciowy
        """
        for row in range(settings.poziom.vertical_tile_number):
            y = row * settings.poziom.tile_size
            if row < self.horizon:
                surface.blit(self.background,(self.x,y))
                surface.blit(self.background2, (self.x2, y))
            surface.blit(self.filter, (0,0))

    def update(self, x_shift):
        """
        Metoda odpowiadajaca za wypisanie tla, i przesuniecie go w zaleznosci od predkosci przesuniecia tla, 
        odpowiada tez za zapetlanie tla

        Parametry:
        - x_shift - predkosc przesuniecia tla
        """
        self.x += x_shift/2
        self.x2 += x_shift/2

        if self.x + self.background.get_width() < 0:
            self.x = self.x2 + self.background2.get_width()

        if self.x - self.background.get_width() > 1200:
            self.x = self.x2 - self.background2.get_width()

        if self.x2 + self.background2.get_width() < 0:
            self.x2 = self.x + self.background.get_width()

        if self.x2 - self.background2.get_width() > 1200:
            self.x2 = self.x - self.background.get_width()