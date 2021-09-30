"""
    This file implements a simulation of the card game Scum.

    If you're implementing a graphics library for this game, all you need from here to start should be gamestate.

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
from Cards import Deck, Hand, Card
from Cards import is_set, compute_playable, default_trade
import random

class GameState():
    def __init__(self, n, names):
        """
            Initialize with n, the number of players,
            and names, the names of the player in order.
        """
        self.names = names
        self.n = n
        self.hands = [Hand() for _ in range(n)] # list of Hand objects for the players (a Hand is just a list of cards, see Cards.py)
        self.out = [] # ordered list of palyers who are out, with the first player out first in the list
        self.cards_seen = [] # optional parameter for us to use, this is a list of all cards played.
        self.top_cards = [] # the most recently played card(s)
        self.passed = [False] * self.n # list of booleans, True if the player has passed on the current round
        self.last_player = 0 # the most recent player to play a card (the person who opens if the current card is passed on by all)

    def reset(self):
        """
            Resets the GameState to a blank slate for the start of a round.
        """
        for hand in self.hands:
            hand.clear()
        self.out = []
        self.cards_seen = []
        self.top_cards = []
        self.passed = [False] * self.n
        self.last_player = 0

class AgentView():
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
            action = [action]
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
        self.scum = self.n - 1

    def incr_player(self, next_player=-1):
        """
            Function that increments the current player when called without arguments.
            Can also be used to set the next player to a specific player.

            Will automatically iterate past out players.
        """
        if next_player >= 0:
            self.curr_player = next_player
        else:
            self.curr_player = (self.curr_player + 1) % self.n

        while self.curr_player in self.gamestate.out or self.gamestate.passed[self.curr_player]: # skip out / passed players
            self.curr_player = (self.curr_player + 1) % self.n

    def deal_round(self):
        Deck().deal_hands(self.gamestate.hands, self.president)

    def trade(self):
        """
            Initiate trading. For now, this trading is just done automatically.
        """
        default_trade(self.gamestate.hands[self.president], self.gamestate.hands[self.scum])

    def setup_round(self, prev_order):
        """
            Sets up the players to play a round by resetting gamestate, 
            dealing cards, simulating trading.
            if prev_order is None, this function will act as if it is the first round.
        """
        self.gamestate.reset()

        if prev_order:
            self.president = prev_order[0]
            self.scum = prev_order[-1]
        else:
            self.president = random.randrange(self.n)
            self.scum = None
        
        self.curr_player = self.president

        # deal hands starting at the president
        Deck().deal_hands(self.gamestate.hands, self.president)

        # if we have a scum (not first round) initiate trading
        if self.scum != None:
            self.trade()

    def game(self, n_rounds):
        """
            Simulates a game with the loaded agents for n_rounds rounds.
        """
        player_results = [[] for _ in range(self.n)]
        for _ in range(n_rounds):
            scores = self.round()
            for i in range(self.n):
                player_results[scores[i]].append(i)
        return player_results

    def round(self, prev_order):
        """
            Run a single round of play given previous ordering prev_order.
        """
        self.setup_round(prev_order)

        MAX_ITER = 10000# just in case
        for i in range(MAX_ITER + 1):
            if i == MAX_ITER:
                raise ValueError("ERROR: MAX ITER REACHED. INFINITE LOOP DETECTED.")
            
            scores = self.turn()
            if scores != None: # only get a return value if the round is over.
                return scores


    def turn(self):
        """
            Run a single turn of play for the current player
        """
        view = AgentView(self.gamestate, self.curr_player)
        action = self.agents[self.curr_player].get_action(view)
        if self.play(action) == "Pass":
            self.gamestate.passed[self.curr_player] = True

        # test for end of game
        if len(self.gamestate.out) >= self.n - 1: # are all but 1 players out?
            # add the last player to the end of out
            for p in range(self.n):
                if p not in self.gamestate.out:
                    self.gamestate.out.append(p)
                    return self.gamestate.out # final scores is the order of going out

        if all(self.gamestate.passed): # all players have passed, move play to the last_player to lead.
            self.gamestate.passed = [False] * self.n  # reset passed list
            self.incr_player(self.gamestate.last_player)
        else: # otherwise, increment player normally
            self.incr_player()

    def play(self, action):
        if isinstance(action, list):
            if not set(action) <= set(self.gamestate.hands[self.curr_player]): # skip move if the cards aren't in the players hand
                raise ValueError(f"Action {action} attempted to play cards not in hand")
                return "Pass"
            
            if not is_set(action): # skip mvoes that aren't a set
                raise ValueError(f"Action {action} is not a set")
                return "Pass"
            
            if self.gamestate.top_cards and action[0].rank() <= self.gamestate.top_cards[0].rank(): # skip move if the rank is not higher than the previous move
                raise ValueError(f"Action {action} does not beat top cards {self.gamestate.top_cards}")
                return "Pass"

            self.gamestate.top_cards = action # update the top cards
            self.gamestate.last_player = self.curr_player
            self.gamestate.seen_cards += action # mark the cards as seen
            self.gamestate.hands[self.curr_player].remove(action) # remove the cards from that players hand
            if not self.gamestate.hands[self.curr_player]: # is the player's hand now empty...
                self.gamestate.out.append(self.curr_player)
            return "Not Passed"
        return "Pass"







        




        

        

    





def main():
    pass

if __name__ == "__main__":
    main()