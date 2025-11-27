import pygame
import sys
import random
      

def check_bullet_collisions(player_bullets, enemy_bullets):
    collisions = pygame.sprite.groupcollide(
        player_bullets, enemy_bullets, True, True
    )


# Размеры и отступы
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню и выбор уровня")


# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

# Шрифты
font_title = pygame.font.SysFont("Arial", 40)
font_button = pygame.font.SysFont("Arial", 28)
font_tutorial = pygame.font.SysFont("Arial", 18)
font_style = pygame.font.SysFont("Arial", 36)




# Состояния игры
MENU = "menu"
LEVEL_SELECTION = "level_selection"
PLAYING = "playing"
TUTORIAL = "tutorial"


current_state = MENU


# BONUS: Типы бонусов и активные эффекты
bonus_types = ['shield', 'fire_rate', 'life']
active_bonuses = {}  # Хранит активные бонусы и время их действия
bonus_spawn_timer = 0
BONUS_SPAWN_INTERVAL = 5000  # мс


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 28)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
# BONUS: Класс бонуса
class Bonus(pygame.sprite.Sprite):
    def __init__(self, bonus_type, x, y):
        super().__init__()
        self.type = bonus_type
        self.image = pygame.Surface((30, 30))
        if bonus_type == 'shield':
            self.image.fill((0, 0, 255))  # Синий
        elif bonus_type == 'fire_rate':
            self.image.fill((255, 165, 0))  # Оранжевый
        elif bonus_type == 'life':
            self.image.fill((255, 0, 0))  # Красный
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2


    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


def draw_multiline_text(text, font, color, surface, x, y, line_height=25):
    lines = text.strip().split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            text_surf = font.render(line.strip(), True, color)
            text_rect = text_surf.get_rect(left=x, top=y + i * line_height)
            surface.blit(text_surf, text_rect) 


