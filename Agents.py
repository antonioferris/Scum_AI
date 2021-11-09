"""
    This file implements the abstract Agent class,
    and the AgentView objects which captures the available information
    given to an agent to make each decision.
"""
from State import AgentView, int_state, int_action_space, int_to_action
from Cards import Deck, Hand, Card
from Cards import all_sets, compute_playable
import random
from collections import Counter

class Agent:
    def __init__(self, action_function):
        """
            An Agent is initialized with an action_function.
            This function takes in an AgentView, and returns:
            1. A legal card or list of cards to be played
            2. "Pass"
            Any other input will be interpreted as a pass.
        """
        self.action_function = action_function

    def auto_passer(self, top_cards, hand):
        """
            Function that auto-passes if no non=pass options are legal
        """
        if not top_cards: # can always play on an empty stack
            return False
        rank = top_cards[0].rank()
        num = len(top_cards)
        return compute_playable(hand)[num-1] < rank

    def get_action(self, view):
        if self.auto_passer(view.top_cards, view.hand):
            return "Pass" # pass turn if no playable cards
        action = self.action_function(view)

        if isinstance(action, int):
            action = int_to_action(action, view)
        if isinstance(action, Card):
            action = (action,)
        return action

def action_space(view):
    """
        Given an agentview, returns a list of all valid actions
        given the state of that game
    """
    poss_actions = ["Pass"]
    sets = all_sets(view.hand)
    if not view.top_cards:
        poss_actions += sets
    else:
        for action in sets:
            if len(action) == len(view.top_cards) and action[0].rank() > view.top_cards[0].rank():
                poss_actions.append(action)
    return poss_actions


def random_action(view):
    return random.choice(action_space(view))

def get_random_agent():
    return Agent(random_action)

def get_baseline_agent():
    return Agent(baseline_action)

def baseline_action(view):
    """
        Chooses an action given the view based on a simple rule:
        Always play when able.
        Choose the smallest card to play.
    """
    actions = int_action_space(view)
    if len(actions) > 1:
        return actions[1]
    return actions[0]

def heuristic_action(view):
    actions = int_action_space(view)
    s = int_state(view)
    if len(actions) == 1:
        return actions[0]
    if not view.top_cards:
        return actions[1]

    r = actions[1] + 1
    score = 0
    for c in view.hand.cards:
        if c.rank() < r:
            score -= 1
        elif c.rank() > r:
            score += 1

    if score >= 0:
        return actions[1]
    return actions[0]
