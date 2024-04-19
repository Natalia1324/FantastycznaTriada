"""
@package FantastycznaTriada
Dokumentacja dla modułu Frontend_Python.

Zawiera klasy Game i StartScreen oraz funkcje main z glowna petla gry.
"""

import pygame
""" modul c++ - backend """
import backend
from time import sleep
from Classes import *
from settings import *
from Game import Overworld, Indicator
from Health import Health


pygame.init()
OKNO = pygame.display.set_mode((poziom.screen_width, poziom.screen_height))
pygame.display.set_caption('Fantastyczna Triada')

nodes = {'0':(320, 450), '1':(320, 580)}

global_time = 0

class StartScreen:
    """
    Klasa reprezentująca ekran startowy.
    """

    def __init__(self):
        self.current = 0
        self.setup_indicator()
        self.image = pygame.image.load((os.path.dirname(__file__) + '/Assets/StartScreen.jpg'))

    def setup_indicator(self):
        """
        Metoda ktora ustawia wskaźnik poziomu na aktualnej pozycji.
        """
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Indicator(nodes[str(self.current)])
        self.icon.add(icon_sprite)

    def input(self):
        """
        Metoda ktora obsługuje input od użytkownika.
        
        Zwraca:
        - true jesli wcisnieto enter
        - false jesli nie wcisnieto entera
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN] and self.current < 1:
            self.current += 1
        elif keys[pygame.K_UP] and self.current > 0:
            self.current -= 1
        elif keys[pygame.K_RETURN]:
            if self.current == 0:
                global_time = pygame.time.get_ticks()
                return True
            else:
                exit(0)
        return False
  

    def run(self):
        """
        Metoda ktora wyświetla ekran startowy i obsługuje wejście użytkownika.
        
        Zwraca:
        - true jesli self.input jest true
        - false jesli self.input jest false
        """
        OKNO.blit(self.image, (0, 0))
        if self.input():
            return True
        self.setup_indicator()
        self.icon.draw(OKNO)
        return False

class Game:
    """
    Klasa reprezentująca logikę gry.
    """

    def __init__(self):
        self.max_level = 0
        self.read_level()
        self.max_health = 6
        self.health = Health(OKNO)
        self.current_health = 6
        self.start_screen = StartScreen()
        self.overworld = Overworld(0, self.max_level, OKNO, self.create_level)
        self.status = 'ekran_startu'
        
    def change_health(self, amount):
        """
        Metoda ktora, zmienia aktualne zdrowie o określoną wartość.
        
        Parametry:
        - amount - Wartość, o którą ma zostać zmienione aktualne zdrowie.
        """
        self.current_health += amount

    def now_health(self):
        """
        Zwraca aktualne zdrowie.
        
        Zwraca:
        - self.current_health - aktualne zdrowie.
        """
        return self.current_health

    def read_level(self):
        """
        Metoda ktora odczytuje maksymalny poziom z pliku save.txt.
        """
        try:
            with open("save.txt", "r") as file:
                value = int(file.read())
                if value >= 0 and value <= 2:
                    self.max_level = value
                if value == 7:
                    pygame.display.set_caption('Totalnie Dziwna Gra?')
        except FileNotFoundError:
            pass

    def check_save_file(self):
        """
        Metoda ktora sprawdza istnienie pliku save.txt i zapisuje aktualny maksymalny poziom.
        """
        with open("save.txt", "w") as file:
            file.write(str(self.max_level))

    def create_level(self, current_level):
        """
        Metoda ktora tworzy poziom o określonym numerze.

        Parametry:
        - current_level - numer obecnego poziomu.
        """
        if current_level == 0:
            temp = level_1
        elif current_level == 1:
            temp = level_2
        elif current_level == 2:
            temp = level_3

        self.level = Level(temp, OKNO, self.create_overworld, self.change_health, self.now_health)
        self.status = 'poziom'

    def create_overworld(self, current_level, new_max_level):
        """
        Metoda ktora tworzy ekran wyboru poziomu.

        Parametry:
        - current_level - Aktualny poziom.
        - new_max_level - Nowy maksymalny poziom.
        """
        if self.max_level < new_max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, OKNO, self.create_level)
        self.check_save_file()
        self.status = 'ekran_wyboru'
    

    def run(self):
        """
        Uruchamia logikę gry.
        """
        if self.status == 'ekran_startu':
            if self.start_screen.run():
                self.status = 'ekran_wyboru'
        if self.status == 'ekran_wyboru':
            self.overworld.run(global_time)
        elif self.status == 'poziom':
            if not self.level.run():
                self.health.show_health(self.current_health, self.max_health)
            else:
                return False
        return True


icon = pygame.image.load((os.path.dirname(__file__) + "/Assets/icom.jpg")).convert_alpha()
pygame.display.set_icon(icon)
ZEGAR = pygame.time.Clock()
game = Game()
    

def main():
    """
    Funkcja główna.
    """
    run = True
    while run:
        ZEGAR.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
        if game.run() == False:
            OKNO.fill((0,0,0))
            white = (255, 255, 255)
            font = pygame.font.Font('freesansbold.ttf', 64)
            text = font.render('KONIEC GRY', True, white)
            textRect = text.get_rect()
            textRect.center = (settings.poziom.screen_width // 2, settings.poziom.screen_height // 2)
            OKNO.blit(text, textRect)
        
        pygame.display.update()   
       

    pygame.quit()

if __name__ == "__main__":
    main()