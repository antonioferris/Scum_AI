"""
    This file implements the abstract Agent class,
    and the AgentView objects which captures the available information
    given to an agent to make each decision.
"""
from Cards import Deck, Hand, Card
from Cards import all_sets, compute_playable
import random
from collections import Counter

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

    def __str__(self):
        s = "Agent View:\n"
        s += "Top Cards: " + str(self.top_cards) + "\n"
        s += "Hand: " + str(self.hand.cards)
        return s

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

def int_action_space(view):
    """
        Given an agentview, returns a list of all valid actions
        given the state of that gameas integers
    """
    poss_actions = {0}
    if not view.top_cards:
        for card in view.hand.cards:
            poss_actions.add(card.rank() - 1)
    else:
        ranks = Counter([card.rank() for card in view.hand.cards])
        for rank, cnt in ranks.items():
            if cnt >= len(view.top_cards) and rank > view.top_cards[0].rank():
                poss_actions.add(rank - 1)

    poss_actions = sorted(list(poss_actions))
    return poss_actions

def int_to_action(a, view):
    if a == 0:
        return "Pass"

    ranks = Counter([card.rank() for card in view.hand.cards])
    if not view.top_cards:
        n = ranks[a + 1]
    else:
        n = len(view.top_cards)

    action = []
    for card in view.hand.cards:
        if card.rank() == a + 1:
            action.append(card)
            if len(action) == n:
                action = tuple(action)
                break

    return action


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
    actions = int_action_space(view)
    print(view)
    print(f"Actions: {actions}")
    print()
    if len(actions) > 1:
        return actions[1]
    return actions[0]