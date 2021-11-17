from numpy.lib.function_base import average
from ScumController import ScumController
from Agents import QAgent, getter, Agent, DataCollectingAgent
import Agents
from graphics import quit_pygame
import sys
from State import test_state
import pickle
import random

def test_agent_against(agent, opponent_func, n_rounds, n_agents=7, draw=False, tick_speed=3):
    agents = [agent] + [opponent_func() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.game(n_rounds)
    return interpret_results(results, display=False)

def interpret_results(results, display=True):
    n_rounds = sum(cnt for _, cnt in results[0].items())
    avg_placement = sum((placement + 1) * cnt for placement, cnt in results[0].items()) / n_rounds

    return avg_placement, results[0][0] / n_rounds

def test_agent(agent, agentname, n_rounds, draw, tick_speed):
    # ap1, wr1 = test_agent_against(agent, getter(Agents.random_action), n_rounds, 7, draw=draw, tick_speed=tick_speed)
    # print(f"Against random opponents, Agent {agentname} had placement {ap1} and winrate {wr1}")

    ap2, wr2 = test_agent_against(agent, getter(Agents.baseline_action), n_rounds, 7, draw=draw, tick_speed=tick_speed)
    print(f"Against baseline opponents, Agent {agentname} had placement {ap2} and winrate {wr2}")

    return ap2, wr2

def generate_data(n_rounds, draw, tick_speed):
    agents = [DataCollectingAgent(Agents.heuristic_action) for _ in range(2)] + [DataCollectingAgent(Agents.baseline_action) for _ in range(3)] + [DataCollectingAgent(Agents.q_learn_action) for _ in range(2)]
    # agents = [DataCollectingAgent(Agents.q_learn_action) for _ in range(7)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    controller.game(n_rounds)

<<<<<<< HEAD
    data_path = "data/baseline_100000_01reward.p"

    with open(data_path, "wb") as f:
        pickle.dump(controller.collected_data, f)

    # for testing data pickling
    with open(data_path, "rb") as f:
=======
    with open("data/reward_exp.p", "wb") as f:
        pickle.dump(controller.collected_data, f)

    # for testing data pickling
    with open("data/reward_exp.p", "rb") as f:
>>>>>>> a71c3d3ea7ee1d6ca2608f06ea699f07c5eed62a
        data = pickle.load(f)

    subset = random.choices(data, k=20)
    print("s, a, r, sp")
    for s, a, r, sp in subset:
        print(f"{s}, {a}, {r:.2f}, {sp}")

def main(draw, tick_speed):
    test_state()
    a = QAgent(Agents.q_learn_action)
    b = Agent(Agents.heuristic_action)
    c = Agent(Agents.baseline_action)
    n_rounds = 100
    n_runs = 50
    sum_ap = 0
    sum_wr = 0
    for _ in range(n_runs):
        ap2, wr2 = test_agent(a, "Q-Learning", n_rounds, draw, tick_speed)
        sum_ap += ap2
        sum_wr += wr2
    print("AVERAGE PLACE: ", sum_ap/n_runs)
    print("AVERAGE WIN RATE: ", sum_wr/n_runs)
    # test_agent(b, "Heuristic", n_rounds, draw, tick_speed)
<<<<<<< HEAD
    generate_data(100000, draw, tick_speed)
=======
    # generate_data(100, draw, tick_speed)
>>>>>>> a71c3d3ea7ee1d6ca2608f06ea699f07c5eed62a



# to run with graphics and control tick speed, call "python Scum.py -d <a number from 1 - 5>"
if __name__ == "__main__":
    draw = "-d" in sys.argv
    tick_speed = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    if "-g" in sys.argv:
        generate_data(10000, draw, tick_speed)
    else:
        main(draw, tick_speed)
        quit_pygame()