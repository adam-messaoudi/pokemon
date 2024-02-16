import pygame
# Importation des constantes de pygame
from pygame.locals import *
import time
import math
import random
import requests
import io
from urllib.request import urlopen
from move import Move
from move import display_message
from move import create_button


# Initialisation de pygame
pygame.init()

# Création de la fenêtre de jeu
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Pokemon Battle')

# Définition des couleurs utilisées dans le jeu
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

# URL de base de l'API Pokemon
base_url = 'https://pokeapi.co/api/v2'
pokemon_endpoint = '/pokemon'

# Classe représentant un Pokémon
class Pokemon(pygame.sprite.Sprite):
    
    def __init__(self, name, level, x, y):
        
        pygame.sprite.Sprite.__init__(self)
        
        # Appel de l'API Pokemon pour obtenir les données du Pokémon
        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.json = req.json()
        
        # Initialisation du nom et du niveau du Pokémon
        self.name = name
        self.level = level
        
        # Position du sprite sur l'écran
        self.x = x
        self.y = y
        
        # Nombre de potions restantes
        self.num_potions = 3
        
        # Obtention des statistiques du Pokémon depuis l'API
        stats = self.json['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat']
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat']
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']
                
        # Types du Pokémon
        self.types = []
        for i in range(len(self.json['types'])):
            type = self.json['types'][i]
            self.types.append(type['type']['name'])
            
        # Taille du sprite
        self.size = 150
        
        # Initialisation du sprite du Pokémon
        self.set_sprite('front_default')
    

    def perform_attack(self, other, move):
        
        display_message(f'{self.name} used {move.name}')
        
        # Pause de 1 seconde
        time.sleep(1)
        
        # Calcul des dégâts
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power
        
        # Bonus de même type d'attaque (STAB)
        if move.type in self.types:
            damage *= 1.5
            
        # Coup critique (chance de 6.25%)
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5
            
        # Arrondi des dégâts
        damage = math.floor(damage)
        
        other.take_damage(damage)
        
    def take_damage(self, damage):
        
        self.current_hp -= damage
        
        # Les points de vie ne peuvent pas être inférieurs à 0
        if self.current_hp < 0:
            self.current_hp = 0
    
    def use_potion(self):
        
        # Vérification s'il reste des potions
        if self.num_potions > 0:
            
            # Ajout de 30 points de vie (mais pas au-delà du maximum)
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp
                
            # Diminution du nombre de potions restantes
            self.num_potions -= 1
        
    def set_sprite(self, side):
        
        # Chargement du sprite du Pokémon
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()
        
        # Mise à l'échelle de l'image
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pygame.transform.scale(self.image, (int(new_width), int(new_height)))
        
    def set_moves(self):
        
        self.moves = []
        
        # Parcours de tous les mouvements de l'API
        for i in range(len(self.json['moves'])):
            
            # Obtention du mouvement depuis différentes versions du jeu
            versions = self.json['moves'][i]['version_group_details']
            for j in range(len(versions)):
                
                version = versions[j]
                
                # Sélection des mouvements de la version Rouge-Bleu uniquement
                if version['version_group']['name'] != 'red-blue':
                    continue
                    
                # Sélection des mouvements appris par niveau (exclut les TM)
                learn_method = version['move_learn_method']['name']
                if learn_method != 'level-up':
                    continue
                    
                # Ajout du mouvement si le niveau du Pokémon est suffisant
                level_learned = version['level_learned_at']
                if self.level >= level_learned:
                    move = Move(self.json['moves'][i]['move']['url'])
                    
                    # Inclusion uniquement des mouvements d'attaque
                    if move.power is not None:
                        self.moves.append(move)
                        
        # Sélection aléatoire de jusqu'à 4 mouvements
        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)
        
    def draw(self, alpha=255):
        
        # Affichage du sprite avec une transparence
        sprite = self.image.copy()
        transparency = (255, 255, 255, alpha)
        sprite.fill(transparency, None, pygame.BLEND_RGBA_MULT)
        game.blit(sprite, (self.x, self.y))
        
    def draw_hp(self):
        
        # Affichage de la barre de vie
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, red, bar)
            
        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
            pygame.draw.rect(game, green, bar)
            
        # Affichage du texte "HP"
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
        text_rect = text.get_rect()
        text_rect.x = self.hp_x
        text_rect.y = self.hp_y + 30
        game.blit(text, text_rect)
        
    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        
# Création des Pokémon de départ
level = 30
bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
charmander = Pokemon('Charmander', level, 175, 150)
squirtle = Pokemon('Squirtle', level, 325, 150)
bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
charmander = Pokemon('Charmander', level, 175, 150)
squirtle = Pokemon('Squirtle', level, 325, 150)
pokemons = [bulbasaur, charmander, squirtle]

# Pokémon sélectionné par le joueur et son rival
player_pokemon = None
rival_pokemon = None

