"""
@package FantastycznaTriada
Dokumentacja dla modułu Classes.

Zawiera klasy Player i Level.
"""

#external modules
import pygame
from csv import reader
import os
#PyBind11 module
#import superfastcode2 as backend
#py modules
import settings
from Tiles import Tile, StaticTile, Background, AnimatedTile, Enemy, Weapon
from Game import Overworld
import Game
from time import sleep
import asyncio


def import_csv_layout(path):
    """
    Importuje dane o układzie mapy z pliku CSV.
    funkcja nie jest juz wykorzystywana - zamiast niej 
    zaimplementowano funkcje read_csv_to_numpy w module backend
    (funkcja jest niezakomentowana ze wzgledu na brak obslugi 
    modulu PyBind11 na niektorych urzadzeniach (np chromebook))
    """
    terrain_map = []
    with open(path) as map:
        level = reader(map,delimiter = ',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map

class Player(pygame.sprite.Sprite):
    """Klasa reprezentująca gracza
       Parametry:
       - pos - pozycja pojawienia sie gracza
       - change_health - metoda polimofriczna z klasy Game
       - level_id - numer poziomu, na jego podstawie 
         zmieniana jest grafika postaci
    """
    def __init__(self,pos, change_health, level_id):
        super().__init__()
        self.level = level_id
        self.import_assets()
        self.frame_index = 0
        self.ani_speed = 0.15
        self.image =  pygame.transform.scale(self.animations['idle'][self.frame_index], (64,64))
        self.rect = self.image.get_rect(topleft = pos)
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -18
        self.status = 'idle'
        self.facing_right = True
        self.change_health = change_health
        self.invincibility = False
        self.invinc_duration = 100
        self.hurt = 0
        


    def facing(self):
        """
        Zwraca:
        - self.facing_right - informacja, czy gracz patrzy w prawo.
        """
        return self.facing_right

    def import_assets(self):
        """Importuje zasoby animacji gracza zależnie od poziomu."""
        if self.level == 1:
            character_path = os.path.dirname(__file__) + '/Assets/Natasha/'
        elif self.level == 2:
            character_path = os.path.dirname(__file__) + '/Assets/Irna/'
        elif self.level == 3:
            character_path = os.path.dirname(__file__) + '/Assets/Shin-ah/'
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = settings.import_folder(full_path)

    def animate(self):
        """Aktualizuje animację gracza na podstawie bieżącego statusu."""
        animation = self.animations[self.status]
        self.frame_index += self.ani_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = pygame.transform.scale(animation[int(self.frame_index)], (64, 64))
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

    def get_input(self):
        """Pobiera dane wejściowe od użytkownika."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            self.jump()

    def get_status(self):
        """Ustala bieżący status gracza na podstawie kierunku 
        i prędkości poruszania się."""
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 0:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def apply_gravity(self):
        """Zastosowuje wartość grawitacji do poruszania się gracza w pionie."""
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        """Wykonuje skok gracza, jeśli gracz może skoczyc 
        (uniemozliwienie podwojnego skoku)"""
        if self.status == 'run' or self.status == 'idle':
            self.direction.y = self.jump_speed

    def update(self):
        """Aktualizuje stan gracza na podstawie danych wejściowych i animacji."""
        self.get_input()
        self.get_status()
        self.animate()






class Level():
    """Klasa obsługująca logike gry i wszystkie jej elementy
    Parametry: 
    - level_data - lista sciezek do odpowiednich plikow csv z danymi o poziomie
    - surface - ekran wyjściowy
    - create_overworld - metoda przekazana z klasy Game (rodzaj polimorfizmu),
        wywołuje powrót do ekranu wyboru poziomu
    - change_health - metoda przekazana z klasy Game, zmienia poziom zdrowia gracza,
        który klasa Game wypisuje na ekran
    - health - obecny stan zdrowia
    """
    def __init__ (self,level_data,surface,create_overworld,change_health, health):
        self.display_surface = surface
        self.world_shift = 0
        self.frame_index = 0
        self.invincibility = 0
        self.level_id = 0
        if level_data == settings.level_1:
            self.level_id = 1
        elif level_data == settings.level_2:
            self.level_id = 2
        elif level_data == settings.level_3:
            self.level_id = 3
        self.new_max_level = Game.levels[self.level_id-1]['unlock']
        self.health = health
        self.create_overworld = create_overworld
        self.is_dead = False
        self.change_health = change_health

        result = asyncio.run(settings.process_level_data(level_data))

        """
        pobranie tablic rozkladu poziomu z asynchronicznie tworzonej listy "result"
        """
        terrain_layout, player_layout, enemy_layout = result

        """terrain"""
        self.terrain = self.create_tile_group(terrain_layout['terrain'],'terrain')
        """player"""
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout['player'], change_health)
        """enemies"""
        self.enemies = self.create_tile_group(enemy_layout['enemies'],'enemies')
        self.constraint = self.create_tile_group(enemy_layout['enemies'],'constraint')
        """background"""
        self.background = Background(level_data['background'],1)
        """miecz"""
        self.sword = pygame.sprite.GroupSingle()

        
       
    def player_setup(self,layout, change_health):
        """
        Zczytanie z tablicy rozkladu poziomu pozycje startową gracza 
        oraz pozycje flagi (koniec poziomu)

        Parametry:
        - layout - rozklad poziomu
        - change_health - metoda zmieniająca zdrowie, 
            przekazywana obiektowi Player
        """
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * settings.poziom.tile_size
                y = row_index * settings.poziom.tile_size
                if val == 0:
                    sprite = Player((x,y), change_health, self.level_id)
                    self.player.add(sprite)
                if val == 2:
                    surface = pygame.image.load((os.path.dirname(__file__) + '//Assets//goal.png')).convert_alpha()
                    sprite = StaticTile(settings.poziom.tile_size,x,y,surface)
                    self.goal.add(sprite)
                    

    def attack(self):
        """
        Logika ataku mieczem, obejmująca zczytanie wcisniecia klawisza 
        shift oraz zapamietanie stanu animacji 
        (ze wzgledu na tworzenie nowej instancji miecza z kazdym tickiem, 
        animacja sie nie porusza bez zapamietania jej stanu)
        """
        keys = pygame.key.get_pressed()
        weapon = Weapon(64, self.player.sprite.rect.x, self.player.sprite.rect.y, self.level_id)
        
        if keys[pygame.K_RSHIFT]:
            self.frame_index += 0.5
            if self.frame_index >= 3:
                self.frame_index = 0
            self.sword.add(weapon)
            weapon.update(self.world_shift, self.player.sprite.facing(), self.frame_index)
        else:
            self.sword.empty()

        self.sword.draw(self.display_surface)

    def damage(self):
        """
        Logika zmniejszenia zdrowia i sprawdzenia czy zdrowie nie jest 0
        """
        self.change_health(-1)
        if self.health() <= 0:
            self.is_dead = True

    def check_enemy_collision(self):
        """
        Logika kolizji gracz-przeciwnik oraz miecz-przeciwnik
        W przypadku kolizji gracz przeciwnik wywoływana jest metoda damage() 
        wraz ze zmianą zmiennej self.invincibility:
        ta zmienna jest kluczowa ponieważ funkcja wywoluje sie 30 razy na 
        sekunde co powoduje wrecz natychmiastowe zmniejszenie
        licznika zdrowia do zera w przypadku kontaktu z przeciwnikiem,
        ograniczenie zmniejszania zdrowia do 6 razy na sekunde pozwala graczowi
        zareagowac i uciec od zagrozenia bez tracenia calego zdrowia
        W przypadku kolizji miecz-przeciwnik wywoływana jest metoda 
        usunięcia przeciwnika z listy przeciwników, czyli "zabicie" go
        """
        enemy_collisions_player = pygame.sprite.spritecollide(self.player.sprite, self.enemies, False)
        enemy_collisions_sword = pygame.sprite.groupcollide(self.sword, self.enemies, False, False)

        if enemy_collisions_sword:
            for sword in enemy_collisions_sword:
                enemies_hit = enemy_collisions_sword[sword]
                for enemy in enemies_hit:
                    enemy.kill()

        if enemy_collisions_player:
            for enemy in enemy_collisions_player:
                self.invincibility += 0.2
                if self.invincibility > 1:
                    self.damage()
                    self.invincibility = 0
            
    def check_goal(self):
        """
        Metoda sprawdzajaca czy flaga zostala zebrana, jesli tak (czyli, 
        jesli nastapila kolizja gracz-flaga)
        wywolywana jest polimorficzna metoda create_overworld, 
        ktora wypisuje znowu ekran wyboru poziomu, tym razem
        z nowo odblokowanym poziom (np. w przypadku ukonczenia poziomu 1, 
        dostepny bedzie juz poziom 2)
        """
        collisions = pygame.sprite.spritecollide(self.player.sprite, self.goal, False)        
        if collisions:
            self.create_overworld(0, self.new_max_level)


    def check_fall(self):
        """
        Metoda zmniejszajaca zdrowie gracza gdy wypadnie poza mape - 
        to pewna smierc wiec nie zastosowano ograniczenia
        """
        if self.player.sprite.rect.y > settings.poziom.screen_height:
            self.damage()

    def create_tile_group(self,layout,type):
        """
        Metoda odpowiadajaca za zczytanie z listy rozkladu poziomu pozycji 
        każdej grafiki, oraz zapisanie jej do tymczasowego
        wektora sprite'ow, który jest potem zwracany
        
        Parametry:
        - layout - lista z rozkladem poziomu
        - type - zmienna typu string zawierajaca informacje o rodzaju rozkladu, 
            ktory bedzie analizowany
        typy rozkladow to: 
        'terrain' - teren
        'enemies' - miejsce pojawienia sie przeciwnika
        'constraint' - niewidzialne i niekolidowalne z graczem obiekty, 
            wyznaczaja przeciwnikom pole poruszania sie

        Zwraca:
        - sprite_group - kontener obiektow typu pygame.sprite, czyli obiektu, 
        ktory zawiera grafike, rozmiar i koordynaty polozenia
        jest obiektem, ktory mozna latwo wypisac na ekran oraz zaktualizowac
        """
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != -1:
                    x = col_index * settings.poziom.tile_size
                    y = row_index * settings.poziom.tile_size

                    if type == 'terrain':
                        if self.level_id == 1:
                            terrain_list = settings.import_all_graphics((os.path.dirname(__file__) + '//Assets//Ground_Level1'))
                        elif self.level_id == 2:
                            terrain_list = settings.import_all_graphics((os.path.dirname(__file__) + '//Assets//Ground_Level2'))
                        elif self.level_id == 3:
                            terrain_list = settings.import_all_graphics((os.path.dirname(__file__) + '//Assets//Ground_Level3'))

                        tile_surface = terrain_list[int(val)]
                        sprite = StaticTile(settings.poziom.tile_size,x,y,tile_surface)
                        sprite_group.add(sprite)

                    if type == 'enemies':
                        if val == 0:
                            sprite = Enemy(settings.poziom.tile_size,x,y, self.level_id)
                            sprite_group.add(sprite)
                    if type == 'constraint':
                        if val == 1:
                            sprite = Tile((x,y),settings.poziom.tile_size)
                            sprite_group.add(sprite)


        return sprite_group

    def enemy_collision_reverse(self):
        """
        Logika ograniczenia pola ruchu przeciwnikow, 
        gdy przeciwnik trafi na ograniczenie (w wektorze self.constraint)
        to zmienia swoja predkosc poruszania na przeciwna - porusza sie w przeciwna strone
        oraz jego ikona zostaje obrocona
        """
        for enemy in self.enemies.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint, False):
                enemy.reverse()
    
    def scroll_x(self):
        """
        Logika przesuwania poziomu
        Jesli gracz wysunie sie za bardzo w lewo lub prawo - 
        jego predkosc jest ustawiana na 0, w zamian tego poruszany jest teren
        zapobiega to wyjsciu gracza poza ekran
        """
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < 400 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > 800 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_col(self):
        """
        Metoda odpowiadajaca za logike kolizji na osi x gracza z terenem 
        Logika jest nastepujaca:
        - jesli gracz idzie w prawo, to nie moze przekroczyc 
        przez lewa sciane grafiki terenu
        - jesli gracz idzie w lewo, to nie moze przekroczyc 
        przez prawa sciane grafiki terenu
        """
        collidable_sprites = self.terrain.sprites()
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    def vertical_col(self):
        """
        Metoda odpowiadajaca za logike kolizji na osi y gracza z terenem
        Logika jest analogiczna do logiki funkcji horizontal_col()
        Ta metoda dodatkowo wywoluje funkcje player.apply_gravity(), ktora 
        z kazda iteracja petli gry sciaga gracza w dol - symulacja grawitacji
        """
        collidable_sprites = self.terrain.sprites()
        player = self.player.sprite
        player.apply_gravity()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                elif player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0


    def run(self):
        """
        Metoda ktora aktualizuje kazdy aspekt poziomu
        
        Zwraca:
        - self.is_dead - jesli zdrowie gracza spadlo do zera w iteracji, 
        gra jest zatrzymywana z poziomu glownej petli w funkcji main()
        """
        self.background.draw(self.display_surface)
        self.background.update(self.world_shift)

        self.terrain.update(self.world_shift)
        self.terrain.draw(self.display_surface)
        
        self.player.draw(self.display_surface)
        self.player.update()

        self.enemies.update(self.world_shift)
        self.constraint.update(self.world_shift)
        self.enemy_collision_reverse()
        self.check_enemy_collision()
        self.enemies.draw(self.display_surface)

        self.horizontal_col()
        self.vertical_col()
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        self.check_goal()
        self.attack()
        self.check_fall()

        self.scroll_x()

        return self.is_dead
        

    
