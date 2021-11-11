from random import randint
import numpy as np
from State import SimpleView, int_state, int_action_space, int_to_action


class QLearning():

    def __init__(self, actions, state, view):
        self.view = view
        self.curr_state = state
        self.actions = actions
        self.a_sp_pairs = self.generate_iter_pairs()
        max_sp = 0
        if len(self.a_sp_pairs) > 0:
            max_sp = max([arr[1] for arr in self.a_sp_pairs])
        self.Q = np.zeros((max(state, max_sp)+1, 14))

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
        for (action, state_prime) in self.a_sp_pairs:
            reward = randint(10, 500)

            temp_actions = self.actions
            temp_actions.remove(action)
            if len(temp_actions) == 0:
                reward = 1000

            self.Q[self.curr_state, action - 1] = self.Q[self.curr_state, action - 1] + 0.1*(reward + 0.95 * self.Q[state_prime, action - 1] - self.Q[self.curr_state, action - 1])

    def optimal_policy(self):
        if not np.any(self.Q[self.curr_state]):
            return np.random.choice(self.actions)
        else:
            return np.argmax(self.Q[self.curr_state]) + 1