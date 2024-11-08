import pygame
import random
import math
import time
import os
import sys
from pygame import mixer

pygame.init()
screen = pygame.display.set_mode((1000, 600))

pygame.display.set_caption("Battle of Time ")
icon = pygame.image.load("ufo.png")
pygame.display.set_icon(icon)
 
mixer.music.load("background.wav")
mixer.music.play(-1)

background = pygame.image.load("background.png")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Variables Globales
score_value = 0
lives = 3
player_name = ""
start_time = time.time()  # Tiempo de inicio del juego
level = 1
boss_defeated = 0
game_paused = False  # Variable para controlar el estado de pausa

# Función para mostrar texto en pantalla
def show_text(text, x, y, font_size=32, color=WHITE):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))


# Función auxiliar para detectar si el mouse hace clic en un botón
def is_mouse_over(x, y, width, height):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return x <= mouse_x <= x + width and y <= mouse_y <= y + height

# Función para guardar el score al finalizar el juego
def save_score(name, score, time_taken):
    with open("scores.txt", "a") as file:
        file.write(f"{name},{score},{time_taken}\n")

# Función para cargar y mostrar los scores guardados
def load_scores():
    scores = []
    if os.path.exists("scores.txt"):
        with open("scores.txt", "r") as file:
            for line in file:
                name, score, time_taken = line.strip().split(",")
                scores.append((name, int(score), float(time_taken)))
    return sorted(scores, key=lambda x: (-x[1], x[2]))  # Ordenar por puntaje y tiempo

# Clase para el jugador
class Player:
    def __init__(self):
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.x = 370
        self.y = 480
        self.x_change = 0

    def move(self):
        self.x += self.x_change
        if self.x <= 0:
            self.x = 0
        elif self.x >= 936:
            self.x = 936

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Clase para los enemigos normales
class Enemy:
    def __init__(self, speed=2):
        self.image = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.x = random.randint(0, 935)
        self.y = random.randint(50, 150)
        self.x_change = speed
        self.y_change = 40
        self.speed = speed

    def move(self):
        self.x += self.x_change
        if self.x <= 0:
            self.x_change = self.speed
            self.y += self.y_change
        elif self.x >= 936:
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
        self.image = pygame.transform.scale(self.image, (32, 32))
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

# Clase para la barra de vida
class LifeBar:
    def __init__(self):
        self.image = pygame.image.load("life.png")
        self.image = pygame.transform.scale(self.image, (32, 32))

    def draw(self, lives):
        for i in range(lives):
            screen.blit(self.image, (700 + i * 35, 10))

# Clase para los ataques del Boss
class BossBullet:
    def __init__(self, x, y):
        self.image = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.x = x
        self.y = y
        self.y_change = 5

    def move(self):
        self.y += self.y_change

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Boss:
    def __init__(self, level, speed=1):
        boss_images = ["boss1.png", "boss2.png", "boss3.png"]  
        self.image = pygame.image.load(boss_images[level - 1])
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.x = 300
        self.y = 50
        self.x_change = speed
        self.health = 8 + (level - 1) * 7 
        self.max_health = self.health
        self.bullets = []
        self.last_shot_time = time.time()

    def move(self):
        self.x += self.x_change
        if self.x <= 0 or self.x >= 880:
            self.x_change *= -1

    def shoot(self):
        if time.time() - self.last_shot_time > random.uniform(1.0, 3.0):
            self.bullets.append(BossBullet(self.x + 60, self.y + 60))
            self.last_shot_time = time.time()

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
        pygame.draw.rect(screen, RED, (self.x, self.y - 20, 120 * (self.health / self.max_health), 10))

    def is_hit(self, bullet):
        distance = math.sqrt(math.pow(self.x - bullet.x, 2) + math.pow(self.y - bullet.y, 2))
        return distance < 50

def is_collision(x1, y1, x2, y2, distance_threshold):
    distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return distance < distance_threshold

def show_level_up_screen(level):
    screen.fill(BLACK)
    show_text(f"You are on level -> {level} ", 200, 250, 64, WHITE)
    show_text("Get Ready...", 220, 320, 32, WHITE)
    pygame.display.update()
    time.sleep(4)  

def show_pause_menu():
    global game_paused
    while game_paused:
        screen.blit(background, (0, 0))
        show_text("PAUSE", 400, 200, 64)
        show_text("[Here you need to select numbers 1 or 2 to access]", 250, 270, 20)
        show_text("[1] Return", 370, 340, 32)
        show_text("[2] Exit to Main Menu", 370, 390, 32)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Reanudar
                    game_paused = False
                elif event.key == pygame.K_2:  # Salir al menú principal
                    main_menu()

def main_menu():
    global score_value, lives, level, boss_defeated, game_paused
    score_value = 0
    lives = 3
    level = 1
    boss_defeated = 0
    game_paused = False
    show_start_menu()
    main()

def show_game_over():
    global start_time
    # screen.fill(BLACK)
    screen.blit(background, (0, 0))
    end_time = time.time()
    time_taken = end_time - start_time
    save_score(player_name, score_value, time_taken)

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

def show_start_menu():
    screen.blit(background, (0, 0))
    selected_option = 0
    options = ["> Start Game", "> View Scores", "> Exit"]
    font_size = 48

    while True:
        screen.blit(background, (0, 0))
        show_text("---Battle of Time---", 220, 150, 64)
        show_text("[Use the arrow keys to move and press Enter to select]", 240, 225, 20)
        
        for i, option in enumerate(options):
            color = WHITE if i == selected_option else (100, 100, 100)
            show_text(option, 300, 300 + i * font_size, font_size, color)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Iniciar Juego
                        return
                    elif selected_option == 1:  # Ver Scores
                        show_scores_menu()
                    elif selected_option == 2:  # Salir
                        pygame.quit()
                        quit()
                        
