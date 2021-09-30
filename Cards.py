"""
    This file contains the class definitions and utility functions to manage a deck of cards.
    It is used by Scum.py to simulate the card game Scum.
"""
from functools import total_ordering
import random
from collections import Counter

CARD_STRS = [str(val) + suit for val in list(range(2, 11)) + ["J", "Q", "K", "A"] for suit in ["C", "D", "S", "H"]]
VALUE_DICT = {
    "J" : 11,
    "Q" : 12,
    "K" : 13,
    "A" : 14
}


# util functions

def is_set(cards):
    """
        Verifies that a list of cards is a set (all the same rank)
    """
    return len({card.name[:-1] for card in cards}) == 1 # take out the suit, and see if all are the same

def all_sets(hand):
    """
        Given a hand, returns the tuple of every unique set of cards in the hand
    """
    sets = []
    set = []
    for card in hand.cards:
        if set and set[-1].rank() != card.rank():
            set = [card]
        else:
            set.append(card)
        sets.append(tuple(set))
    return sets


def compute_playable(hand):
    """
        Computes the largest rank playable by this hand at each possible multiple threshold.
        For example, the hand ["KS", "10S", "10H"] would have a playability of
        [12, 9, 0, 0]
        because the hand can play on anything Queen (rank 12) or below singles,
        anything 9 or below doubles, and can't play on triples or quads.
    """
    ranks = [card.rank() for card in hand.cards]
    r = [0] * 4
    c = Counter(ranks)
    for rank, cnt in c.items():
        for i in range(cnt):
            r[i] = max(r[i], rank - 1) # the highest we can play at any lower count is 1 less than the rank here
    return r

def default_give(president_hand):
    """
        Find the card that the president would give by default
        (lowest unpaired card)
    """
    ranks = [card.rank() for card in president_hand.cards]
    c = Counter(ranks)
    try:
        give_rank = min(rank for rank, cnt in c.items() if cnt == 1)
    except ValueError: # if there are no unpaired cards, just return the smallest card
        return president_hand.cards[0]

    for card in president_hand.cards:
        if card.rank() == give_rank:
            return card


def default_trade(president_hand, scum_hand):
    """
        Baseline implementation of basic auto-trading between president and scum.
    """

    # scum gives their highest card
    scum_give = scum_hand.cards[-1]
    president_hand.get(scum_give)
    scum_hand.remove(scum_give)

    # president gives away the lowest unpaired card
    pres_give = default_give(president_hand)
    president_hand.remove(pres_give)
    scum_hand.get(pres_give)



# total ordering lets Cards be sorted without needing every possible comparison function implemented below.
@total_ordering
class Card:
    def __init__(self, name):
        """
            Name is a unique identifier for the card.
            Names will be of the form "AS" (Ace of Spades), "10D" (ten of Diamonds)
            Suits are (H)earts, (S)pades, (C)lubs, (D)iamonds
        """
        self.name = name

    def rank(self):
        """
            Get the rank of the card, in ordered int form.
        """
        v = self.name[:-1]
        if v in VALUE_DICT:
            v = VALUE_DICT[v]
        return int(v)


    def __eq__(self, other):
        if isinstance(other, Card):
            return self.name == other.name
        return False

    def __lt__(self, other):
        return CARD_STRS.index(self.name) < CARD_STRS.index(other.name)

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Hand:
    def __init__(self):
        self.cards = []

    def get(self, card):
        self.cards.append(card)
        self.cards.sort()

    def remove(self, cards):
        if not isinstance(cards, tuple):
            cards = (cards,) # wrap singleton cards to be lists for universality
        for card in cards:
            if card not in self.cards:
                raise ValueError(f"Attempted to remove card {card} from hand {self.cards}")
            self.cards.remove(card)
        self.cards.sort()

    def clear(self):
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return " ".join(map(str, self.cards))


class Deck:
    def __init__(self):
        """
            Every deck starts as a shuffled list of cards.
        """
        self.cards = [Card(s) for s in CARD_STRS]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

    def deal_hands(self, hands, president=0):
        """
            Deals the entire deck into n different hands.
            president is the index of the president (dealing starts at the president)
        """
        n = len(hands) # make sure the hands are empty before dealing to them.
        for hand in hands:
            hand.clear()
        for i in range(len(self.cards)):
            hands[(i + president) % n].get(self.deal()) # deal the card to the next player in a circle.

        return hands

