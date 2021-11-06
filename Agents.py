"""
    This file implements the abstract Agent class,
    and the AgentView objects which captures the available information
    given to an agent to make each decision.
"""
from Cards import Deck, Hand, Card
from Cards import all_sets, compute_playable
import random

class AgentView:
    def __init__(self, gamestate, i):
        """
            Initialize the agentview of the ith player in the game given the gamestate
        """
        self.hand = gamestate.hands[i]
        self.out = gamestate.out
        self.hand_lengths = [len(hand) for hand in gamestate.hands]
        self.cards_seen = gamestate.cards_seen
        self.top_cards = gamestate.top_cards
        self.passed = gamestate.passed
        self.last_player = gamestate.last_player

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

def baseline_action(view):
    """
        Chooses an action given the view based on a simple rule:
        Always play when able.
        Choose the smallest card to play.
    """
    actions = action_space(view)
    if len(actions) > 1:
        return actions[1]
    return actions[0]