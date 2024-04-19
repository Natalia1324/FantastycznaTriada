"""
@package FantastycznaTriada
Dokumentacja dla modułu Health.

Zawiera klase Health ktora odpowiada za wypisanie odpowiedniej grafiki w zaleznosci od zdrowia
"""

import pygame
import os

class Health:
    """
    Klasa odpowiadajaca za wypisanie obecnej ilosci zdrowia

    Parametry:
    - surface - ekran wyjsciowy
    """
    def __init__(self,surface):
        self.display_surface = surface

        self.heart_full = pygame.image.load(os.path.dirname(__file__) + '/Assets/hearts/heart_full.png').convert_alpha()
        self.heart_half = pygame.image.load(os.path.dirname(__file__) + '/Assets/hearts/heart_half.png').convert_alpha()
        self.heart_empty = pygame.image.load(os.path.dirname(__file__) + '/Assets/hearts/heart_empty.png').convert_alpha()
        

    def show_health(self,current,full):
        """
        Metoda odpowiadajaca za wypisanie obecnej ilosci zdrowia w formie serduszek: całego, pół, lub pustego

        Parametry:
        - current - obecne zdrowie gracza
        - full - maksymalna ilosc zdrowia gracza
        """
        #self.display_surface.blit(self.health,(20,10))
        full_hearts = current // 2  # Liczba pełnych serduszek
        half_heart = current % 2  # Czy występuje pół serduszka?
        empty_hearts = full/2 - full_hearts - half_heart
        
        if current > 0:
            for i in range(full):
                if full_hearts > i:
                # Pełne serduszko
                    self.display_surface.blit(self.heart_full, (i * self.heart_full.get_width() + 3, 0))
                elif full_hearts == i and half_heart:
                # Pół serduszka
                    self.display_surface.blit(self.heart_half, (i * self.heart_full.get_width() + 3, 0))
                else:
                    if (empty_hearts > 0):
                        self.display_surface.blit(self.heart_empty, (i * self.heart_full.get_width()+ 3, 0))
                        empty_hearts -= 1