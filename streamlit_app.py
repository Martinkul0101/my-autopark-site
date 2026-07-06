import pygame

# Ініціалізація
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()

# Параметри Годзілли
x, y = 50, 300
vel_y = 0
is_jumping = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Керування
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: x -= 5
    if keys[pygame.K_RIGHT]: x += 5
    
    # Стрибок
    if not is_jumping:
        if keys[pygame.K_SPACE]:
            vel_y = -15
            is_jumping = True
    else:
        y += vel_y
        vel_y += 1 # Гравітація
        if y >= 300:
            y = 300
            is_jumping = False

    # Малювання
    screen.fill((30, 30, 30)) # Фон
    pygame.draw.rect(screen, (0, 255, 0), (x, y, 50, 50)) # Годзілла-квадрат
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
