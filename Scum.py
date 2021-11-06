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
from Agents import Agent, AgentView, get_random_agent
from collections import Counter
import random
import pygame
import time


# Margins
MARGIN_LEFT = 230
MARGIN_TOP = 150

# WINDOW SIZE
WIDTH = 1750
HEIGHT = 1000

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (38, 150, 37)
DARK_GREEN = (10, 90, 7)
RED = (203, 16, 16)
BLUE = (44, 109, 238)

pygame.init()

# Setting up the screen and background
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(GREEN)

# Setting up caption
pygame.display.set_caption("Scum")

# Types of fonts to be used
small_font = pygame.font.Font(None, 32)
large_font = pygame.font.Font(None, 50)

pygame.display.update()

class GameState:
    def __init__(self, n, names):
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
    def __init__(self, agents, names=None):
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

        # emergency_jump = 0
        # while self.curr_player in self.gamestate.out or self.gamestate.passed[self.curr_player]: # skip out / passed players
        #     self.curr_player = (self.curr_player + 1) % self.n
        #     emergency_jump += 1
        #     if emergency_jump > 6:
        #         print(str(self.gamestate))
        #         raise ValueError("Emergency Exit")

    def deal_round(self):
        Deck().deal_hands(self.gamestate.hands, self.president)

    def trade(self):
        """
            Initiate trading. For now, this trading is just done automatically.
        """
        default_trade(self.gamestate.hands[self.president], self.gamestate.hands[self.scum])

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
            self.trade()

    def game(self, n_rounds):
        """
            Simulates a game with the loaded agents for n_rounds rounds.
        """
        player_results = [[] for _ in range(self.n)]
        scores = None
        for r in range(n_rounds):
            scores = self.round(scores, r) # each round's setup depends on the previous round's results
            self.gamestate.turn_count = 0
            self.gamestate.rounds_won[self.gamestate.out[0]] += 1
            self.gamestate.play_order = self.gamestate.out
            for i in range(self.n):
                player_results[scores[i]].append(i)

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
                return scores

    def turn(self, round):
        """
            Run a single turn of play for the current player
        """
        view = AgentView(self.gamestate, self.curr_player)
        action = self.agents[self.curr_player].get_action(view)
        if self.play(action) == "Pass":
            self.gamestate.passed[self.curr_player] = True

        self.draw_graphics(round, self.curr_player, action)

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

            self.draw_graphics(round, self.curr_player, "WIN")
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

    def translate_for_graphics(self, action):
        res = []
        for a in action:
            card = str(a)
            num = ""
            suit = ""
            if card[0] not in ['Q', 'K', 'J', '1', 'A']:
                num = card[0]
            elif card[0] == 'Q':
                num = 'queen'
            elif card[0] == 'K':
                num = 'king'
            elif card[0] == 'J':
                num = 'jack'
            else:
                num = 'ace'
            
            if card[1] == 'C':
                suit = 'clubs'
            elif card[1] == 'D':
                suit = 'diamonds'
            elif card[1] == 'S':
                suit = 'spades'
            else:
                suit = 'hearts'
            
            filename = num + "_of_" + suit + ".png"
            res.append(filename)
        return res


    def draw_graphics(self, round, player, action):
        pygame.event.get()

        time_sleep = .25

        # Draw other player's indicator
        pygame.draw.rect(screen, DARK_GREEN, (0,0,WIDTH,350))
        pygame.draw.line(screen, RED, (0, 350), (WIDTH, 350))
        pygame.draw.line(screen, BLACK, (0, 351), (WIDTH, 351))
        pygame.draw.line(screen, BLACK, (0, 352), (WIDTH, 352))
        pygame.draw.line(screen, BLACK, (0, 353), (WIDTH, 353))
        pygame.draw.line(screen, RED, (0, 354), (WIDTH, 354))


        text = small_font.render("Overview of Players", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH//2, 50)
        screen.blit(text, text_rect)

        scum = -1
        if self.gamestate.n - len(self.gamestate.out) == 1:
            for i in range(self.gamestate.n):
                if i not in self.gamestate.out:
                    scum = i
                    time_sleep = 4
                    break
        
        offset = 0
        start = WIDTH//2 - 85 * (self.gamestate.n // 2)
        for i in self.gamestate.play_order:
            c = pygame.image.load(r'./' + 'avatar.jpg')
            c = pygame.transform.scale(c , (75,75))
            screen.blit(c, (start-30+offset, 155))

            num_text = small_font.render(str(i+1), True, BLACK)
            num_text_rect = num_text.get_rect()
            num_text_rect.center = (start+10+offset, 185)
            screen.blit(num_text, num_text_rect)

            play_order_text = small_font.render("Play Order:", True, WHITE)
            play_order_rect = play_order_text.get_rect()
            play_order_rect.center = (start-150, 185)
            screen.blit(play_order_text, play_order_rect)

            rounds_won_text = small_font.render("Rounds Won:", True, WHITE)
            rounds_won_text_rect = rounds_won_text.get_rect()
            rounds_won_text_rect.center = (start-150, 250)
            screen.blit(rounds_won_text, rounds_won_text_rect)

            hands_rem_text = small_font.render("Cards Remaining:", True, WHITE)
            hands_rem_text_rect = hands_rem_text.get_rect()
            hands_rem_text_rect.center = (start-150, 300)
            screen.blit(hands_rem_text, hands_rem_text_rect)

            if i in self.gamestate.out:
                place = large_font.render(str(self.gamestate.out.index(i)+1), True, BLUE)
                place_rect = place.get_rect()
                place_rect.center = (start+10+offset, 135)
                screen.blit(place, place_rect)
            elif scum != -1 and i == scum:
                place = large_font.render(str(len(self.gamestate.out)+1), True, RED)
                place_rect = place.get_rect()
                place_rect.center = (start+10+offset, 135)
                screen.blit(place, place_rect)

            rounds = large_font.render(str(self.gamestate.rounds_won[i]), True, WHITE)
            rounds_rect = rounds.get_rect()
            rounds_rect.center = (start+10+offset, 250)
            screen.blit(rounds, rounds_rect)

            cards = large_font.render(str(len(self.gamestate.hands[i].cards)), True, WHITE)
            cards_rect = rounds.get_rect()
            cards_rect.center = (start+10+offset, 300)
            screen.blit(cards, cards_rect)

            offset+=95

        # Draw the table with cards
        round_text = small_font.render("Round "+str(round+1), True, BLACK)
        round_text_rect = round_text.get_rect()
        round_text_rect.center = (WIDTH//2, HEIGHT//2 - 120)
        screen.blit(round_text, round_text_rect)

        player_text = small_font.render("Player "+str(player+1), True, BLACK)
        player_text_rect = player_text.get_rect()
        player_text_rect.center = (WIDTH//2, HEIGHT//2 - 90)
        screen.blit(player_text, player_text_rect)

        ac = ""
        if action == 'Pass':
            ac = "Passed"
        elif action == "WIN":
            ac = "Won this turn"
            time_sleep = .75
        else:
            ac = ' & '.join([str(a) for a in action])

        hand_text = small_font.render("Action: " + ac, True, BLACK)
        hand_text_rect = hand_text.get_rect()
        hand_text_rect.center = (WIDTH//2, HEIGHT//2 - 60)
        screen.blit(hand_text, hand_text_rect)

        turn_text = small_font.render("Turn: " + str(self.gamestate.turn_count), True, BLACK)
        turn_text_rect = turn_text.get_rect()
        turn_text_rect.center = (WIDTH//2, HEIGHT//2 - 30)
        screen.blit(turn_text, turn_text_rect)

        if action == "Pass" or action == "WIN":
            action = self.gamestate.last_action

        offset = 0
        if action != "Pass":
            start = WIDTH//2 - 115 * (len(action) // 2)
            for file in self.translate_for_graphics(action):
                c = pygame.image.load(r'./cards/' + file)
                c = pygame.transform.scale(c , (100,160))
                screen.blit(c, (start+offset, HEIGHT//2 + 30))
                offset+=120

        self.gamestate.last_action = action


        # Draw Player One's Hand
        pygame.draw.line(screen, RED, (0, 750), (WIDTH, 750))
        pygame.draw.line(screen, BLACK, (0, 751), (WIDTH, 751))
        pygame.draw.line(screen, BLACK, (0, 752), (WIDTH, 752))
        pygame.draw.line(screen, BLACK, (0, 753), (WIDTH, 753))
        pygame.draw.line(screen, RED, (0, 754), (WIDTH, 754))

        pygame.draw.rect(screen, DARK_GREEN, (0,754,WIDTH,1000))

        player_one_text = small_font.render("Player One's Hand: ", True, WHITE)
        player_one_rect = player_one_text.get_rect()
        player_one_rect.center = (WIDTH//2, HEIGHT//2 + 300)
        screen.blit(player_one_text, player_one_rect)

        offset = 0
        start = WIDTH//2 - 75 * (len(self.gamestate.hands[0].cards) // 2)
        for file in self.translate_for_graphics(self.gamestate.hands[0].cards):
            c = pygame.image.load(r'./cards/' + file)
            c = pygame.transform.scale(c , (70,112))
            screen.blit(c, (start+offset, HEIGHT//2 + 350))
            offset+=80


        if player not in self.gamestate.out or scum != -1:
            pygame.display.update()
            time.sleep(time_sleep)
        screen.fill(GREEN)

def test_random_agents(n_agents, n_rounds):
    agents = [get_random_agent() for _ in range(n_agents)]
    controller = ScumController(agents)
    results = controller.game(n_rounds)
    print(results)


def main():
    test_random_agents(5, 1000)

if __name__ == "__main__":
    main()
    pygame.quit()