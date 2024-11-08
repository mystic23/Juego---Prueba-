import pygame
import random
import math
import time
from pygame import mixer

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
screen = pygame.display.set_mode((1000, 600))

# Título e icono
pygame.display.set_caption("Space Invaders Mejorado")
icon = pygame.image.load("ufo.png")
pygame.display.set_icon(icon)

# Música de fondo
mixer.music.load("background.wav")
mixer.music.play(-1)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Variables Globales
score_value = 0
lives = 3
player_name = ""
start_time = time.time()  # Tiempo de inicio del juego

# Función para mostrar texto en pantalla
def show_text(text, x, y, font_size=32, color=WHITE):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))

# Clase para el jugador
class Player:
    def __init__(self):
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.image, (64, 64))  # Escalar imagen
        self.x = 370
        self.y = 480
        self.x_change = 0

    def move(self):
        self.x += self.x_change
        if self.x <= 0:
            self.x = 0
        elif self.x >= 736:
            self.x = 736

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Clase para los enemigos normales
class Enemy:
    def __init__(self, speed=2):
        self.image = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.x = random.randint(0, 735)
        self.y = random.randint(50, 150)
        self.x_change = speed
        self.y_change = 40
        self.speed = speed

    def move(self):
        self.x += self.x_change
        if self.x <= 0:
            self.x_change = self.speed
            self.y += self.y_change
        elif self.x >= 736:
            self.x_change = -self.speed
            self.y += self.y_change

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def is_off_screen(self):
        return self.y > 440

# Clase para la bala
class Bullet:
    def __init__(self):
        self.image = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale(self.image, (32, 32))  # Escalar imagen
        self.x = 0
        self.y = 480
        self.y_change = 10
        self.state = "ready"

    def fire(self, x):
        if self.state == "ready":
            self.x = x
            self.state = "fire"

    def move(self):
        if self.state == "fire":
            self.y -= self.y_change
            if self.y <= 0:
                self.y = 480
                self.state = "ready"

    def draw(self):
        if self.state == "fire":
            screen.blit(self.image, (self.x + 16, self.y + 10))

# Detección de colisión
def is_collision(enemy, bullet):
    distance = math.sqrt(math.pow(enemy.x - bullet.x, 2) + math.pow(enemy.y - bullet.y, 2))
    return distance < 27

# Menú de entrada de nombre del jugador
def get_player_name():
    global player_name
    player_name = ""
    waiting = True
    while waiting:
        screen.fill(BLACK)
        show_text("ENTER YOUR NAME", 200, 250, 64)
        show_text(player_name, 300, 350, 32)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += event.unicode

# Menú de inicio
def show_start_menu():
    screen.fill(BLACK)
    show_text("SPACE INVADERS", 220, 250, 64)
    show_text("Press ENTER to Start", 250, 350, 32)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Menú de fin de juego
def show_game_over():
    screen.fill(BLACK)
    show_text("GAME OVER", 250, 250, 64)
    show_text(f"Score: {score_value}", 300, 350, 32)
    show_text(f"Player: {player_name}", 300, 400, 32)
    show_text("Press ENTER to Restart", 200, 450, 32)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    main()

# Función principal del juego
def main():
    global score_value, lives
    player = Player()
    bullet = Bullet()
    enemies = [Enemy(speed=1) for _ in range(3)]  # Enemigos normales con velocidad reducida
    fast_enemy_spawned = False
    score_value = 0
    lives = 3

    running = True
    while running:
        screen.fill(BLACK)

        # Eventos del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x_change = -3  # Velocidad del jugador reducida
                if event.key == pygame.K_RIGHT:
                    player.x_change = 3  # Velocidad del jugador reducida
                if event.key == pygame.K_SPACE:
                    if bullet.state == "ready":
                        bullet.fire(player.x)
                        bullet_sound = mixer.Sound("laser.wav")
                        bullet_sound.play()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.x_change = 0

        # Lógica del juego
        player.move()
        bullet.move()

        # Spawn de enemigo rápido después de 30 segundos
        if not fast_enemy_spawned and time.time() - start_time > 30:
            enemies.append(Enemy(speed=6))  # Enemigo rápido con velocidad aumentada
            fast_enemy_spawned = True

        for enemy in enemies:
            enemy.move()
            if enemy.is_off_screen():
                lives -= 1  # Reducir vida si el enemigo llega al fondo
                enemy.y = random.randint(50, 150)  # Reiniciar posición del enemigo
                enemy.x = random.randint(0, 735)
                if lives == 0:
                    show_game_over()
                    return

            if is_collision(enemy, bullet):
                explosion_sound = mixer.Sound("explosion.wav")
                explosion_sound.play()
                bullet.y = 480
                bullet.state = "ready"
                score_value += 1
                enemy.x = random.randint(0, 735)
                enemy.y = random.randint(50, 150)

            enemy.draw()

        # Dibujar los elementos en pantalla
        player.draw()
        bullet.draw()
        show_text(f"Score: {score_value}", 10, 10)
        show_text(f"Lives: {lives}", 700, 10)
        pygame.display.update()

# Flujo del juego
get_player_name()
show_start_menu()
main()
pygame.quit()
