# Juego---Prueba-
## María Isabel Solá Valle
# Battle of Time

Este juego está inspirado en el clásico **Space Invaders**, pero con un diseño temático basado en la serie de ciencia ficción **Doctor Who**. Los jugadores asumen el papel de la **Tardis**, esta es una maquina que puede viajar por todo el universo y viajar a través del tiempo, enfrentándose a oleadas de enemigos y poderosos jefes, recordando los desafíos que la **Tardis** enfrenta al salvar el universo. En cada nivel, deben acumular puntos y sobrevivir a amenazas. Además, el juego incluye mecánicas como control de vidas, puntuación progresiva, niveles de dificultad creciente y un sistema de pausa para permitir a los jugadores tomar un respiro antes de enfrentar los siguientes niveles.
## Funcionalidad del Código

### 1. Importación de Módulos

```python
import pygame
import random
import math
import time
import os
import sys
from pygame import mixer
```
Estos módulos permiten el desarrollo de la funcionalidad principal del juego:

### 2. Variables Globales
Las variables globales permiten gestionar la puntuación, vidas, nombre del jugador, nivel actual, estado de pausa, y otros aspectos generales del juego.

```
score_value = 0
lives = 3
player_name = ""
start_time = time.time()
level = 1
boss_defeated = 0
game_paused = False
```
### 3. Funciones Utiles 

- ```show_text:```
Muestra texto en la pantalla en una posición específica.

```
def show_text(text, x, y, font_size=32, color=WHITE):
    font = pygame.font.Font("freesansbold.ttf", font_size)
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))
```
- ```is_mouse_over:```
Detecta si el mouse está sobre una región específica para interactuar con botones.

- ```save_score:```
Guarda el nombre, puntaje y tiempo de juego del jugador en un archivo de texto.

- ```load_scores:``` Carga y muestra los puntajes guardados, ordenándolos por puntaje y tiempo.

### 4. Clases Principales del Juego
- ```Clase Player:``` Representa al jugador y controla su movimiento y representación en pantalla.

    - ```move():``` Mueve al jugador a izquierda y derecha.
    - ```draw():``` Dibuja la imagen del jugador en pantalla.
```
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
```



- ```Clase Enemy```
Controla los enemigos normales que el jugador debe derrotar.

    - ```move():``` Define el movimiento de los enemigos y la lógica de cambio de dirección.
    - ```draw():``` Dibuja cada enemigo en pantalla.
    - ```is_off_screen():``` Detecta si el enemigo ha salido de la pantalla.

```
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
```

- ```Clase Bullet```
Controla las balas disparadas por el jugador.

    - ```fire(x):``` Activa una bala para disparar desde la posición x.
    - ```move():``` Mueve la bala hacia arriba de la pantalla.
    - ```draw():``` Dibuja la bala mientras está activa.
```
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

```

- ```Clase LifeBar```
Representa y dibuja la barra de vida en la pantalla.
```
class LifeBar:
    def __init__(self):
        self.image = pygame.image.load("life.png")
        self.image = pygame.transform.scale(self.image, (32, 32))

    def draw(self, lives):
        for i in range(lives):
            screen.blit(self.image, (700 + i * 35, 10))

```

- ```Clase BossBullet```
Controla las balas disparadas por el jefe, con movimiento y representación gráfica.
```
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
```


- ```Clase Boss```
Controla al jefe en el juego, con mayor dificultad que los enemigos normales.

    - ```move():``` Define el movimiento del jefe.
    - ```shoot():``` Permite que el jefe dispare en intervalos aleatorios.
    -```draw():``` Dibuja la imagen y la barra de vida del jefe.
    - ```is_hit(bullet):``` Detecta si el jefe ha sido golpeado por una bala del jugador.
```
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
```

### 5. Detección de Colisiones
```is_collision: ```
Detecta si hay una colisión entre dos objetos, como una bala y un enemigo.
```
def is_collision(x1, y1, x2, y2, distance_threshold):
    distance = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    return distance < distance_threshold
```

### 6 Pantallas de Mensajes
- ```show_level_up_screen```
Muestra una pantalla temporal indicando que el jugador ha subido de nivel.

- ```show_pause_menu```
Muestra el menú de pausa con opciones para reanudar el juego o salir al menú principal.

- ```show_game_over```
Muestra la pantalla de "Game Over" y permite al jugador reiniciar el juego presionando Enter.

- ```show_start_menu```
Muestra el menú principal donde el jugador puede elegir iniciar el juego, ver los puntajes, o salir.

- ```show_scores_menu```
Muestra los puntajes altos guardados en el archivo.

### 7 Entrada de Nombre del Jugador
- ``` get_player_name```
Permite al jugador ingresar su nombre o seleccionar la opción de "Omitir" para asignar un nombre automático.

### 8 Función Principal del Juego
- ``` main```
Define la lógica central del juego, controlando:

    - Movimientos del jugador y enemigos.
    - Colisiones y actualizaciones de puntaje.
    - Comportamiento del jefe.
    - Pérdida de vidas y finalización del juego si las vidas llegan a cero.
### 9 Flujo del Juego
La secuencia de ejecución:
- ```get_player_name():``` Solicita el nombre del jugador.
- ```show_start_menu():``` Muestra el menú principal.
- ```main():``` Inicia la lógica central del juego.
Al perder todas las vidas, se llama a ```show_game_over()``` para mostrar la pantalla final.

## Cómo Ejecutar el Juego
**Instala Pygame ejecutando:**
```
pip install pygame
```
**Corre el juego ejecutando el archivo principal:**
```
python main.py
```