from random import randint
import numpy as np
import pickle
from State import SimpleView, int_state, int_action_space, int_to_action
from os.path import exists


class QLearning():

    def __init__(self, actions, state, view):
        self.view = view
        self.curr_state = state
        self.actions = actions
        self.Q = np.zeros((500000, 14))

    def generate_iter_pairs(self):
        pairs = []
        for action in self.actions:
            if action != 0:
                temp_actions = self.view.hand
                cards_Action = int_to_action(action, self.view)
                temp_actions.remove(cards_Action)
                view = SimpleView(temp_actions, cards_Action)
                state = int_state(view)
                pair = (action, state)
                pairs.append(pair)

        return pairs

    def q_learn(self):
        if not exists("data\baseline_q.p"):
            with open("data/baseline_7.p", "rb") as f:
                data = pickle.load(f)

            for state, action, reward, state_prime in data:
                if action in self.actions:
                    self.Q[state, action] = self.Q[state, action] + 0.1*(reward + 0.95 * self.Q[state_prime, action] - self.Q[state, action])

            pickle.dump(self.Q, open("data/baseline_q.p", "wb"))
        else:
            self.Q = pickle.load(open("data/baseline_q.p", "rb"))

    def optimal_policy(self):
        if not np.any(self.Q[self.curr_state]):
            return np.random.choice(self.actions)
        else:
            val = np.argmax(self.Q[self.curr_state])
            return val