import gettext
import math
import random
import sys
from time import sleep

import pygame
from pygame.locals import *

WINDOW_width = 800
WINDOW_height = 600

BLACK = (0.0,0)
WHILE = (200, 200, 200)
YELLOW = (250, 250, 20)
BLUE = (20, 20, 250)

pygame.init()
screen = pygame.display.set_mode((WINDOW_width, WINDOW_height))
pygame.display.set_caption('Pyspaceship : 암석 피하기 게임')
pygame.display.set_icon(pygame.image.load('image/warp.png'))
fps_clock = pygame.time.Clock()
FPS = 60
score = 0

default_font = pygame.font.Font('NanumGothic.ttf', 28)
background_img = pygame.image.load('image/background.jpg')
explosion_sound = pygame.mixer.Sound('bgm/explosion.wav')
warp_sound = pygame.mixer.Sound('bgm/warp.wav')
pygame.mixer.music.load('bgm/Inner_Sanctum.wav')
warp_Interaction = pygame.mixer.Sound('bgm/warp1up.wav')
warp_gain = pygame.mixer.Sound('bgm/워프 효과음.wav')
class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super(Spaceship, self).__init__()
        self.image = pygame.image.load('image/spaceship.png')
        self.rect = self.image.get_rect()
        self.centerx = self.rect.centerx
        self.centery = self.rect.centery

    # 포지션
    def set_pos(self, x, y):
        self.rect.x = x - self.centerx
        self.rect.y = y - self.centery

    def collide(self, sprites):
        for sprite in sprites:
            if pygame.sprite.collide_rect(self, sprite):
                return sprite

class Rock(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, hspeed, vspeed):
        super(Rock, self).__init__()
        rocks = ('rock/rock01.png','rock/rock02.png','rock/rock03.png','rock/rock04.png','rock/rock05.png',\
                 'rock/rock06.png','rock/rock07.png','rock/rock08.png','rock/rock09.png','rock/rock10.png',\
                 'rock/rock11.png','rock/rock12.png','rock/rock13.png','rock/rock14.png','rock/rock15.png',\
                 'rock/rock16.png','rock/rock17.png','rock/rock18.png','rock/rock19.png','rock/rock20.png',\
                 'rock/rock21.png','rock/rock22.png','rock/rock23.png','rock/rock24.png','rock/rock25.png',\
                 'rock/rock26.png','rock/rock27.png','rock/rock28.png','rock/rock29.png','rock/rock30.png',\
                 'rock/rock.31.png')
        self.image = pygame.image.load(random.choice(rocks))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.hspeed = hspeed
        self.vspeed = vspeed

        self.set_direction()

    # 암석의 각도 변환
    def set_direction(self):
        if self.hspeed > 0:
            self.image = pygame.transform.rotate(self.image, 270)
        elif self.hspeed < 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.vspeed > 0:
            self.image = pygame.transform.rotate(self.image, 180)

    def update(self):
        self.rect.x += self.hspeed
        self.rect.y += self.vspeed
        if self.collide():
            self.kill()

    # 우주선과 암석 충돌
    def collide(self):
        if self.rect.x < 0 - self.rect.height or self.rect.x > WINDOW_width:
            return True
        elif self.rect.y < 0 - self.rect.height or self.rect.y > WINDOW_height:
            return True

def random_rock(speed):
    random_direction = random.randint(1,4)
    if random_direction == 1:
        return Rock(random.randint(0, WINDOW_width), 0 , 0, speed) #왼쪽->오른쪽
    elif random_direction == 2:
        return Rock(WINDOW_width, random.randint(0, WINDOW_height), -speed, 0) # 위 -> 아래
    elif random_direction == 3:
        return Rock(random.randint(0, WINDOW_width), WINDOW_height, 0, -speed) # 아래 -> 위
    elif random_direction == 4:
        return Rock(0, random.randint(0, WINDOW_height), speed, 0) # 오른쪽 -> 왼쪽

# 아이템
class Warp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Warp, self).__init__()
        self.image = pygame.image.load('image/warp.png')
        self.rect = self.image.get_rect()
        self.rect.x = x - self.rect.centerx
        self.rect.y = y - self.rect.centery

def draw_repeating_background(background_img):
    background_rect = background_img.get_rect()
    for i in range(int(math.ceil(WINDOW_width / background_rect.width))):
        for j in range(int(math.ceil(WINDOW_height / background_rect.height))):
            screen.blit(background_img, Rect(i * background_rect.width,
                                             j * background_rect.height,
                                             background_rect.width,
                                             background_rect.height))

def draw_text(text, font, surface, x, y ,main_color):
    text_obj = font.render(text, True, main_color)
    text_rect = text_obj.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surface.blit(text_obj, text_rect)