# Boucle principale du jeu
game_status = 'select pokemon'
while game_status != 'quit':
    
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 'quit'
            
        # Détection d'une pression sur une touche
        if event.type == KEYDOWN:
            
            # Rejouer
            if event.key == K_y:
                # Réinitialisation des Pokémon
                bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
                charmander = Pokemon('Charmander', level, 175, 150)
                squirtle = Pokemon('Squirtle', level, 325, 150)
                pokemons = [bulbasaur, charmander, squirtle]
                game_status = 'select pokemon'
                
            # Quitter
            elif event.key == K_n:
                game_status = 'quit'
            
        # Détection d'un clic de souris
        if event.type == MOUSEBUTTONDOWN:
            
            # Coordonnées du clic de souris
            mouse_click = event.pos
            
            # Pour sélectionner un Pokémon
            if game_status == 'select pokemon':
                
                # Vérification du Pokémon cliqué
                for i in range(len(pokemons)):
                    
                    if pokemons[i].get_rect().collidepoint(mouse_click):
                        
                        # Attribution des Pokémon du joueur et de son rival
                        player_pokemon = pokemons[i]
                        rival_pokemon = pokemons[(i + 1) % len(pokemons)]
                        
                        # Réduction du niveau du Pokémon rival pour faciliter le combat
                        rival_pokemon.level = int(rival_pokemon.level * .75)
                        
                        # Définition des coordonnées des barres de vie
                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 50
                        rival_pokemon.hp_y = 50
                        
                        game_status = 'prebattle'
            
            # Pour sélectionner Combat ou Utiliser une potion
            elif game_status == 'player turn':
                
                # Vérification si le bouton Combat a été cliqué
                if fight_button.collidepoint(mouse_click):
                    game_status = 'player move'
                    
                # Vérification si le bouton Potion a été cliqué
                if potion_button.collidepoint(mouse_click):
                    
                    # Forcer l'attaque s'il n'y a plus de potions
                    if player_pokemon.num_potions == 0:
                        display_message('No more potions left')
                        time.sleep(2)
                        game_status = 'player move'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} used potion')
                        time.sleep(2)
                        game_status = 'rival turn'
                        
            # Pour sélectionner un mouvement
            elif game_status == 'player move':
                
                # Vérification du mouvement cliqué
                for i in range(len(move_buttons)):
                    button = move_buttons[i]
                    
                    if button.collidepoint(mouse_click):
                        move = player_pokemon.moves[i]
                        player_pokemon.perform_attack(rival_pokemon, move)
                        
                        # Vérification si le Pokémon rival est évanoui
                        if rival_pokemon.current_hp == 0:
                            game_status = 'fainted'
                        else:
                            game_status = 'rival turn'
            
    # Écran de sélection des Pokémon
    if game_status == 'select pokemon':
        
        game.fill(white)
        
        # Affichage des Pokémon de départ
        bulbasaur.draw()
        charmander.draw()
        squirtle.draw()
        
        # Affichage de la bordure noire autour du Pokémon sur lequel la souris est positionnée
        mouse_cursor = pygame.mouse.get_pos()
        for pokemon in pokemons:
            
            if pokemon.get_rect().collidepoint(mouse_cursor):
                pygame.draw.rect(game, black, pokemon.get_rect(), 2)
        
        pygame.display.update()
        
    # Récupération des mouvements depuis l'API et repositionnement des Pokémon
    if game_status == 'prebattle':
        
        # Affichage du Pokémon sélectionné
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()
        
        player_pokemon.set_moves()
        rival_pokemon.set_moves()
        
        # Repositionnement des Pokémon
        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50
        
        # Redimensionnement des sprites
        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')
        
        game_status = 'start battle'
        
    # Animation de début de combat
    if game_status == 'start battle':
        
        # Le rival envoie son Pokémon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw(alpha)
            display_message(f'Rival sent out {rival_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
            
        # Pause de 1 seconde
        time.sleep(1)
        
        # Le joueur envoie son Pokémon
        alpha = 0
        while alpha < 255:
            
            game.fill(white)
            rival_pokemon.draw()
            player_pokemon.draw(alpha)
            display_message(f'Go {player_pokemon.name}!')
            alpha += .4
            
            pygame.display.update()
        
        # Affichage des barres de vie
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # Détermination de qui commence en premier
        if rival_pokemon.speed > player_pokemon.speed:
            game_status = 'rival turn'
        else:
            game_status = 'player turn'
            
        pygame.display.update()
        
        # Pause de 1 seconde
        time.sleep(1)
        
    # Affichage des boutons Combat et Utiliser potion
    if game_status == 'player turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # Création des boutons Combat et Utiliser potion
        fight_button = create_button(240, 140, 10, 350, 130, 412, 'Fight')
        potion_button = create_button(240, 140, 250, 350, 370, 412, f'Use Potion ({player_pokemon.num_potions})')

        # Affichage de la bordure noire
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        pygame.display.update()
        
    # Affichage des boutons de mouvement
    if game_status == 'player move':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # Création d'un bouton pour chaque mouvement
        move_buttons = []
        for i in range(len(player_pokemon.moves)):
            move = player_pokemon.moves[i]
            button_width = 240
            button_height = 70
            left = 10 + i % 2 * button_width
            top = 350 + i // 2 * button_height
            text_center_x = left + 120
            text_center_y = top + 35
            button = create_button(button_width, button_height, left, top, text_center_x, text_center_y, move.name.capitalize())
            move_buttons.append(button)
            
        # Affichage de la bordure noire
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
        
        pygame.display.update()
        
    # Le rival choisit un mouvement au hasard pour attaquer
    if game_status == 'rival turn':
        
        game.fill(white)
        player_pokemon.draw()
        rival_pokemon.draw()
        player_pokemon.draw_hp()
        rival_pokemon.draw_hp()
        
        # Effacer la boîte d'affichage et pause de 1 seconde
        display_message('')
        time.sleep(1)
        
        # Attaque aléatoire du rival
        move = random.choice(rival_pokemon.moves)
        rival_pokemon.perform_attack(player_pokemon, move)
        
        # Vérification si le joueur est évanoui
        if player_pokemon.current_hp == 0:
            game_status = 'fainted'
        else:
            game_status = 'player turn'
            
    # Affichage de l'écran de fin de partie si le joueur est évanoui
    if game_status == 'fainted':
        
        game.fill(white)
        display_message('Do you want to play again? (Y/N)')
        pygame.display.update()
        

    
  