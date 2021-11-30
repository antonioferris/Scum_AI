from numpy.lib.function_base import average
from ScumController import ScumController
from Agents import QAgent, ParamAgent, baseline_action, getter, Agent, DataCollectingAgent, heuristic_action
import Agents
from graphics import quit_pygame
import sys
from State import test_state
import pickle
import random
import time

def test_agent_against(agent, opponent_func, n_games, n_rounds, n_agents=7, draw=False, tick_speed=3):
    """
        Tests a given agent against a given type of opponent.
    """
    agents = [agent] + [opponent_func() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.games(n_games, n_rounds)
    return interpret_results(results, display=False)

def interpret_results(results, display=True):
    """
        Outputs the placement and win rate nicely.
    """
    n_rounds = sum(cnt for _, cnt in results[0].items())
    avg_placement = sum((placement + 1) * cnt for placement, cnt in results[0].items()) / n_rounds

    return avg_placement, results[0][0] / n_rounds

def test_agent(agent, agentname, n_games, n_rounds, draw, tick_speed):
    """
        Calls test_agent_against on baseline agents.
    """
    ap1, wr1 = test_agent_against(agent, getter(Agents.baseline_action), n_games, n_rounds, 7, draw=draw, tick_speed=tick_speed)
    print(f"Against baseline opponents, Agent {agentname} had placement {ap1} and winrate {wr1}")

    return ap1, wr1

def generate_data(n_rounds, draw, tick_speed, reward):
    """
        Generates data by simulating games.
        Saves the results as pickle files to be used by Q-learning.
    """
    baseline_agents = [DataCollectingAgent(Agents.baseline_action, reward) for _ in range(2)]
    heuristic_agents = [DataCollectingAgent(Agents.heuristic_action, reward) for _ in range(1)]
    randbase_agents = [DataCollectingAgent(Agents.randomized_baseline_action, reward) for _ in range(2)]
    q_learn_agents = [DataCollectingAgent(Agents.q_learn_action, reward) for _ in range(1)]
    random_agents = [DataCollectingAgent(Agents.random_action, reward) for _ in range(1)]
    amalgam_agents = baseline_agents+heuristic_agents+randbase_agents+q_learn_agents+random_agents

    agents = [DataCollectingAgent(Agents.randomized_baseline_action, 1) for _ in range(7)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    controller.game(n_rounds)

    with open("data/randbase_backprop_100000.p", "wb") as f:
        pickle.dump(controller.collected_data, f)

    # for testing data pickling
    with open("data/randbase_backprop_100000.p", "rb") as f:
        data = pickle.load(f)

    subset = random.choices(data, k=20)
    print("s, a, r, sp")
    with open("data/randbase_backprop_100000.txt", "a") as f:
        for s, a, r, sp in data:
            # print(f"{s}, {a}, {r:.2f}, {sp}")
            f.write(f"{s}, {a}, {r:.2f}, {sp} \n")

def main(draw, tick_speed):
    test_state()
    # a = QAgent()
    b = Agent(Agents.heuristic_action)
    c = Agent(Agents.baseline_action)
    d = Agent(Agents.randomized_baseline_action)
    e = ParamAgent()
    n_rounds = 50
    n_games = 5
    t1 = time.time()
    ap, wr = test_agent(e, "Param Agent", n_rounds, n_games, draw, tick_speed)
    print(f"{(time.time() - t1)}s runtime")
    # print("AVERAGE PLACE: ", ap)
    # print("AVERAGE WIN RATE: ", wr)



# to run with graphics and control tick speed, call "python Scum.py -d <a number from 1 - 5>"
if __name__ == "__main__":
    draw = "-d" in sys.argv
    tick_speed = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    if "-g" in sys.argv:
        generate_data(100000, draw, tick_speed, 1)
    else:
        main(draw, tick_speed)
        quit_pygame()