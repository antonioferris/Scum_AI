"""
    This file contains the definition of ParamAgent,
    which uses a parametric version of the state / action pair to
    directly evaluate possibilities.
"""
from river import linear_model
from State import int_action_space
import numpy as np
from random import shuffle, random, choice

class ParamModel():
    def __init__(self, exploration=0.1, alpha=1):
        self.model = linear_model.LogisticRegression()
        self.exploration = exploration
        self.alpha = alpha

    def X(self, view, a):
        def baseline():
            actions = int_action_space(view)
            if len(actions) > 1:
                return actions[1]
            return actions[0]
        X = {
            "like_baseline" : 1 if a == baseline() else 0,
            # "action" : a,
            # "Out Count" : len(view.out),
            # "Top Card Rank" : view.top_cards[0].rank()-1 if view.top_cards else 0,
            # "Top Card Count" : len(view.top_cards)
        }
        # X.update(dict(enumerate(view.hand_lengths + view.passed + [1 if i == view.last_player else 0 for i in range(7)])))
        return X

    def get_action(self, view):
        actions = int_action_space(view)

        if len(actions) == 1:
            return actions[0]
        self.exploration *= self.alpha
        if random() < self.exploration:
            return choice(actions)

        curr_action = None
        curr_p = -1
        shuffle(actions)
        for a in actions[1:]:
            X = self.X(view, a)
            p = self.model.predict_proba_one(X)[True]
            if p > curr_p:
                curr_action = a
                curr_p = p

        return curr_action

    def learn(self, X, Y):
        self.model.learn_one(X, Y)



