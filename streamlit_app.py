import pygame
import os

pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Завантаження картинки (якщо вона є в папці)
if os.path.exists("godzilla.png"):
    godzilla_img = pygame.image.load("godzilla.png")
    godzilla_img = pygame.transform.scale(godzilla_img, (60, 60))
else:
    godzilla_img = None

# Параметри гравця
player_x, player_y = 50, 300
vel_y = 0
is_jumping = False

# Параметри перешкоди (будинку)
obs_x, obs_y = 700, 300
obs_speed = 7

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Стрибок
    keys = pygame.key.get_pressed()
    if not is_jumping:
        if keys[pygame.K_SPACE]:
            vel_y = -18
            is_jumping = True
    else:
        player_y += vel_y
        vel_y += 1
        if player_y >= 300:
            player_y = 300
            is_jumping = False

    # Рух перешкоди
    obs_x -= obs_speed
    if obs_x < -50:
        obs_x = 800

    # Перевірка програшу (зіткнення)
    if player_x + 50 > obs_x and player_y + 50 > obs_y:
        print("GAME OVER!")
        obs_x = 800 # Рестарт позиції

    # Рендеринг
    screen.fill((135, 206, 235))
    pygame.draw.rect(screen, (34, 139, 34), (0, 350, 800, 50)) # Земля
    
    # Малюємо Годзіллу або квадрат
    if godzilla_img:
        screen.blit(godzilla_img, (player_x, player_y))
    else:
        pygame.draw.rect(screen, (0, 100, 0), (player_x, player_y, 50, 50))
    
    # Малюємо будинок
    pygame.draw.rect(screen, (100, 100, 100), (obs_x, obs_y, 50,
