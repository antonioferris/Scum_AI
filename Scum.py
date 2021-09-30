"""
    This file implements a simulation of the card game Scum.

    If you're implementing a graphics library for this game, all you need from here to start should be GameState.

    The rules of this game are as follows:

    A deck of cards is dealt to all players, starting at the President (if there is one) and continuing clockwise
    until all cards have been dealt. After cards are dealt, the scum must hand over the best card in their hand to the president,
    and the president passes back any card they do not want.

    The player on the dealer's left begins by leading any number of cards of the same rank The player on the left may then play an equal number
    of matching cards with a higher face value, or may pass. Note that the same number of cards as the lead must be played. If the leader starts
    with a pair, only pairs may be played on top of it. If three-of-a-kind is led, only three-of-a-kinds can be played on top of it. The next player
    may do the same, and so on.

    This continues until all players have had a turn (which may or may not be because the highest-value card has already been played),
    or opted to pass. When one player runs out of cards, they are out of play for the rest of the round, but the other players can continue
    to play to figure out the titles. The next president is the first player out of the round, and the next scum is the last remaining. 

"""
from Cards import Deck, Hand, is_set
import random

class GameState():
    def __init__(self, n, names):
        """
            Initialize with n, the number of players,
            and names, the names of the player in order.
        """
        self.names = names
        self.n = n
        self.hands = [Hand() for _ in range(n)]
        self.out = [] # ordered list of palyers who are out, with the first player out first in the list
        self.cards_seen = [] # optional parameter for us to use, this is a list of all cards played.
        self.top_cards = [] # the most recently played card(s)
        self.passed = [False] * self.n # list of booleans, True if the player has passed on the current round

class AgentView():
    def __init__(self, gameState, i):
        """
            Initialize the agentview of the ith player in the game given the GameState
        """
        self.hand = gameState.hands[i]
        self.out = gameState.out
        self.hand_lengths = [len(hand) for hand in gameState.hands]
        self.cards_seen = gameState.cards_seen
        self.top_cards = gameState.top_cards
        self.passed = gameState.passed

class Agent():
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
        pass # TODO resume here

    def get_action(self, gameState):
        action = self.action_function(AgentView(gameState))
        if isinstance(action, Card):
            action = [Card]
        return action


class ScumController():
    def init__(self, agents, names=None):
        """
            Initialize a scum game with agents as the players in the game
        """
        self.n = len(agents)
        self.agents = agents
        if not names:
            self.names = [str(i) for i in range(self.n)]
        else:
            self.names = names
        self.gamestate = GameState(self.n, self.names)
        self.president = random.randrange(self.n)
        self.curr_player = self.president

    def incr_player(self):
        self.curr_player = (self.curr_player + 1) % self.n

    def deal_round(self):
        Deck().deal_hands(self.gameState.hands, self.president)

    def turn(self):
        """
            Run a single turn of play for the current player
        """
        action = self.agents[self.curr_player].get_action(self.gamestate)
        if play(action) == "Pass":
            self.gamestate.passed[self.curr_player] = True
        self.incr_player()

    def play(self, action):
        if isinstance(action, list):
            if not set(action) <= set(self.gamestate.hands[self.curr_player]): # skip move if the cards aren't in the players hand
                raise ValueError(f"Action {action} attempted to play cards not in hand")
                return "Pass"
            
            if not is_set(actions): # skip mvoes that aren't a set
                raise ValueError(f"Action {action} is not a set")
                return "Pass"
            
            if self.gamestate.top_cards and rank(actions[0]) <= rank(self.gamestate.top_cards[0]): # skip move if the rank is not higher than the previous move
                return "Pass"

            self.gamestate.top_cards = action # update the top cards
            self.gamestate.hands[self.curr_player].remove(action) # remove the cards from that players hand







        




        

        

    





def main():
    pass

if __name__ == "__main__":
    main()