import random
from enum import Enum

import pygame
import QLearner
from Slider import Slider
from CustomButton import CustomButton

pygame.init()
smallFont = pygame.font.SysFont("bahnschrift", 15)
font = pygame.font.SysFont("bahnschrift", 25)
bigFont = pygame.font.SysFont("bahnschrift", 35)

complete_display_height = 640

display_width = 640
display_height = 480
block_size = 20

speed = 25

green = (34, 177, 76)
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)
red = (255, 0, 0)

start: bool = False

selected_model = "Human"
high_score = 0
episodes = 0

learning_rate = 0.5
epsilon_value = 0.01
discount_value = 0.2

epsilon_slider = Slider((20, display_height + 115), 1.0, 2,
                        "Epsilon")

learning_rate_slider = Slider((180, display_height + 115), 1.0, 80,
                              "Learning Rate")

discount_slider = Slider((340, display_height + 115), 1.0, 90,
                         "Discount Factor")

global_message = f"Current agent: {selected_model}"

class Movement(Enum):
    STOP = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class GameBoard:
    def __init__(self, width=display_width, height=display_height):
        self.display = pygame.display.set_mode((width, complete_display_height))
        self.display_width = width
        self.display_height = height
        self.clock = pygame.time.Clock()

        self.head = (width / 2 - block_size * 10, height / 2)
        self.snake = [self.head, (self.head[0] - block_size, self.head[1]),
                      (self.head[0] - block_size * 2, self.head[1])]
        self.length = 3

        if start:
            self.direction = Movement.RIGHT
        else:
            self.direction = Movement.STOP

        self.food = (self.head[0] + block_size * 10, self.head[1])
        self.start_button = CustomButton(self.display, display_width - 140, display_height + 10, 120, 40, text='Start',
                                         fontSize=25, margin=20, inactiveColour=(0, 255, 0),
                                         radius=4, onClick=self.toggleStart)
        self.train_button = CustomButton(self.display, display_width - 140, display_height + 60, 120, 40,
                                         text='Train', fontSize=20, margin=20, inactiveColour=(0, 250, 0),
                                         radius=4, onClick=self.toggleTrain)
        self.restart_button = CustomButton(self.display, display_width - 140, display_height + 110, 120, 40,
                                           text='Restart', fontSize=20, margin=20, inactiveColour=(250, 250, 0),
                                           radius=4, onClick=self.toggleRestart)

        self.human_button = CustomButton(self.display, 20, display_height + 60, 100, 40,
                                         text="Human", fontSize=20, margin=20, inactiveColour=(250, 125, 0),
                                         radius=4, onClick=self.toggleChoice, onClickParams="Human")
        self.qlearn_button = CustomButton(self.display, 140, display_height + 60, 100, 40,
                                          text="Q-Learn", fontSize=20, margin=20, inactiveColour=(250, 125, 0),
                                          radius=4, onClick=self.toggleChoice, onClickParams="Q-Learn")

        if start:
            self.toggleStart(True)
        if speed == 200:
            self.toggleTrain(True)

    def toggleChoice(self, model):
        global selected_model
        global global_message
        selected_model = model
        global_message = f"Current agent: {model}"
        self.toggleRestart()
        QModel.reset()

    def toggleRestart(self):
        global episodes
        global high_score
        global start
        global speed
        episodes = 0
        high_score = 0
        start = False
        self.direction = Movement.STOP
        self.head = (self.display_width / 2 - block_size * 10, self.display_height / 2)
        self.snake = [self.head, (self.head[0] - block_size, self.head[1]),
                      (self.head[0] - block_size * 2, self.head[1])]
        self.length = 3
        self.food = (self.head[0] + block_size * 10, self.head[1])
        QModel.qvalues = QModel.loadInitialQvalues()
        self.start_button.text = font.render("Start", True, "black")
        self.start_button.inactiveColour = (0, 250, 0)
        self.train_button.text = font.render("Train", True, "black")
        self.train_button.inactiveColour = (0, 250, 0)
        speed = 20

    def toggleTrain(self, first=False):
        global speed
        if selected_model == "Human":
            return
        if first and speed == 500000:
            self.train_button.text = font.render("Training", True, "black")
            self.train_button.inactiveColour = (250, 0, 0)
        elif speed == 500000:
            self.train_button.text = font.render("Train", True, "black")
            self.train_button.inactiveColour = (0, 250, 0)
            speed = 20
        else:
            self.train_button.text = font.render("Training", True, "black")
            self.train_button.inactiveColour = (250, 0, 0)
            speed = 500000
            pygame.time.delay(100)

    def toggleStart(self, first=False):
        global start
        if first and start:
            self.start_button.text = font.render("Stop", True, "black")
            self.start_button.inactiveColour = (250, 0, 0)
        elif not start:
            start = True
            self.start_button.text = font.render("Stop", True, "black")
            self.start_button.inactiveColour = (250, 0, 0)
            self.direction = Movement.RIGHT
        else:
            start = False
            self.start_button.text = font.render("Start", True, "black")
            self.start_button.inactiveColour = (0, 250, 0)
            self.direction = Movement.STOP

    def generate_food(self):
        random_x = random.randint(0, (display_width - block_size)
                                  // block_size) * block_size
        random_y = random.randint(2, (display_height - block_size)
                                  // block_size) * block_size
        self.food = (random_x, random_y)
        if self.food in self.snake:
            self.generate_food()

    def updateUI(self):
        global selected_model
        self.display.fill((84, 140, 52))
        pygame.draw.circle(self.display, (225, 215, 0),
                           (self.snake[0][0] + block_size // 2,
                            self.snake[0][1] + block_size // 2),
                           10)
        for pt in self.snake[1:]:
            pygame.draw.rect(self.display, (255, 215, 0),
                             pygame.Rect(pt[0], pt[1], block_size, block_size))
        pygame.draw.circle(self.display, (200, 0, 0),
                           (self.food[0] + block_size // 2,
                            self.food[1] + block_size // 2), 10, 4)
        food = font.render("Food: " + str(self.length - 3), True, (225, 215, 10))
        high = font.render("Top Score: " + str(high_score), True, (225, 215, 10))
        episode_counter = font.render("Episodes: " + str(episodes), True, (225, 215, 10))

        text_surface = pygame.Surface((display_width, 40))
        text_surface.fill((80, 116, 44))
        text_surface.blit(food, (70, 0))
        text_surface.blit(high, (240, 0))
        text_surface.blit(episode_counter, (410, 0))
        self.display.blit(text_surface, [0, 0])

        phrase = font.render(global_message, True, (225, 215, 10))
        bottom_surface = pygame.Surface((display_width, 160))
        bottom_surface.fill((80, 100, 44))
        bottom_surface.blit(phrase, (30, 10))
        self.display.blit(bottom_surface, [0, display_height])

        self.start_button.listen(pygame.mouse.get_pressed())
        self.start_button.draw()

        self.train_button.listen(pygame.mouse.get_pressed())
        self.train_button.draw()

        self.restart_button.listen(pygame.mouse.get_pressed())
        self.restart_button.draw()

        self.human_button.listen(pygame.mouse.get_pressed())
        self.human_button.draw()

        self.qlearn_button.listen(pygame.mouse.get_pressed())
        self.qlearn_button.draw()

        epsilon_slider.render(game.display)
        epsilon_slider.changeValue()

        learning_rate_slider.render(game.display)
        learning_rate_slider.changeValue()

        discount_slider.render(game.display)
        discount_slider.changeValue()

        self.checkParameterChanges()
        pygame.display.update()

    def checkParameterChanges(self):
        global epsilon_value
        global discount_value
        global learning_rate
        changed = False
        if epsilon_value != epsilon_slider.getValue():
            epsilon_value = epsilon_slider.getValue()
            changed = True
        if discount_value != discount_slider.getValue():
            discount_value = discount_slider.getValue()
            changed = True
        if learning_rate != learning_rate_slider.getValue():
            learning_rate = learning_rate_slider.getValue()
            changed = True
        if changed:
            self.toggleRestart()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != Movement.DOWN:
                    self.direction = Movement.UP
                elif event.key == pygame.K_DOWN and self.direction != Movement.UP:
                    self.direction = Movement.DOWN
                elif event.key == pygame.K_LEFT and self.direction != Movement.RIGHT:
                    self.direction = Movement.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Movement.LEFT:
                    self.direction = Movement.RIGHT
        return self.process_move()

    def check_q_events(self, move):
        print(move)
        if not start:
            self.direction = Movement.STOP
        elif move == "up":
            if self.direction != Movement.DOWN:
                self.direction = Movement.UP
            else:
                return False, "direction"
        elif move == "down":
            if self.direction != Movement.UP:
                self.direction = Movement.DOWN
            else:
                return False, "direction"
        elif move == "left":
            if self.direction != Movement.RIGHT:
                self.direction = Movement.LEFT
            else:
                return False, "direction"
        elif move == "right":
            if self.direction != Movement.LEFT:
                self.direction = Movement.RIGHT
            else:
                return False, "direction"
        return self.check_events()

    def process_move(self):
        if self.direction == Movement.STOP:
            return True, None
        (x, y) = self.head
        if self.direction == Movement.UP:
            y -= block_size
        elif self.direction == Movement.DOWN:
            y += block_size
        elif self.direction == Movement.LEFT:
            x -= block_size
        elif self.direction == Movement.RIGHT:
            x += block_size
        self.head = (x, y)

        if self.checkEnd():
            return False, "end"
        self.snake.insert(0, self.head)
        if self.head == self.food:
            self.length += 1
            self.generate_food()
        else:
            self.snake.pop()
        return True, None

    def checkEnd(self):
        if self.head in self.snake[1:]:
            return True
        elif self.head[0] > display_width - block_size:
            return True
        elif self.head[0] < 0:
            return True
        elif self.head[1] > display_height - block_size:
            return True
        elif self.head[1] < 40:
            return True
        return False


def restart():
    global episodes
    global high_score
    newGame = GameBoard()
    episodes = 0
    high_score = 0
    return newGame


if __name__ == '__main__':
    # human and game
    game = restart()
    # qlearner
    deadQ = False
    QModel = QLearner.Learner(display_width, display_height, block_size)
    QModel.reset()
    QModel.setHyperParameters(epsilon_value, learning_rate, discount_value)

    while True:
        if selected_model == "Human":
            if game.length - 3 > high_score:
                high_score = game.length - 3
            complete = game.checkEnd()
            if complete and game.length > 1:
                episodes += 1
                game = GameBoard()
            game.updateUI()
            game.clock.tick(speed)
            if not game.check_events():
                episodes += 1
                game = GameBoard
        elif selected_model == "Q-Learn":
            QModel.reset()
            deadQ = False
            while not deadQ and selected_model == "Q-Learn":
                QModel.setHyperParameters(epsilon_value, learning_rate, discount_value)
                if episodes % 100 == 0 and episodes > 0:
                    QModel.saveQvalues(path="QLearner/qvalues"+str(episodes)+".json")
                if game.length - 3 > high_score:
                    high_score = game.length - 3
                worked = True
                reason = None
                if not start:
                    worked, reason = game.check_q_events("stop")
                if start:
                    action = QModel.act(game.snake, game.food)
                    worked, reason = game.check_q_events(action)
                    QModel.updateQValues(reason)
                game.updateUI()
                if reason:
                    deadQ = True
                    episodes += 1
                    game = GameBoard()
                game.clock.tick(speed)