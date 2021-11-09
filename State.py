"""
    This file is designed to help represent the state and action space
    of Scum as integers

    It allows encoding of views as states
    and actions as integers.
"""
import random
from Cards import CARD_STRS, Deck, Hand, Card
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

class SimpleView:
    def __init__(self, hand, top_cards):
        """
            Initialize the agentview of the ith player in the game given the gamestate
        """
        self.hand = hand
        self.top_cards = top_cards

    def __str__(self):
        s = "Agent View:\n"
        s += "Top Cards: " + str(self.top_cards) + "\n"
        s += "Hand: " + str(self.hand.cards)
        return s

def int_state(view):
    """
        Given an agentview, returns the state as an integer
        This state encodes the 5 highest cards in the hand and the top cards.

        Cards are encoded such that 1-13 represent the 13 ranks, and 0 represents
        the card not existing
    """
    ranks = sorted([card.rank() - 1 for card in view.hand.cards])
    ranks = ranks[-5:] # only get the first 5 cards

    s = 0
    if view.top_cards:
        s += view.top_cards[0].rank() - 1
        s += 14 * (len(view.top_cards) - 1) # encode the number of cards in the middle

    # s = 0 here corresponds to empty top cards
    if s >= 14 * 4:
        print(view)
        raise ValueError(f"State {s} too large in encoding")
    m = 14 * 4
    for d in ranks:
        s += d * m
        m *= 14

    return s

def state_int(s):
    hand = []
    top_cards = []

    if s % 56 != 0: # if s is nonzero 0 mod 14*4, top cards are empty
        top_card_rank = (s % 14)
        s = s // 14

        top_card_count = (s % 4)
        s = s // 4
        for _ in range(top_card_count + 1):
            top_cards.append(top_card_rank + 1)

    for _ in range(5):
        if s == 0:
            break
        r = s % 14
        if r != 0:
            hand.append(r + 1)
        s = s // 14

    return (hand, top_cards)

def test_state():
    """
        tests the int_state function by
        randomly testing it 1000 times and ensuring it matches
        the actual state
    """
    for _ in range(1000):
        d = Deck()
        n = random.randint(11, 26)
        hands = [Hand() for _ in range(n)]
        d.deal_hands(hands)

        for h in hands:
            top_cards = [Card(random.choice(CARD_STRS))] * random.randint(1, 4)
            s = int_state(SimpleView(h, top_cards))
            h2, tc2 = state_int(s) # convert the state back to an integer

            # now, we test to see if the returned state is the same
            h1 = [c.rank() for c in h.cards]
            tc1 = [c.rank() for c in top_cards]

            if sorted(h1) != sorted(h2):
                print(top_cards)
                print(h)
                raise ValueError(f"State conversion failed, state encoded hand {h2} instead of {h1}")
            if sorted(tc1) != sorted(tc2):
                raise ValueError(f"State conversion failed, state encoded top cards {tc2} instead of {tc1}")

def int_action_space(view):
    """
        Given an agentview, returns a list of all valid actions
        given the state of that game as integers
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