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

from os.path import exists
from Cards import Deck, Hand, Card
from Cards import is_set, compute_playable, default_trade
from Agents import Agent, DataCollectingAgent
from State import AgentView
from collections import Counter
from graphics import draw_graphics, quit_pygame, set_up_graphics
import random
import time


class GameState:
    def __init__(self, n, names, tick_speed):
        """
            Initialize with n, the number of players,
            and names, the names of the player in order.
        """
        self.names = names
        self.n = n
        self.hands = [Hand() for _ in range(n)] # list of Hand objects for the players (a Hand is just a list of cards, see Cards.py)
        self.out = [] # ordered list of players who are out, with the first player out first in the list
        self.cards_seen = [] # optional parameter for us to use, this is a list of all cards played.
        self.top_cards = [] # the most recently played card(s)
        self.passed = [False] * self.n # list of booleans, True if the player has passed on the current round
        self.last_player = 0 # the most recent player to play a card (the person who opens if the current card is passed on by all)
        self.last_action = "Pass"
        self.turn_count = 1
        self.rounds_won = [0 for _ in range(n)]
        self.play_order = [i for i in range(n)]
        self.tick_speed = tick_speed

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

    def __repr__(self):
        return str(self)

    def __str__(self):
        s = ""
        s += "Cards Seen: " + str(self.cards_seen) + "\n"
        s += "Names: " + str(self.names) + "\n"
        s += "Hands: " + str(self.hands) + "\n"
        s += "Out: " + str(self.out) + "\n"
        s += "Top Cards: " + str(self.top_cards) + "\n"
        s += "Passed: " + str(self.passed) + "\n"
        s += "Last Player: " + str(self.last_player) + "\n"
        return s


class ScumController:
    def __init__(self, agents, names=None, draw=False, tick_speed=3):
        """
            Initialize a scum game with agents as the players in the game
        """
        self.n = len(agents)
        self.agents = agents
        if not names:
            self.names = [str(i) for i in range(self.n)]
        else:
            self.names = names
        self.gamestate = GameState(self.n, self.names, tick_speed)
        self.president = random.randrange(self.n)
        self.curr_player = self.president
        self.scum = self.n - 1
        self.draw = draw
        self.collected_data = []
        if draw:
            set_up_graphics()

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

    def deal_round(self):
        Deck().deal_hands(self.gamestate.hands, self.president)

    def trade(self, prev_order):
        """
            Initiate trading. For now, this trading is just done automatically.
        """
        # the president takes the 3 highest cards away from the scum
        default_trade(self.gamestate.hands[prev_order[0]], self.gamestate.hands[prev_order[-1]])
        default_trade(self.gamestate.hands[prev_order[0]], self.gamestate.hands[prev_order[-1]])
        default_trade(self.gamestate.hands[prev_order[0]], self.gamestate.hands[prev_order[-1]])

        # 2nd and 2nd to last trade 2 times
        default_trade(self.gamestate.hands[prev_order[1]], self.gamestate.hands[prev_order[-2]])
        default_trade(self.gamestate.hands[prev_order[1]], self.gamestate.hands[prev_order[-2]])

        # 3rd and 3rd to last trade once
        default_trade(self.gamestate.hands[prev_order[2]], self.gamestate.hands[prev_order[-3]])

    def setup_round(self, prev_order=None):
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
            self.trade(prev_order)

    def games(self, n_games, n_rounds):
        """
            Simulates a game with the loaded agents for n_rounds rounds.
        """
        player_results = [[] for _ in range(self.n)]
        scores = None
        for g in range(n_games):
            for r in range(n_rounds):
                scores = self.round(scores, r) # each round's setup depends on the previous round's results
                self.gamestate.turn_count = 0
                self.gamestate.rounds_won[self.gamestate.out[0]] += 1
                self.gamestate.play_order = self.gamestate.out
                for i in range(self.n):
                    player_results[scores[i]].append(i)

            # save data if any was collected
            for agent in self.agents:
                if isinstance(agent, DataCollectingAgent):
                    self.collected_data += agent.data

        # convert player results to a counter
        nice_results = [Counter(result) for result in player_results]

        return nice_results

    def round(self, prev_order, round):
        """
            Run a single round of play given previous ordering prev_order.
        """
        self.setup_round(prev_order)
        MAX_ITER = 1000
        for i in range(MAX_ITER + 1):
            if i == MAX_ITER:
                print(str(self.gamestate))
                raise ValueError("Max Iter reached")
                return [0] * self.n

            scores = self.turn(round)
            if scores != None: # only get a return value if the round is over.
                # allow the data collecting agents to collect their data
                for i in range(len(self.agents)):
                    agent = self.agents[i]
                    if isinstance(agent, DataCollectingAgent):
                        agent.finish_round(scores.index(i))
                return scores

    def turn(self, round):
        """
            Run a single turn of play for the current player
        """
        view = AgentView(self.gamestate, self.curr_player)
        action = self.agents[self.curr_player].get_action(view)
        if self.play(action) == "Pass":
            self.gamestate.passed[self.curr_player] = True

        if self.draw:
            draw_graphics(round, self.curr_player, action, self.gamestate)

        # test for end of game
        if len(self.gamestate.out) >= self.n - 1: # are all but 1 players out?
            # add the last player to the end of out
            for p in range(self.n):
                if p not in self.gamestate.out:
                    self.gamestate.out.append(p)
                    return self.gamestate.out # final scores is the order of going out

        if all(self.gamestate.passed[i] or i in self.gamestate.out for i in range(self.n)): # all players have passed or out, move play to the last_player to lead.
            self.gamestate.passed = [False] * self.n  # reset passed list
            self.incr_player(self.gamestate.last_player)
            self.gamestate.top_cards = [] # reset top cards

            if self.draw:
                draw_graphics(round, self.curr_player, "WIN", self.gamestate)
            self.gamestate.turn_count += 1
        else: # otherwise, increment player normally
            self.incr_player()

    def play(self, action):
        if isinstance(action, tuple):
            if not set(action) <= set(self.gamestate.hands[self.curr_player].cards): # skip move if the cards aren't in the players hand
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
            self.gamestate.cards_seen += action # mark the cards as seen
            self.gamestate.hands[self.curr_player].remove(action) # remove the cards from that players hand
            if not self.gamestate.hands[self.curr_player]: # is the player's hand now empty...
                self.gamestate.out.append(self.curr_player)
            option = "Not Passed"
        option = "Pass"

        return option