class GameSprite(pygame.sprite.Sprite):
    def __init__(self, sprite1, sprite1_x, sprite1_y, sprite1_speed):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(sprite1), (65, 65))
        self.speed = sprite1_speed
        self.rect = self.image.get_rect()
        self.rect.x = sprite1_x
        self.rect.y = sprite1_y


    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
        
        # Визуальный эффект щита, если активен
        if 'shield' in active_bonuses and active_bonuses['shield'] > pygame.time.get_ticks():
            # Мигающий эффект: мерцание каждые 300 мс
            current_time = pygame.time.get_ticks()
            if (current_time // 200) % 2 == 0:  
                pygame.draw.circle(
                    window,
                    (100, 200, 255),  # голубой цвет
                    (self.rect.centerx, self.rect.centery),
                    self.rect.width // 2 + 10,  # радиус чуть больше ракеты
                    width=4  # толщина линии
                )


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.direction_x = 0
        self.direction_y = 0
        # BONUS: Добавляем свойство для количества жизней
        self.lives = 1


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 20:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < 700 - 80:
            self.rect.x += self.speed

class Enemy(GameSprite):
    def __init__(self, sprite1, sprite1_x, sprite1_y, sprite1_speed):
        super().__init__(sprite1, sprite1_x, sprite1_y, sprite1_speed)


    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > 500:
            self.rect.y = 0
            self.rect.x = random.randint(0, 700 - 65)
            lost = lost + 1

class Asteroid(GameSprite):
    def __init__(self, sprite1, sprite1_x, sprite1_y, sprite1_speed):
        super().__init__(sprite1, sprite1_x, sprite1_y, sprite1_speed)

    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > 500:
            self.rect.y = 0
            self.rect.x = random.randint(0, 700 - 65)
            lost = lost + 1

bottom = 150

class Bullet(GameSprite):
    def __init__(self, bullet_img, x, y, speed, vel_x, vel_y, owner):
        super().__init__(bullet_img, x, y, speed)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.owner = owner
        
        # Поворот в зависимости от владельца
        if self.owner == "player":
            # Пуля игрока: остриё вверх (стандартная ориентация)
            pass  # ничего не делаем — изображение уже правильно ориентировано
        elif self.owner == "boss":
            # Пуля босса: переворачиваем на 180°
            self.image = pygame.transform.rotate(self.image, 180)
    
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Удаление при выходе за экран
        if (self.rect.bottom < 0 or self.rect.top > 500 or 
            self.rect.right < 0 or self.rect.left > 700):
            self.kill()


def apply_bonus(bonus_type):
    global active_bonuses, rocket, win, lose
    
    if bonus_type == 'shield':
        active_bonuses['shield'] = pygame.time.get_ticks() + 5000  # 5 секунд
        
    elif bonus_type == 'fire_rate':
        active_bonuses['fire_rate'] = pygame.time.get_ticks() + 7000  # 7 секунд
        
    elif bonus_type == 'life':
        rocket.lives += 1




def run_level_1():
    global lost, count, game, finish, window, clock, font_style, monsters, asteroids, bullets, rocket, win, lose, bonuses, bonus_spawn_timer

    # Инициализация
    pygame.font.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # Создаём окно
    window = pygame.display.set_mode((700, 500))
    pygame.display.set_caption('Уровень 1')

    # Группы спрайтов
    monsters = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()

    # Фон и звуки
    background = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (700, 500))
    win = font_style.render('Победа!', True, (255, 215, 0))
    lose = font_style.render('ПОРАЖЕНИЕ', True, (255, 50, 50))
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.play(-1)  # зацикливание музыки
    shoot = pygame.mixer.Sound('fire.ogg')
    rumble_sound = pygame.mixer.Sound('Rumble_Effect.mp3')
    rumble_sound.set_volume(10)

    # Игрок — сбросим жизни
    rocket = Player('rocket.png', 350, 430, 3)
    rocket.lives = 1  # начальные жизни

    # Враги
    for i in range(2):
        monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
        monsters.add(monster)

    for i in range(1):
        asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
        asteroids.add(asteroid)

    # Счётчики
    lost = 0
    count = 0
    game = True
    finish = False
    last_shot_time = 0
    SHOOT_DELAY = 700  # задержка стрельбы
    bonus_spawn_timer = 0  # обнуляем таймер спавна бонусов

    # Главный цикл уровня
    while game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # Нажали Esc — выходим из уровня сразу в главное меню
                    pygame.mixer.music.stop()
                    return  # выходим из функции run_level_1, возвращаемся в главный цикл

                if e.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    shoot_delay = 400 if 'fire_rate' in active_bonuses and active_bonuses['fire_rate'] > current_time else 500

                    if current_time - last_shot_time >= shoot_delay:
                        bullet = Bullet('bullet.png', rocket.rect.centerx - 30, rocket.rect.top, 0, 0, -10, owner = 'player')
                        bullets.add(bullet)
                        shoot.play()
                        last_shot_time = current_time

        if finish:
            pygame.time.wait(1000)
            break

        # Обновление бонусов
        bonus_spawn_timer += clock.get_time()
        if bonus_spawn_timer >= BONUS_SPAWN_INTERVAL:
            bonus_spawn_timer = 0
            bonus_type = random.choice(bonus_types)
            bonus = Bonus(bonus_type, random.randint(50, WIDTH - 50), -30)
            bonuses.add(bonus)

        # Обновление спрайтов
        rocket.update()
        monsters.update()
        asteroids.update()
        bullets.update()
        bonuses.update()

        # Проверка столкновений с пулями
        killed_monsters = pygame.sprite.groupcollide(monsters, bullets, True, True)
        count += len(killed_monsters)

        killed_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        count += len(killed_asteroids)

        # Восстановление врагов
        for _ in killed_monsters:
            monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
            monsters.add(monster)

        for _ in killed_asteroids:
            asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
            asteroids.add(asteroid)

        # Сбор бонусов
        collected = pygame.sprite.spritecollideany(rocket, bonuses)
        if collected:
            collected.kill()
            apply_bonus(collected.type) 

        # Проверка столкновений с врагами
        if pygame.sprite.spritecollideany(rocket, monsters) or pygame.sprite.spritecollideany(rocket, asteroids):
            if 'shield' in active_bonuses and active_bonuses['shield'] > pygame.time.get_ticks():
                pass  # щит защищает
            else:
                rumble_sound.play()
                rocket.lives -= 1 
                hit = pygame.sprite.spritecollideany(rocket, monsters)
                if hit:
                    hit.kill()
                hit = pygame.sprite.spritecollideany(rocket, asteroids)
                if hit:
                    hit.kill()

        # Проверка условий окончания
        if rocket.lives <= 0:
            finish = True
            window.blit(lose, (250, 200))  # Добавьте обновление экрана
            pygame.display.update()  # Убедитесь, что это есть
            pygame.time.wait(1000)

        if lost >= 10:  # или 15 для уровня 2
            finish = True
            window.blit(lose, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        if count >= 15:  # или 25 для уровня 2
            finish = True
            window.blit(win, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        # Отрисовка
        window.blit(background, (0, 0))
        text_lost = font_style.render(f'Пропущено: {lost}', True, WHITE)
        text_count = font_style.render(f'Счёт: {count}', True, WHITE)
        text_lives = font_style.render(f'Жизни: {rocket.lives}', True, WHITE)
        window.blit(text_lost, (10, 50))
        window.blit(text_count, (10, 20))
        window.blit(text_lives, (10, 80))

        # Отрисовка спрайтов
        rocket.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        bonuses.draw(window)

        # Отображение активных бонусов
        font_small = pygame.font.SysFont("Arial", 20)
        y_offset = 110
        expired_bonuses = []
        for b_type, end_time in active_bonuses.items():
            if end_time > pygame.time.get_ticks():
                sec = (end_time - pygame.time.get_ticks()) // 1000
                text = font_small.render(f'{b_type}: {sec}s', True, (255, 255, 0))
                window.blit(text, (10, y_offset))
                y_offset += 25
            else:
                expired_bonuses.append(b_type)

        for b_type in expired_bonuses:
            del active_bonuses[b_type]

        pygame.display.update()
        clock.tick(60)

    # После окончания уровня (победа/поражение) — музыка останавливается
    pygame.mixer.music.stop()



def run_level_2():
    global lost, count, game, finish, window, clock, font_style, monsters, asteroids, bullets, rocket, win, lose, bonuses, bonus_spawn_timer

    # Инициализация
    pygame.font.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # Окно
    window = pygame.display.set_mode((700, 500))
    pygame.display.set_caption('Уровень 2')

    # Группы спрайтов
    monsters = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()

    # Фон и звуки
    background = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (700, 500))
    win = font_style.render('Победа!', True, (255, 215, 0))
    lose = font_style.render('ПОРАЖЕНИЕ', True, (255, 50, 50))
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.play(-1)
    shoot = pygame.mixer.Sound('fire.ogg')
    rumble_sound = pygame.mixer.Sound('Rumble_Effect.mp3')
    rumble_sound.set_volume(10)

    # Игрок
    rocket = Player('rocket.png', 350, 430, 3)
    rocket.lives = 1  # больше жизней на втором уровне

    # Враги — больше, чем на первом
    for i in range(3):
        monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
        monsters.add(monster)

    for i in range(2):
        asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
        asteroids.add(asteroid)

    # Счётчики
    lost = 0
    count = 0
    game = True
    finish = False
    last_shot_time = 0
    SHOOT_DELAY = 700
    bonus_spawn_timer = 0

    # Главный цикл уровня
    while game:
        # Обработка событий
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # Выход в меню
                    pygame.mixer.music.stop()
                    return  # выходим из функции, возвращаемся в главное меню

                if e.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    shoot_delay = 400 if 'fire_rate' in active_bonuses and active_bonuses['fire_rate'] > current_time else 500

                    if current_time - last_shot_time >= shoot_delay:
                        bullet = Bullet('bullet.png', rocket.rect.centerx - 30, rocket.rect.top, 0, 0, -10, owner = 'player')
                        bullets.add(bullet)
                        shoot.play()
                        last_shot_time = current_time

        if finish:
            pygame.time.wait(1000)
            break

        # Спавн бонусов
        bonus_spawn_timer += clock.get_time()
        if bonus_spawn_timer >= BONUS_SPAWN_INTERVAL:
            bonus_spawn_timer = 0
            bonus_type = random.choice(bonus_types)
            bonus = Bonus(bonus_type, random.randint(50, WIDTH - 50), -30)
            bonuses.add(bonus)

        # Обновление
        rocket.update()
        monsters.update()
        asteroids.update()
        bullets.update()
        bonuses.update()

        # Попадания
        killed_monsters = pygame.sprite.groupcollide(monsters, bullets, True, True)
        count += len(killed_monsters)

        killed_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        count += len(killed_asteroids)

        # Восстановление врагов
        for _ in killed_monsters:
            monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
            monsters.add(monster)

        for _ in killed_asteroids:
            asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40), 1)
            asteroids.add(asteroid)

        # Бонусы
        collected = pygame.sprite.spritecollideany(rocket, bonuses)
        if collected:
            collected.kill()
            apply_bonus(collected.type)

        # Столкновения
        if pygame.sprite.spritecollideany(rocket, monsters) or pygame.sprite.spritecollideany(rocket, asteroids):
            if 'shield' in active_bonuses and active_bonuses['shield'] > pygame.time.get_ticks():
                pass
            else:
                rumble_sound.play()
                rocket.lives -= 1
                hit = pygame.sprite.spritecollideany(rocket, monsters)
                if hit:
                    hit.kill()
                hit = pygame.sprite.spritecollideany(rocket, asteroids)
                if hit:
                    hit.kill()

        # Условия окончания
        if rocket.lives <= 0:
            finish = True
            window.blit(lose, (250, 200))  # Добавьте обновление экрана
            pygame.display.update()  # Убедитесь, что это есть
            pygame.time.wait(1000)

        if lost >= 15:  # или 15 для уровня 2
            finish = True
            window.blit(lose, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        if count >= 25:  # или 25 для уровня 2
            finish = True
            window.blit(win, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        # Отрисовка
        window.blit(background, (0, 0))
        text_lost = font_style.render(f'Пропущено: {lost}', True, WHITE)
        text_count = font_style.render(f'Счёт: {count}', True, WHITE)
        text_lives = font_style.render(f'Жизни: {rocket.lives}', True, WHITE)
        window.blit(text_lost, (10, 50))
        window.blit(text_count, (10, 20))
        window.blit(text_lives, (10, 80))

        rocket.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        bonuses.draw(window)

        # Отображение бонусов
        font_small = pygame.font.SysFont("Arial", 20)
        y_offset = 110
        expired_bonuses = []
        for b_type, end_time in active_bonuses.items():
            if end_time > pygame.time.get_ticks():
                sec = (end_time - pygame.time.get_ticks()) // 1000
                text = font_small.render(f'{b_type}: {sec}s', True, (255, 255, 0))
                window.blit(text, (10, y_offset))
                y_offset += 25
            else:
                expired_bonuses.append(b_type)

        for b_type in expired_bonuses:
            del active_bonuses[b_type]

        pygame.display.update()
        clock.tick(60)

    # Остановка музыки после завершения уровня
    pygame.mixer.music.stop()
   


def run_level_3():
    global lost, count, game, finish, window, clock, font_style, monsters, asteroids, bullets, rocket, win, lose, bonuses, bonus_spawn_timer

    # Инициализация
    pygame.font.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # Окно
    window = pygame.display.set_mode((700, 500))
    pygame.display.set_caption('Уровень 3')

    # Группы спрайтов
    monsters = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()  # пули босса
    bonuses = pygame.sprite.Group()

    # Фон и звуки
    background = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (700, 500))
    win = font_style.render('Победа!', True, (255, 215, 0))
    lose = font_style.render('ПОРАЖЕНИЕ', True, (255, 50, 50))
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.play(-1)
    shoot = pygame.mixer.Sound('fire.ogg')
    boss_shoot = pygame.mixer.Sound('fire.ogg')  
    rumble_sound = pygame.mixer.Sound('Rumble_Effect.mp3')
    rumble_sound.set_volume(10)

    # Игрок
    rocket = Player('rocket.png', 350, 430, 3)
    rocket.lives = 1  # максимум жизней

    

    # Обычные враги и астероиды
    for i in range(4):
        monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), random.randint(1,2))
        monsters.add(monster)

    for i in range(3):
        asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40),  random.randint(1,2))
        asteroids.add(asteroid)

    # Счётчики
    lost = 0
    count = 0
    game = True
    finish = False
    last_shot_time = 0
    boss_last_shot = 0
    bonus_spawn_timer = 0

    # Главный цикл уровня
    while game:
        # Обработка событий
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return  # выход в меню

                if e.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    shoot_delay = 400 if 'fire_rate' in active_bonuses and active_bonuses['fire_rate'] > current_time else 500

                    if current_time - last_shot_time >= shoot_delay:
                        bullet = Bullet('bullet.png', rocket.rect.centerx - 30, rocket.rect.top, 0, 0, -10, owner = 'player')
                        bullets.add(bullet)
                        shoot.play()
                        last_shot_time = current_time

        if finish:
            pygame.time.wait(1000)
            break

        # Спавн бонусов
        bonus_spawn_timer += clock.get_time()
        if bonus_spawn_timer >= BONUS_SPAWN_INTERVAL:
            bonus_spawn_timer = 0
            bonus_type = random.choice(bonus_types)
            bonus = Bonus(bonus_type, random.randint(50, WIDTH - 50), -30)
            bonuses.add(bonus)

        # Обновление
        rocket.update()
        monsters.update()
        asteroids.update()
        bullets.update()
        enemy_bullets.update()
        bonuses.update()

 


        # Попадания по врагам
        killed_monsters = pygame.sprite.groupcollide(monsters, bullets, False, True)
        for monster in killed_monsters:
            if hasattr(monster, 'is_boss'):
                monster.health -= 1
                if monster.health <= 0:
                    monster.kill()

            else:
                monster.kill()
                count += 1

        killed_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        count += len(killed_asteroids)

        for _ in killed_monsters:
            monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-100, -40), 2)
            monsters.add(monster)

        for _ in killed_asteroids:
            asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-100, -40), 2)
            asteroids.add(asteroid)

        # Бонусы
        collected = pygame.sprite.spritecollideany(rocket, bonuses)
        if collected:
            collected.kill()
            apply_bonus(collected.type)

        # Столкновения с врагами
        if pygame.sprite.spritecollideany(rocket, monsters) or pygame.sprite.spritecollideany(rocket, asteroids):
            if 'shield' in active_bonuses and active_bonuses['shield'] > pygame.time.get_ticks():
                pass
            else:
                rumble_sound.play()
                rocket.lives -= 1
                hit = pygame.sprite.spritecollideany(rocket, monsters)
                if hit:
                    hit.kill()
                hit = pygame.sprite.spritecollideany(rocket, asteroids)
                if hit:
                    hit.kill()

        # Пули врагов — тоже опасны
        if pygame.sprite.spritecollideany(rocket, enemy_bullets):
            if 'shield' in active_bonuses and active_bonuses['shield'] > pygame.time.get_ticks():
                pygame.sprite.spritecollide(rocket, enemy_bullets, True)
            else:
                rocket.lives -= 1
                pygame.sprite.spritecollide(rocket, enemy_bullets, True)

        # Условия окончания
        if rocket.lives <= 0:
            finish = True
            window.blit(lose, (250, 200)) 
            pygame.display.update()  
            pygame.time.wait(1000)

        if lost >= 20:  
            finish = True
            window.blit(lose, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        if count >= 40:  
            finish = True
            window.blit(win, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        # Отрисовка
        window.blit(background, (0, 0))
        text_lost = font_style.render(f'Пропущено: {lost}', True, WHITE)
        text_count = font_style.render(f'Счёт: {count}', True, WHITE)
        text_lives = font_style.render(f'Жизни: {rocket.lives}', True, WHITE)
        window.blit(text_lost, (10, 50))
        window.blit(text_count, (10, 20))
        window.blit(text_lives, (10, 80))
      

        # Отрисовка спрайтов
        rocket.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        bonuses.draw(window)

        # Отображение бонусов
        font_small = pygame.font.SysFont("Arial", 20)
        y_offset = 110
        expired_bonuses = []
        for b_type, end_time in active_bonuses.items():
            if end_time > pygame.time.get_ticks():
                sec = (end_time - pygame.time.get_ticks()) // 1000
                text = font_small.render(f'{b_type}: {sec}s', True, (255, 255, 0))
                window.blit(text, (10, y_offset))
                y_offset += 25
            else:
                expired_bonuses.append(b_type)

        for b_type in expired_bonuses:
            del active_bonuses[b_type]

        pygame.display.update()
        clock.tick(60)

    # Очистка и остановка
    pygame.mixer.music.stop()
    enemy_bullets.empty()


def run_level_4():
    global lost, count, game, finish, window, clock, font_style, monsters, asteroids, bullets, rocket, win, lose, bonuses, bonus_spawn_timer

    # Инициализация
    pygame.font.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()

    # Окно
    window = pygame.display.set_mode((700, 500))
    pygame.display.set_caption('Уровень 4 — ФИНАЛЬНЫЙ БОСС')

    # Группы спрайтов
    monsters = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()  # пули босса и элитных врагов
    bonuses = pygame.sprite.Group()

    # Фон и звуки
    background = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (700, 500))
    win = font_style.render('ПОБЕДА ГАЛАКТИКА СПАСЕНА!', True, (255, 215, 0))
    lose = font_style.render('ПОРАЖЕНИЕ', True, (255, 50, 50))
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.play(-1)
    shoot = pygame.mixer.Sound('fire.ogg')
    boss_shoot = pygame.mixer.Sound('fire.ogg')
    boss_shoot.set_volume(0.8)
    rumble_sound = pygame.mixer.Sound('Rumble_Effect.mp3')
    rumble_sound.set_volume(10)

    # Игрок
    rocket = Player('rocket.png', 350, 430, 3)
    rocket.lives = 2  # даём чуть больше шансов

    class Boss(GameSprite):
        def __init__(self):
            super().__init__('ufo.png', 275, 50, 1)
            self.image = pygame.transform.scale(self.image, (120, 80))
            self.health = 15
            self.max_health = 15
            self.is_boss = True
            self.shoot_timer = 0

        def update(self):
            self.rect.x += self.speed 
            if self.rect.right >= 700 or self.rect.left <= 0:
                self.speed *= -1

        def shoot(self):
            bullet = Bullet('bullet.png', self.rect.centerx, self.rect.bottom, 0, 0, 4, "boss")
            enemy_bullets.add(bullet)
    boss_shoot.play()
    boss = Boss()
    monsters.add(boss)

    # Элитные враги появляются чаще
    for i in range(5):
        monster = Enemy('ufo.png', random.randint(0, 700 - 65), random.randint(-200, -40), 2)
        monsters.add(monster)

    for i in range(4):
        asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), random.randint(-200, -40), 3)
        asteroids.add(asteroid)

    # Счётчики
    lost = 0
    count = 0
    game = True
    finish = False
    last_shot_time = 0
    boss_last_shot = 0
    BOSS_SHOOT_DELAY = 600  # стреляет чаще
    ELITE_SPAWN_TIMER = 0
    ELITE_SPAWN_INTERVAL = 8000  # появление элитного врага
    ASTEROID_SPAWN_TIMER = 0
    ASTEROID_SPAWN_INTERVAL = 4000  # больше астероидов
    bonus_spawn_timer = 0

    # Главный цикл уровня
    while game:
        dt = clock.get_time()  # delta time
        current_time = pygame.time.get_ticks()

        # Обработка событий
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    enemy_bullets.empty()
                    return

                if e.key == pygame.K_SPACE:
                    shoot_delay = 100 if 'fire_rate' in active_bonuses and active_bonuses['fire_rate'] > current_time else 500
                    if current_time - last_shot_time >= shoot_delay:
                        bullet = Bullet('bullet.png', rocket.rect.centerx - 30, rocket.rect.top, 0, 0, -10, "player")
                        bullets.add(bullet)
                        shoot.play()
                        last_shot_time = current_time

        if finish:
            pygame.time.wait(1500)
            break

        # Спавн бонусов
        bonus_spawn_timer += dt
        if bonus_spawn_timer >= BONUS_SPAWN_INTERVAL + random.randint(-1000, 1000):  # случайный интервал
            bonus_spawn_timer = 0
            bonus_type = random.choice(bonus_types)
            bonus = Bonus(bonus_type, random.randint(50, WIDTH - 50), -30)
            bonuses.add(bonus)

        # Спавн элитных врагов
        ELITE_SPAWN_TIMER += dt 
        if ELITE_SPAWN_TIMER >= ELITE_SPAWN_INTERVAL:
            ELITE_SPAWN_TIMER = 0
            elite = Enemy('ufo.png', random.randint(0, 700 - 65), -60, 3)
            monsters.add(elite)

        # Спавн дополнительных астероидов
        ASTEROID_SPAWN_TIMER += dt
        if ASTEROID_SPAWN_TIMER >= ASTEROID_SPAWN_INTERVAL:
            ASTEROID_SPAWN_TIMER = 0
            asteroid = Asteroid('asteroid.png', random.randint(0, 700 - 65), -60, 3)
            asteroids.add(asteroid)

        if current_time - boss_last_shot >= BOSS_SHOOT_DELAY and boss.alive():
            boss.shoot()
            boss_last_shot = current_time

        # Обновление
        rocket.update()
        monsters.update()
        asteroids.update()
        bullets.update()        # пули игрока
        enemy_bullets.update()  # пули босса
        bonuses.update()

        check_bullet_collisions(bullets, enemy_bullets)



        # Попадания
        killed_monsters = pygame.sprite.groupcollide(monsters, bullets, False, True)
        for monster in killed_monsters:
            if hasattr(monster, 'is_boss'):
                monster.health -= 1
                if monster.health <= 0:
                    monster.kill()
                    count += 20 
            else:
                monster.kill()
                count += 1

        killed_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        count += len(killed_asteroids)

        for _ in range(len(killed_monsters)):
            if random.random() < 0.5:
                monster = Enemy('ufo.png', random.randint(0, 700 - 65), -40, 2)
                monsters.add(monster)

        # Бонусы
        collected = pygame.sprite.spritecollideany(rocket, bonuses)
        if collected:
            collected.kill()
            apply_bonus(collected.type)

        # Столкновения с врагами
        if pygame.sprite.spritecollideany(rocket, monsters) or pygame.sprite.spritecollideany(rocket, asteroids):
            if 'shield' in active_bonuses and active_bonuses['shield'] > current_time:
                pass
            else:
                rumble_sound.play()
                rocket.lives -= 1
                hit = pygame.sprite.spritecollideany(rocket, monsters)
                if hit:
                    hit.kill()
                hit = pygame.sprite.spritecollideany(rocket, asteroids)
                if hit:
                    hit.kill()

        # Пули врагов — опасны
        if pygame.sprite.spritecollideany(rocket, enemy_bullets):
            if 'shield' in active_bonuses and active_bonuses['shield'] > current_time:
                pygame.sprite.spritecollide(rocket, enemy_bullets, True)
            else:
                rocket.lives -= 1
                pygame.sprite.spritecollide(rocket, enemy_bullets, True)

        # Условия окончания
        if rocket.lives <= 0:
            finish = True
            window.blit(lose, (250, 200))  # Добавьте обновление экрана
            pygame.display.update()  # Убедитесь, что это есть
            pygame.time.wait(1000)

        if lost >= 100:  # или 15 для уровня 2
            finish = True
            window.blit(lose, (250, 200))
            pygame.display.update()
            pygame.time.wait(1000)


        if count >= 60 and not boss.alive():  # победа только после убийства босса
            finish = True
            window.blit(win, (50, 200))
            pygame.display.update()
            pygame.time.wait(1000)

        # Отрисовка
        window.blit(background, (0, 0))

        # HUD
        text_lost = font_style.render(f'Пропущено: {lost}', True, WHITE)
        text_count = font_style.render(f'Счёт: {count}', True, WHITE)
        text_lives = font_style.render(f'Жизни: {rocket.lives}', True, WHITE)
        window.blit(text_lost, (10, 50))
        window.blit(text_count, (10, 20))
        window.blit(text_lives, (10, 80))

        # Индикатор здоровья босса
        if boss.alive():
            bar_width = 200
            health_ratio = boss.health / boss.max_health
            pygame.draw.rect(window, (100, 0, 0), (250, 10, bar_width, 15))
            pygame.draw.rect(window, (0, 255, 0), (250, 10, bar_width * health_ratio, 15))
            boss_text = font_style.render("ФИНАЛЬНЫЙ БОСС", True, RED)
            window.blit(boss_text, (250, 30))

        # Отрисовка спрайтов
        rocket.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        enemy_bullets.draw(window)
        bonuses.draw(window)

        # Отображение бонусов
        font_small = pygame.font.SysFont("Arial", 20)
        y_offset = 110
        expired_bonuses = []
        for b_type, end_time in active_bonuses.items():
            if end_time > current_time:
                sec = (end_time - current_time) // 1000
                text = font_small.render(f'{b_type}: {sec}s', True, (255, 255, 0))
                window.blit(text, (10, y_offset))
                y_offset += 25
            else:
                expired_bonuses.append(b_type)
        for b_type in expired_bonuses:
            del active_bonuses[b_type]

        pygame.display.update()
        clock.tick(60)

    # Очистка
    pygame.mixer.music.stop()
    enemy_bullets.empty()
    