# 엔진
def game_loop():
    global score

    pygame.mixer.music.play(-1)
    pygame.mouse.set_visible(False)

    spaceship = Spaceship()
    spaceship.set_pos(*pygame.mouse.get_pos())
    rocks = pygame.sprite.Group()
    warps = pygame.sprite.Group()

    min_rock_speed = 1
    max_rock_speed = 1
    occur_of_rocks = 1
    occur_prob = 15
    score = 0
    warp_count = 1
    paused = False # p키를 누르면 게임 일시 중지

    while True:
        pygame.display.update()
        fps_clock.tick(FPS) # FPS = 60
        
        if paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        pygame.mouse.set_visible(False)
                if event.type == QUIT:
                    return 'quit'

        else:
            draw_repeating_background(background_img)

            # 난이도 설정
            occur_of_rocks = 1 + int(score/ 500)
            min_of_rocks = 1 + int(score/ 400)
            max_of_rocks = 1 + int(score/ 300)

            if random.randint(1, occur_prob) == 1: # 1/15 확률
                for i in range(occur_of_rocks):
                    rocks.add(random_rock(random.randint(min_rock_speed, max_rock_speed)))
                    score += 1

                if random.randint(1, occur_prob * 10) == 1: # 1/175 확률
                    warp = Warp(random.randint(30, WINDOW_width - 30),
                                random.randint(30, WINDOW_height - 30))
                    warps.add(warp)
                    warp_gain.play()

                    

            draw_text('점수: {}'.format(score), default_font, screen, 80, 20, YELLOW)
            draw_text('워프: {}'.format(warp_count), default_font, screen, 700, 20, BLUE)
            rocks.update()
            warps.update()
            rocks.draw(screen)
            warps.draw(screen)

            warp = spaceship.collide(warps)

            if spaceship.collide(rocks):
                explosion_sound.play()
                pygame.mixer.music.stop()
                rocks.empty()
                return 'game_screen'
            elif warp:
                warp_count += 1
                warp.kill()
                warp_Interaction.play()

            screen.blit(spaceship.image, spaceship.rect)
            # 왼쪽 끝 가면 오른쪽 끝으로 나오고, 오른쪽 끝으로 가면 왼쪽 끝으로 나오게 한다.
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0] <= 10:
                        pygame.mouse.set_pos(WINDOW_width - 10, mouse_pos[1])
                    elif mouse_pos[0] >= WINDOW_width - 10:
                        pygame.mouse.set_pos(0 + 10, mouse_pos[1])
                    elif mouse_pos[1] <= 10:
                        pygame.mouse.set_pos(mouse_pos[0], WINDOW_height - 10)
                    elif mouse_pos[1] >= WINDOW_height - 10:
                        pygame.mouse.set_pos(mouse_pos[0], 0 + 10)
                    spaceship.set_pos(*mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if warp_count > 0:
                        warp_count -= 1
                        warp_sound.play()
                        sleep(1)
                        rocks.empty()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            transp_surf = pygame.Surface((WINDOW_width, WINDOW_height))
                            transp_surf.set_alpha(150)
                            screen.blit(transp_surf, transp_surf.get_rect())
                            pygame.mouse.set_visible(True)
                            draw_text('일시정지', pygame.font.Font('NanumGothic.ttf', 60), screen, WINDOW_width / 2, WINDOW_height / 2, YELLOW)
                if event.type == QUIT:
                    return 'quit'
    return 'game_screen'

def game_screen():
    global score
    pygame.mouse.set_visible(True)

    start_image = pygame.image.load('image/game_screen.png')
    screen.blit(start_image, [0,0])

    draw_text('우주선으로 암석 피하기', pygame.font.Font('NanumGothic.ttf', 70), screen, WINDOW_width / 2, WINDOW_height / 3.4, WHILE)
    draw_text('점수 : {}'.format(score), default_font, screen, WINDOW_width / 2, WINDOW_height / 2.4, YELLOW)
    draw_text("마우스 버튼이나 'S'를 누르면 게임이 시작됩니다.", default_font, screen, WINDOW_width / 2, WINDOW_height / 2.0, WHILE)
    draw_text("게임을 종료하려면 'Q'키를 누르세요", default_font, screen, WINDOW_width / 2, WINDOW_height / 1.8, WHILE)
    draw_text("게임이 시작되면 종료되지 않습니다.", default_font, screen, WINDOW_width / 2, WINDOW_height / 1.6, WHILE)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                return 'quit'
            elif event.key == pygame.K_s:
                return 'play'
        if event.type == pygame.MOUSEBUTTONDOWN:
            return 'play'
        if event.type == QUIT:
            return 'quit'

    return 'game_screen'

def main_loop():
    action = 'game_screen'
    while action != 'quit':
        if action == 'game_screen':
            action = game_screen()
        elif action == 'play':
            action = game_loop()

    pygame.quit()

main_loop()
