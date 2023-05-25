import os
import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

# Game Settings
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 551
FLOOR_HEIGHT = 520
GRAVITY = 0.5
SCROLL_SPEED = 2

window = None

# Images
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]
background = pygame.image.load("assets/background.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")

pygame.display.set_icon(bird_images[2])

bird_start_position = (100, 250)
score = 0
global cur_name
txt_score = 0
txt_name = ''
font = pygame.font.SysFont('bahnschrift', 25)
game_stopped = True


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.vel = 0
        self.flap = False
        self.alive = True
        self.dead = False

    def update(self, user_input):
        # Animate Bird
        if self.alive:
            self.image_index += 1
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        # Gravity and Flap
        self.vel += GRAVITY
        if self.vel > 7:
            self.vel = 7
        if self.rect.y < 500:
            self.rect.y += int(self.vel)
        if self.vel == 0:
            self.flap = False

        # Rotate Bird
        self.image = pygame.transform.rotate(self.image, self.vel * -7)

        # User Input
        if user_input[pygame.K_SPACE] and not self.flap and self.rect.y > 0 and self.alive:
            self.flap = True
            self.vel = -7


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type, scroll_speed=1):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type
        self.scroll_speed = scroll_speed
        self.top_left_x = 0

    def update(self):
        # Move Pipe
        self.rect.x -= self.scroll_speed
        self.top_left_x = self.rect.x + self.rect.width
        if self.rect.x <= -SCREEN_WIDTH:
            self.kill()

        # Score
        global score
        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y, scroll_speed=1):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.scroll_speed = scroll_speed

    def update(self):
        # Move Ground
        self.rect.x -= self.scroll_speed
        if self.rect.x <= -SCREEN_WIDTH:
            self.kill()


def quit_game():
    # Exit Game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open('highscores.txt', 'a') as f:
                f.write('\n')
            name, found_score = get_highest_score("highscores.txt", cur_name)
            global score
            print('Your Score:', score)
            if score > found_score:
                print('New High Score!')
            elif name == '' and found_score == 0:
                print('No Previous High Scores Found!')
            else:
                print('Previous Best:', found_score, 'by', name)

            pygame.quit()
            exit()


# Game Main Method
def run_single_player_window():
    global score
    written = False

    # Instantiate Bird
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    # Setup Pipes
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # Instantiate Initial Ground
    x_pos_ground, y_pos_ground = 0, FLOOR_HEIGHT
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground, SCROLL_SPEED))

    run = True
    while run:

        # Quit
        quit_game()

        # Reset Frame
        window.fill((0, 0, 0))

        # User Input
        user_input = pygame.key.get_pressed()

        # Draw Background
        window.blit(background, (0, 0))

        # Spawn Ground
        if len(ground) <= 2:
            ground.add(Ground(SCREEN_WIDTH, y_pos_ground, SCROLL_SPEED))

        # Draw - Pipes, Ground and Bird
        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        # Show Score
        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        # Update - Pipes, Ground and Bird
        if bird.sprite.alive:
            pipes.update()
            ground.update()
        bird.update(user_input)

        # Collision Detection
        collision_pipes = pygame.sprite.spritecollide(bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)

        if collision_pipes or collision_ground:
            bird.sprite.alive = False
            if not written:
                written = True
                with open('highscores.txt', 'a') as f:
                    f.write("|" + str(score))
            if collision_ground:
                window.blit(game_over_image, (SCREEN_WIDTH // 2 - game_over_image.get_width() // 2,
                                              SCREEN_HEIGHT // 3 - game_over_image.get_height() // 3))

                if user_input[pygame.K_r]:
                    score = 0
                    with open('highscores.txt', 'rb+') as f:
                        f.seek(-2, os.SEEK_END)
                        f.truncate()
                    break

        # Spawn Pipes
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-600, -480)
            y_bottom = y_top + random.randint(90, 130) + bottom_pipe_image.get_height()

            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top', SCROLL_SPEED))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom', SCROLL_SPEED))
            pipe_timer = random.randint(100, 150)
        pipe_timer -= 1

        pipe_width = pipes.sprites()[0].rect.width
        if pipes.sprites()[0].rect.x + pipe_width < 0 and pipes.sprites()[1].rect.x + pipe_width < 0:
            pipes.remove(pipes.sprites()[0])
            pipes.remove(pipes.sprites()[0])

        clock.tick(60)
        pygame.display.update()


def menu():
    global game_stopped, window
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    while game_stopped:
        quit_game()

        # Draw Menu
        window.fill((0, 0, 0))
        window.blit(background, (0, 0))
        window.blit(ground_image, Ground(0, FLOOR_HEIGHT))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (SCREEN_WIDTH // 2 - start_image.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - start_image.get_height() // 2))

        # User Input
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            run_single_player_window()

        pygame.display.update()
    pygame.quit()


def start_game():
    username = input("Enter your name: ")
    global cur_name
    cur_name = username
    print("The game opened in new window.")
    with open("highscores.txt", "a") as f:
        f.write(username)
    menu()


def get_highest_score(file_name, cur_name=''):
    with open(file_name, 'r') as file:
        file_score = 0
        file_name = ''

        for line in file:
            try:
                name, val = line.strip().split('|')
            except:
                continue
            val = int(val)

            if val > file_score and name != cur_name:
                file_score = val
                file_name = name
    return file_name, file_score


start_game()
