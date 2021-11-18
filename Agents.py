"""
    This file implements the abstract Agent class,
    and the AgentView objects which captures the available information
    given to an agent to make each decision.
"""
from numpy.lib.function_base import average
from State import AgentView, int_state, int_action_space, int_to_action
from Cards import Deck, Hand, Card
from Cards import all_sets, compute_playable
from q_learn import QLearning
import random
from collections import Counter

zeros = []

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

class DataCollectingAgent(Agent):
    """
            An Agent is initialized with an action_function
            and a selected reward function in [0, 1, 2].
            This agent is meant for data collection during 
            game simulations.
        """
    def __init__(self, action_function, reward_function=0):
        self.action_function = action_function
        self.reward_function = reward_function
        self.data = []
        self.round_data = []
        self.gamma = 0.95
        self.QAgent = None
        if action_function == q_learn_action:
            self.QAgent = QAgent()

    def get_action(self, view):
        """
            Same as Agent's get_action, but accumulates data
        """
        if self.auto_passer(view.top_cards, view.hand):
            return "Pass" # pass turn if no playable cards
        if self.QAgent:
            action = self.action_function(view, self.QAgent.learner)
        else:
            action = self.action_function(view)

        datum = (int_state(view), action) # store data for the future
        self.round_data.append(datum)

        if isinstance(action, int):
            action = int_to_action(action, view)
        if isinstance(action, Card):
            action = (action,)

        return action

    def finish_round(self, placement):
        """
            Finishes the round by calculating the reward and 
            collecting data.
        """
        if not self.round_data:
            return
        r = 0
        if self.reward_function == 0:
            r = self.zero_one_reward(placement)
        elif self.reward_function == 1:
            r = self.backprop_reward(placement)
        else:
            r = self.relative_reward(placement)

        discount = 1
        for i in range(len(self.round_data) - 2, -1, -1):
            s, a = self.round_data[i]

            sp = self.round_data[i + 1][0]
            self.data.append((s, a, r * discount, sp))
            discount *= self.gamma

        self.round_data = []

    def zero_one_reward(self, placement):
        """
            Assigns a reward of 0 if they did not place first.
            Otherwise it assigns a reward of 100.
        """
        r = 0
        if placement == 0:
            r = 100
        return r

    def backprop_reward(self, placement):
        """
            Backprops the rewards for the round
            and adds the data to self.data
        """
        place = (3.5 - placement) / 3.5
        r = place * 10 / len(self.round_data)
        return r

    def relative_reward(self, placement):
        """
            Assigns a reward of 1 if they placed first.
            Otherwise, it returns an increasingly negative
            reward depending upon how badly the agent does.
        """
        r = 0
        if placement == 0:
            r = 1
        else:
            r = float(placement / -7)
        return r


class QAgent(Agent):
    """
        A Q-Agent is initialized and calls creates a
        Q-Learning object and then generates Q.
        This function takes in an AgentView, and returns:
        1. A legal card or list of cards to be played
        2. "Pass"
        Any other input will be interpreted as a pass.
    """
    def __init__(self):
        self.action_function = q_learn_action
        self.learner = QLearning("data/randbase_backprop_100000.p")
        self.learner.q_learn()

    def get_action(self, view):
        """
            Same as Agent's get_action, but handles extra 
            parameter for q_learn_action.
        """
        if self.auto_passer(view.top_cards, view.hand):
            return "Pass" # pass turn if no playable cards
        action = self.action_function(view, self.learner)

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
    """
        Chooses a random action from those available.
    """
    return random.choice(int_action_space(view))

def getter(f):
    return lambda : Agent(f)

def data_getter(f):
    return lambda : DataCollectingAgent(f)

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

def randomized_baseline_action(view):
    """
        50% of the time, uses the baseline action.
        Otherwise, it uses the random action.
    """
    if random.random() <= .5:
        return random_action(view)
    return baseline_action(view)

def heuristic_action(view):
    """
        Chooses an action given the view based on heuristic:
        Keep a high card
    """
    actions = int_action_space(view)
    s = int_state(view)

    if len(actions) == 1:
        return actions[0]
    if not view.top_cards:
        return actions[1]

    r = actions[1] + 1
    score = 0
    for card_rank in {card.rank() for card in view.hand.cards}: # for each unique rank in hand
        if card_rank < r:
            score -= 1
        elif card_rank > r:
            score += 1

    if score >= 0:
        return actions[1]
    return actions[0]

def q_learn_action(view, learner):
    """
        When the number of cards is greater than 4, uses
        baseline action.
        Otherwise, it calls optimal_policy() to select
        the action that maximizes Q for the current state.
    """
    if len(view.hand.cards) >= 5:
        return baseline_action(view)

    s = int_state(view)
    actions = int_action_space(view)
    a = learner.optimal_policy(s, actions)

    # if a == baseline_action(view):
    #     print(view)
    #     print(int_action_space(view))
    #     print(learner.Q[s])
    #     print()
    # print(s)
    zeros.append(len([x for i, x in enumerate(learner.Q[s]) if x == 0 and i in actions])/len(actions))
    print(average(zeros))

    return a