import random
import json
import itertools
import dataclasses

# state class to store important attributes
@dataclasses.dataclass
class State:
    distance: tuple
    position: tuple
    surroundings: str
    food: tuple


class Learner(object):
    def __init__(self, display_width, display_height, block_size):
        # Game content
        self.display_width = display_width
        self.display_height = display_height
        self.block_size = block_size
        self.qvalues = self.loadInitialQvalues()
        self.history = []

        # Learning parameters
        self.epsilon = 0.1
        self.lr = 0.7
        self.discount = .5

        # Action dictionary
        self.actions = {
            0: 'right',
            1: 'left',
            2: 'up',
            3: 'down'
        }

    def setHyperParameters(self, epsilon, lr, discount):
        # reset hyper parameters
        self.epsilon = epsilon
        self.lr = lr
        self.discount = discount

    def reset(self):
        # reset learner
        self.history = []

    def loadInitialQvalues(self):
        # load in initial q values
        squares = [''.join(s) for s in list(itertools.product(*[['0', '1']] * 4))]
        states = {}
        for row in ['0', '1', '-1']:
            for col in ['2', '3', '-1']:
                for sq in squares:
                    states[str((row, col, sq))] = [0, 0, 0, 0]
        return states

    def saveQvalues(self, path="qvalues.json"):
        # save rest of q values at a given time
        with open(path, "w") as f:
            json.dump(self.qvalues, f)

    def act(self, snake, food):
        # act based on current states
        state = self.retrieveState(snake, food)

        # Epsilon greedy
        rand = random.uniform(0, 1)
        if rand < self.epsilon:
            action_key = random.choices(list(self.actions.keys()))[0]
        else:
            state_scores = self.qvalues[self._GetStateStr(state)]
            action_key = state_scores.index(max(state_scores)) # argmax
        action_val = self.actions[action_key]

        # Remember the actions it took at each state
        self.history.append({
            'state': state,
            'action': action_key
        })
        return action_val

    def updateQValues(self, reason):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if reason:  # Snake Died -> Negative reward
                sN = history[0]['state']
                print(sN)
                aN = history[0]['action']
                state_str = self._GetStateStr(sN)
                if reason == "direction":
                    reward = -150
                else:
                    reward = -100
                self.qvalues[state_str][aN] = (1 - self.lr) * self.qvalues[state_str][
                    aN] + self.lr * reward  # Bellman equation - there is no future state since game is over
                reason = None
            else:
                s1 = h['state']  # current state
                s0 = history[i + 1]['state']  # previous state
                a0 = history[i + 1]['action']  # action taken at previous state

                x1 = s0.distance[0]  # x distance at current state
                y1 = s0.distance[1]  # y distance at current state

                x2 = s1.distance[0]  # x distance at previous state
                y2 = s1.distance[1]  # y distance at previous state

                if s0.food != s1.food:  # Snake ate a food, positive reward
                    reward = 10
                elif (abs(x1) > abs(x2) or abs(y1) > abs(y2)):  # Snake is closer to the food, positive reward
                    reward = 1
                else:
                    reward = -1  # Snake is further from the food, negative reward

                state_str = self._GetStateStr(s0)
                new_state_str = self._GetStateStr(s1)
                self.qvalues[state_str][a0] = (1 - self.lr) * (self.qvalues[state_str][a0]) + self.lr * (
                            reward + self.discount * max(self.qvalues[new_state_str]))  # Bellman equation

    def retrieveState(self, snake, food):
        # take the distance between the head of snake and food
        snake_head = snake[0]
        dist_x = food[0] - snake_head[0]
        dist_y = food[1] - snake_head[1]

        if dist_x > 0:
            pos_x = '0'  # Food is to the right of the snake
        elif dist_x < 0:
            pos_x = '1'  # Food is to the left of the snake
        else:
            pos_x = '-1'  # Food and snake are on the same X file

        if dist_y > 0:
            pos_y = '3'  # Food is below snake
        elif dist_y < 0:
            pos_y = '2'  # Food is above snake
        else:
            pos_y = '-1'  # Food and snake are on the same Y file

        # left, right, up, down squares
        squares = [
            (snake_head[0] - self.block_size, snake_head[1]),
            (snake_head[0] + self.block_size, snake_head[1]),
            (snake_head[0], snake_head[1] - self.block_size),
            (snake_head[0], snake_head[1] + self.block_size),
        ]

        surrounding_list = []
        for sq in squares:
            if sq[0] < 0 or sq[1] < 0:  # off screen left or top
                surrounding_list.append('1')
            elif sq[0] >= self.display_width or sq[1] >= self.display_height:  # off screen right or bottom
                surrounding_list.append('1')
            elif sq in snake[:-1]:  # part of tail
                surrounding_list.append('1')
            else:
                surrounding_list.append('0')
        surroundings = ''.join(surrounding_list)

        return State((dist_x, dist_y), (pos_x, pos_y), surroundings, food)

    def _GetStateStr(self, state):
        return str((state.position[0], state.position[1], state.surroundings))