def show_scores_menu():
    scores = load_scores()
    screen.blit(background, (0, 0))
    show_text("High Scores", 250, 50, 64)

    for i, (name, score, time_taken) in enumerate(scores[:5]):  # Mostrar solo los primeros 5
        show_text(f"{i+1}. {name} - Score: {score} - Time: {round(time_taken, 2)}s", 100, 150 + i * 40, 32)

    show_text("Press ENTER to return", 200, 500, 32)
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

player_counter = 1  # Inicia en 1 y se incrementa por cada jugador que omite el nombre

def get_player_name():
    global player_name, player_counter
    player_name = ""
    waiting = True
    skip_button_rect = pygame.Rect(400, 450, 220, 50)  # Posición y tamaño del botón "Omitir"

    while waiting:
        screen.blit(background, (0, 0))
        show_text("Welcome to Battle of Time", 100, 100, 64)
        show_text("Write your name", 250, 200, 64)
        show_text("(Just Write...)", 400, 300, 32)
        show_text(player_name, 400, 350, 40)
        
        # Dibujar botón "Omitir"
        pygame.draw.rect(screen, GRAY, skip_button_rect)
        show_text("SKIP [Enter]", 410, 460, 32, WHITE)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name == "":
                        # Asignar nombre automático si el jugador no ingresó un nombre
                        player_name = f"Player {player_counter}"
                        player_counter += 1  # Incrementar el contador para el próximo jugador automático
                    waiting = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and is_mouse_over(400, 450, 200, 50):  # Verifica si el botón "Omitir" fue presionado
                    # Asignar nombre automático si el jugador omite
                    player_name = f"Player {player_counter}"
                    player_counter += 1  # Incrementar el contador para el próximo jugador automático
                    waiting = False

# Función principal del juego
def main():
    global score_value, lives, start_time, level, boss_defeated, game_paused
    start_time = time.time()
    player = Player()
    bullet = Bullet()
    enemies = [Enemy(speed=3) for _ in range(5)]
    life_bar = LifeBar()
    score_value = 0
    lives = 4
    boss = None
    pause_button_rect = pygame.Rect(880, 10, 110, 40)  # Rectángulo para el botón de pausa
    
    running = True
    while running:
        # screen.fill(BLACK)
        screen.blit(background, (0, 0))
        # Eventos del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x_change = -3
                if event.key == pygame.K_RIGHT:
                    player.x_change = 3
                if event.key == pygame.K_SPACE:
                    if bullet.state == "ready":
                        bullet.fire(player.x)
                        bullet_sound = mixer.Sound("laser.wav")
                        bullet_sound.play()
                if event.key == pygame.K_p:  # Tecla P para pausar
                    game_paused = True
                    show_pause_menu()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.x_change = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and is_mouse_over(*pause_button_rect):  # Botón de pausa
                    game_paused = True
                    show_pause_menu()

        # Lógica del jugador y la bala
        player.move()
        bullet.move()

        # Enemigos normales
        for enemy in enemies:
            enemy.move()
            if enemy.is_off_screen():
                lives -= 1
                enemy.y = random.randint(50, 150)
                enemy.x = random.randint(0, 935)
                if lives == 0:
                    show_game_over()
                    return
            if is_collision(enemy.x, enemy.y, bullet.x, bullet.y, 27):
                explosion_sound = mixer.Sound("explosion.wav")
                explosion_sound.play()
                bullet.y = 480
                bullet.state = "ready"
                score_value += 1
                enemy.x = random.randint(0, 935)
                enemy.y = random.randint(50, 150)
            enemy.draw()

        # Boss de nivel
        if boss is None and score_value >= level * 10:
            show_level_up_screen(level)  # Mostrar la pantalla de subida de nivel
            boss = Boss(level, speed=3 + level)

        if boss:
            boss.move()
            boss.shoot()
            boss.draw()
            for boss_bullet in boss.bullets:
                boss_bullet.move()
                boss_bullet.draw()
                if is_collision(boss_bullet.x, boss_bullet.y, player.x, player.y, 25):
                    lives -= 1
                    boss.bullets.remove(boss_bullet)
                    if lives == 0:
                        show_game_over()
                        return
            if boss.is_hit(bullet):
                boss.health -= 1
                bullet.state = "ready"
                bullet.y = 480
                if boss.health <= 0:
                    score_value += 5
                    boss = None
                    level += 1
                    boss_defeated += 1
                    if boss_defeated >= 3:
                        show_text("Congratulations! You have won the game!", 150, 250, 64)
                        pygame.display.update()
                        time.sleep(4)
                        show_game_over()
                        return

        # Dibujar los elementos en pantalla
        player.draw()
        bullet.draw()
        life_bar.draw(lives)
        elapsed_time = time.time() - start_time
        show_text(f"Score: {score_value}", 10, 10)
        # show_text(f"Health: {lives}", 550, 10)
        show_text(f"Health:", 550, 10)
        show_text(f"Time: {round(elapsed_time, 2)}s", 10, 50)
        show_text("Move left or right with the arrow keys and shoot with Space", 240, 550, 20)

        # Dibujar botón de pausa
        pygame.draw.rect(screen, GRAY, pause_button_rect)
        show_text("Pause [P]", 890, 15, 20, WHITE)

        pygame.display.update()


get_player_name()
show_start_menu()
main()
pygame.quit()
