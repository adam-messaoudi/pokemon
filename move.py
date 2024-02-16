# Importation de tous les modules de pygame.locals
from pygame.locals import *

# Importation du module requests pour effectuer des requêtes HTTP
import requests

# Importation du module pygame
import pygame


# Définition de la largeur et de la hauteur de la fenêtre du jeu
game_width = 500
game_height = 500

# Création d'un tuple contenant les dimensions de la fenêtre
size = (game_width, game_height)

# Création de la fenêtre de jeu avec les dimensions spécifiées
game = pygame.display.set_mode(size)

# Définition du titre de la fenêtre de jeu
pygame.display.set_caption('Pokemon Battle')

# Définition des couleurs utilisées dans le jeu
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)


# Classe représentant un mouvement d'attaque
class Move():
    
    def __init__(self, url):
        
        # Appel de l'API des mouvements d'attaque
        req = requests.get(url)
        
        # Extraction des données JSON de la réponse de l'API
        self.json = req.json()
        
        # Récupération du nom, de la puissance et du type du mouvement
        self.name = self.json['name']
        self.power = self.json['power']
        self.type = self.json['type']['name']


# Fonction pour afficher un message à l'écran
def display_message(message):
    
    # Dessiner un rectangle blanc avec une bordure noire
    pygame.draw.rect(game, white, (10, 350, 480, 140))
    pygame.draw.rect(game, black, (10, 350, 480, 140), 3)
    
    # Afficher le message à l'intérieur du rectangle
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    text = font.render(message, True, black)
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 410
    game.blit(text, text_rect)
    
    # Mettre à jour l'affichage
    pygame.display.update()
    

# Fonction pour créer un bouton
def create_button(width, height, left, top, text_cx, text_cy, label):
    
    # Récupération de la position du curseur de la souris
    mouse_cursor = pygame.mouse.get_pos()
    
    # Création d'un rectangle représentant le bouton
    button = Rect(left, top, width, height)
    
    # Mettre en surbrillance le bouton si la souris est dessus
    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)
        
    # Ajout du libellé au bouton
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)
    
    return button
