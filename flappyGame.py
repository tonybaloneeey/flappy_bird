import os

import pygame
from sys import exit
import random
import neat

pygame.init()
clock = pygame.time.Clock()

# Game Settings
SCREEN_HEIGHT = 720
SCREEN_WIDTH = 551
FLOOR_HEIGHT = 520
GRAVITY = 0.5
SCROLL_SPEED = 2
gen = 0

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

# Game

bird_start_position = (100, 250)
score = 0
font = pygame.font.SysFont('Segoe', 26)
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


class aiBird(Bird):
    def update(self, flap_action):
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

        # AI Input
        if flap_action and not self.flap and self.rect.y > 0 and self.alive:
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

    def get_x(self):
        return self.top_left_x

    def get_y(self):
        return self.rect.y

    def is_passed(self, x_pos):
        if x_pos > self.rect.x:
            return True
        return False

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
            pygame.quit()
            exit()


# Game Main Method
def run_single_player_window():
    global score

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
            if collision_ground:
                window.blit(game_over_image, (SCREEN_WIDTH // 2 - game_over_image.get_width() // 2,
                                              SCREEN_HEIGHT // 2 - game_over_image.get_height() // 2))
                if user_input[pygame.K_r]:
                    score = 0
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


def run_ai_window(genomes, config):
    global gen
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play

    nets = []
    birds = pygame.sprite.Group()
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.add(aiBird())
        ge.append(genome)

    def are_alive(birds):
        for bird in birds:
            if bird.alive:
                return True
        return False

    global score

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
        birds.draw(window)

        # Show Score
        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 20))

        # Update - Pipes, Ground and Bird
        if are_alive(birds):
            pipes.update()
            ground.update()

        # Collision Detection
        for bird in birds:
            collision_pipes = pygame.sprite.spritecollide(bird, pipes, False)
            collision_ground = pygame.sprite.spritecollide(bird, ground, False)

            if collision_pipes or collision_ground:
                bird.alive = False

                ge[birds.sprites().index(bird)].fitness -= 1
                nets.pop(birds.sprites().index(bird))
                ge.pop(birds.sprites().index(bird))

                if collision_ground:
                    # print("COLLISION GROUND")
                    # window.blit(game_over_image, (SCREEN_WIDTH // 2 - game_over_image.get_width() // 2,
                    #                              SCREEN_HEIGHT // 2 - game_over_image.get_height() // 2))
                    if user_input[pygame.K_r]:
                        score = 0
                        menu()

        # Spawn Pipes
        if pipe_timer <= 0 and are_alive(birds):
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

        pipe_ind = 0
        if are_alive(birds):
            if len(pipes) > 1 and birds.sprites()[0].rect.x > pipes.sprites()[0].rect.x + pipes.sprites()[0].rect.width:
                pipe_ind = 2

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            #output = nets[birds.sprites().index(bird)].activate(
            #    (bird.rect.y, abs(bird.rect.y - pipes.sprites()[pipe_ind + 1].rect.y),
            #     abs(bird.rect.y - (pipes.sprites()[pipe_ind].rect.y + pipes.sprites()[pipe_ind].rect.height))))

            output = nets[birds.sprites().index(bird)].activate(
                (bird.rect.y, abs(bird.rect.y - pipes.sprites()[pipe_ind].rect.y + pipes.sprites()[pipe_ind].rect.height),
                 abs(bird.rect.y - pipes.sprites()[pipe_ind + 1].rect.y)))

            pygame.draw.circle(window, (255, 0, 0), (
            pipes.sprites()[0].rect.x, pipes.sprites()[pipe_ind].rect.y + pipes.sprites()[pipe_ind].rect.height), 5)

            #print("Y:", pipes.sprites()[0].rect.y + pipes.sprites()[0].rect.height)

            if output[
                0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                # print("OUTPUT", output[0])
                birds.update(True)  # jump
            else:
                birds.update(False)  # don't jump

        clock.tick(60)
        pygame.display.update()


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(run_ai_window, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)


def menu():
    global game_stopped

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
            # run_single_player_window()
            run_ai_window()

        pygame.display.update()


# Menu
menu()
