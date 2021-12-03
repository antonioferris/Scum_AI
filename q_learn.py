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
    def __init__(self, episodes=100):
        self.Q = np.zeros((500000, 14))
        # self.data = pickle.load(open("Q/randbase_backprop_100000.p", "rb"))
        self.num_episodes = episodes

    def q_learn(self, round_data, reward):
        for i in range(len(round_data) - 2, -1, -1):
            s, a = round_data[i]
            sp = round_data[i + 1][0]
            self.Q[s, a] = self.Q[s, a] + 0.1*(reward + 0.95 * self.Q[sp, a] - self.Q[s, a])

    def load_q(self):
        """
            Builds up Q from the reversed data. It repeats this process for num_episodes.
        """
        if exists("Q/best_randbase_backprop_100000_6.p"):
            print("Loading big Q pickle...")
            self.Q = pickle.load(open("Q/best_randbase_backprop_100000_6.p", "rb"))
        elif exists(r"Q\randbase_backprop_100000.p"):
            print("Loading Q pickle...")
            self.Q = pickle.load(open(r"Q\randbase_backprop_100000.p", "rb"))
        else:
            for i in range(self.num_episodes):
                print("On episode", i+1)
                for state, action, reward, state_prime in reversed(self.data):
                    self.Q[state, action] = self.Q[state, action] + 0.1*(reward + 0.95 * self.Q[state_prime, action] - self.Q[state, action])
            
            pickle.dump(self.Q, open(r"Q\randbase_backprop_100000.p", "wb"))

    def optimal_policy(self, state, actions):
        """
            Returns the action with the maximum expected utility based on Q
            and the available actions.
        """
        
        pairs = [(i, x) for i, x in enumerate(self.Q[state]) if i in actions and i != 0]
        max_index = 0
        max_val = float(-Inf)
        for i, x in pairs:
            if x > max_val:
                max_index = i
                max_val = x


        return max_index
    
    def get_q(self):
        return self.Q