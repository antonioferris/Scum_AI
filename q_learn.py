from random import randint
import numpy as np
import pickle

from numpy.core.numeric import Inf
from State import SimpleView, int_state, int_action_space, int_to_action
from os.path import exists


class QLearning():
    """
        A Q-Learning object is generated in order to initialize Q,
        the data it builds Q from, and the number of episodes used
        to generate Q.
    """
    def __init__(self, f, episodes=100):
        if exists(r"Q\backprop_q.p"):
            self.Q = pickle.load(open(r"Q\backprop_q.p", "rb"))
        else:
            self.Q = np.zeros((500000, 14))
        self.data = pickle.load(open(f, "rb"))
        self.num_episodes = episodes

    def q_learn(self):
        """
            Builds up Q from the reversed data. It repeats this process for num_episodes.
        """
        for _ in range(self.num_episodes):
            for state, action, reward, state_prime in reversed(self.data):
                self.Q[state, action] = self.Q[state, action] + 0.1*(reward + 0.95 * self.Q[state_prime, action] - self.Q[state, action])

        pickle.dump(self.Q, open(r"Q\backprop_q.p", "wb"))

    def optimal_policy(self, state, actions):
        """
            Returns the action with the maximum expected utility based on Q
            and the available actions.
        """
        pairs = [(i, x) for i, x in enumerate(self.Q[state]) if i in actions]
        max_index = 0
        max_val = float(-Inf)
        for i, x in pairs:
            if x > max_val:
                max_index = i

        return max_index