while True:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state == PLAYING:
                    # Выход из игры в главное меню
                    current_state = MENU
                    # Очистка игровых объектов и бонусов
                    active_bonuses.clear()
                    if 'bullets' in globals() and bullets is not None:
                        bullets.empty()
                    if 'monsters' in globals() and monsters is not None:
                        monsters.empty()
                    if 'asteroids' in globals() and asteroids is not None:
                        asteroids.empty()
                    if 'bonuses' in globals() and bonuses is not None:
                        bonuses.empty()
                    if 'enemy_bullets' in globals() and enemy_bullets is not None:
                        enemy_bullets.empty()

                elif current_state == LEVEL_SELECTION:
                    # Из выбора уровня — в главное меню
                    current_state = MENU

                elif current_state == MENU:
                    # Из меню — выход из игры
                    pygame.quit()
                    sys.exit()

                elif current_state == TUTORIAL:
                    # Из обучения — в главное меню
                    current_state = MENU

    # Очистка экрана
    screen.fill(BLACK)

    # Логика отрисовки в зависимости от текущего состояния
    if current_state == MENU:
        # Заголовок меню
        title = font_title.render("Космическая битва", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Кнопка «Играть»
        play_button = pygame.Rect(WIDTH // 2 - 100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, play_button, border_radius=10)
        play_text = font_button.render("Играть", True, BLACK)
        screen.blit(play_text, (
            play_button.centerx - play_text.get_width() // 2,
            play_button.centery - play_text.get_height() // 2
        ))

        # Кнопка «Обучение»
        tutorial_button = pygame.Rect(WIDTH // 2 - 100, 320, 200, 50)
        pygame.draw.rect(screen, BLUE, tutorial_button, border_radius=10)
        tutorial_text = font_button.render("Обучение", True, BLACK)
        screen.blit(tutorial_text, (
            tutorial_button.centerx - tutorial_text.get_width() // 2,
            tutorial_button.centery - tutorial_text.get_height() // 2
        ))

        # Обработка кликов по кнопкам
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        if play_button.collidepoint(mouse_pos) and mouse_pressed[0]:
            current_state = LEVEL_SELECTION
            pygame.time.wait(200)

        if tutorial_button.collidepoint(mouse_pos) and mouse_pressed[0]:
            current_state = TUTORIAL
            pygame.time.wait(200)

    elif current_state == LEVEL_SELECTION:
        # Экран выбора уровня
        title = font_title.render("Выберите уровень", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        levels = [
            ("Уровень 1", 200),
            ("Уровень 2", 270),
            ("Уровень 3", 340),
            ("Уровень 4", 410)
        ]

        for level_text, y in levels:
            level_button = pygame.Rect(WIDTH // 2 - 100, y, 200, 50)
            pygame.draw.rect(screen, GRAY, level_button, border_radius=10)
            text_surf = font_button.render(level_text, True, BLACK)
            screen.blit(text_surf, (
                level_button.centerx - text_surf.get_width() // 2,
                level_button.centery - text_surf.get_height() // 2
            ))

        # Обработка кликов по уровням
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for level_text, y in levels:
            level_button = pygame.Rect(WIDTH // 2 - 100, y, 200, 50)
            if level_button.collidepoint(mouse_pos) and mouse_pressed[0]:
                if level_text == "Уровень 1":
                    run_level_1()
                elif level_text == "Уровень 2":
                    run_level_2()
                elif level_text == "Уровень 3":
                    run_level_3()
                elif level_text == "Уровень 4":
                    run_level_4()
                pygame.time.wait(200)
                break

    elif current_state == TUTORIAL:
        # Экран обучения
        tutorial_text = """
        Управление:
        - Стрелки влево/вправо — движение корабля
        - Пробел — выстрел

        Цель:
        - Уничтожать НЛО и астероиды
        - Набирать очки
        - Не пропускать объекты


        Бонусы:
        - Синий — щит (временная неуязвимость)
        - Оранжевый — ускорение стрельбы
        - Красный — дополнительная жизнь


        Нажмите ESC для возврата в меню
        """
        draw_multiline_text(tutorial_text, font_tutorial, WHITE, screen, 50, 100)

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
