from random import randint
import numpy as np
import pickle

from numpy.core.numeric import Inf
from State import SimpleView, int_state, int_action_space, int_to_action
from os.path import exists


class QLearning():

    def __init__(self, data_loc):
        self.Q = np.zeros((500000, 14))
        with open(data_loc, "rb") as f:
            self.data = pickle.load(f)

    def q_learn(self):
        for _ in range(1000):
            for state, action, reward, state_prime in self.data[:10000]:
                self.Q[state, action] = self.Q[state, action] + 0.1*(reward + 0.8 * self.Q[state_prime, action] - self.Q[state, action])

    def optimal_policy(self, state, actions):
        pairs = [(i, x) for i, x in enumerate(self.Q[state]) if i in actions]
        max_index = 0
        max_val = float(-Inf)
        for i, x in pairs:
            if x > max_val:
                max_index = i

        return max_index