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
import pandas as pd

import matplotlib.pyplot as plt

def test_agent_against(agent, opponent_func, n_games, n_rounds, n_agents=7, draw=False, tick_speed=3):
    """
        Tests a given agent against a given type of opponent.
    """
    agents = [agent] + [opponent_func() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.games(n_games, n_rounds)
    return interpret_results(results, display=False)

def self_play(agents, n_games, n_rounds, draw=False, tick_speed=3):
    """
        Simulated play among the given agents.
    """
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.games(n_games, n_rounds)
    return interpret_results(results, display=False)

def interpret_results(results, display=True, agent=0):
    """
        Outputs the placement and win rate nicely.
    """
    n_rounds = sum(cnt for _, cnt in results[agent].items())
    avg_placement = sum((placement + 1) * cnt for placement, cnt in results[agent].items()) / n_rounds

    return avg_placement, results[0][0] / n_rounds

def test_agent(agent, agentname, n_games, n_rounds, draw=False, tick_speed=3):
    """
        Calls test_agent_against on baseline agents.
    """
    ap1, wr1 = test_agent_against(agent, getter(Agents.baseline_action), n_games, n_rounds, 7, draw=draw, tick_speed=tick_speed)
    # print(f"Against baseline opponents, Agent {agentname} had placement {ap1} and winrate {wr1}")

    return ap1, wr1

def generate_data(n_rounds, draw, tick_speed, reward):
    """
        Generates data by simulating games.
        Saves the results as pickle files to be used by Q-learning.
    """
    baseline_agents = [DataCollectingAgent(Agents.baseline_action, reward) for _ in range(3)]
    heuristic_agents = [DataCollectingAgent(Agents.heuristic_action, reward) for _ in range(2)]
    randbase_agents = [DataCollectingAgent(Agents.randomized_baseline_action, reward) for _ in range(2)]
    q_learn_agents = [DataCollectingAgent(Agents.q_learn_action, reward) for _ in range(1)]
    random_agents = [DataCollectingAgent(Agents.random_action, reward) for _ in range(1)]
    amalgam_agents = baseline_agents+heuristic_agents+randbase_agents

    agents = [DataCollectingAgent(Agents.randomized_baseline_action, 1) for _ in range(7)]
    controller = ScumController(amalgam_agents, draw=draw, tick_speed=tick_speed)
    controller.game(n_rounds)

    with open("data/randbaseheur_backprop_10000.p", "wb") as f:
        pickle.dump(controller.collected_data, f)

    # for testing data pickling
    with open("data/randbaseheur_backprop_10000.p", "rb") as f:
        data = pickle.load(f)

    subset = random.choices(data, k=20)
    print("s, a, r, sp")
    with open("data/randbaseheur_backprop_10000.txt", "a") as f:
        for s, a, r, sp in data:
            # print(f"{s}, {a}, {r:.2f}, {sp}")
            f.write(f"{s}, {a}, {r:.2f}, {sp} \n")

def learn_test(agents):
    selfplay_results = []
    test_results = []
    selfplay_games = 10
    selfplay_rounds = 20
    test_games = 50
    test_rounds = 100
    num_iterations = 100
    t1 = time.time()
    for i in range(num_iterations):
        selfplay_results.append(self_play(agents, selfplay_games, selfplay_rounds))
        test_results.append(test_agent(agents[0], "Q-Learning Agent", test_games, test_rounds))
        print(f"after {i} iterations and {(time.time() - t1):.1f}s runtime, testresults are: {test_results[-1]}", flush=True)


    sp_place = [x[0] for x in selfplay_results]
    sp_wr = [x[1] for x in selfplay_results]
    tr_place = [x[0] for x in test_results]
    tr_wr = [x[1] for x in test_results]

    results_dict = {"Self-play Places":sp_place, "Self-play Win Rate":sp_wr, "Test Results Places":tr_place, "Test Results Win Rate":tr_wr}
    df = pd.DataFrame(results_dict) 
    df.to_csv(r'results\qlearn_results.csv') 

    # pickle.dump(agents[0].get_q(), open("Q/best_randbase_backprop_100000_0.p", "wb"))

    for i in range(len(agents)):
        name = "Q/best_randbase_backprop_100000_" + str(i) + ".p"
        pickle.dump(agents[i].get_q(), open(name, "wb"))

    return selfplay_results, test_results


def final_tournament(draw, tick_speed):
    """
        Generates data by simulating games.
        Saves the results as pickle files to be used by Q-learning.
    """
    random_agent = Agent(Agents.random_action)
    baseline_agent = Agent(Agents.baseline_action)
    heuristic_agent = Agent(Agents.heuristic_action)
    q_learn_agent = QAgent("data/randbase_backprop_100000.p")

    agents_old = pickle.load(open("dump_param_v3_14.p", "rb"))
    param_agent = ParamAgent()
    param_agent.param_model = agents_old[0].param_model

    agents = [random_agent, baseline_agent, heuristic_agent, q_learn_agent, param_agent]

    final_games = 50
    final_rounds = 100
    num_iterations = 100
    agent_results = [[],[],[],[],[]]
    ind_results = [[],[],[],[],[]]
    moving_avg = [0, 0, 0, 0, 0]
    count = 1
    t1 = time.time()
    for i in range(num_iterations):
        controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
        results = controller.games(final_games, final_rounds)
        for k in range(len(agents)):
            ap, _ = interpret_results(results, display=False, agent=k)
            agent_results[k].append(ap)
            ind_results[k] += results[k]
            avg_placement = sum((placement + 1) * cnt for placement, cnt in ind_results[k].items()) / final_rounds*count
            moving_avg[k] = avg_placement

        print(f"It has been {i} iterations with {(time.time() - t1):.1f}s runtime with moving average {moving_avg}", flush=True)


    results_dict = {"Random Placement":agent_results[0], "Baseline Placement":agent_results[1], 
                    "Heuristic Placement":agent_results[2], "Q-Learning Placement":agent_results[3], "Parameter Learning Placement":agent_results[4]}
    df = pd.DataFrame(results_dict) 
    df.to_csv('results/tournament_results.csv') 




def main(draw, tick_speed):
    test_state()
    # a = QAgent(r"data\randbase_backprop_100000.p")
    # b = Agent(Agents.heuristic_action)
    # c = Agent(Agents.baseline_action)
    # d = Agent(Agents.randomized_baseline_action)
    # e = ParamAgent()
    # n_rounds = 100
    # n_games = 50
    # t1 = time.time()
    # ap, wr = test_agent(a, "Q Agent", n_rounds, n_games, draw, tick_speed)
    # print(f"{(time.time() - t1)}s runtime")
    # print("AVERAGE PLACE: ", ap)
    # print("AVERAGE WIN RATE: ", wr)
    
    # pickle.dump(a.get_q(), open("Q/q_randbase_100_50.p", "wb"))

    # test_games = 10
    # test_rounds = 15
    # num_iterations = 100
    # test_results = []
    # t1 = time.time()
    # for i in range(num_iterations):
    #     test_results.append(test_agent(a, "Q-Learning Agent 6", test_games, test_rounds))
    #     print(f"after {i} iterations and {(time.time() - t1):.1f}s runtime, testresults are: {test_results[-1]}", flush=True)

    # tr_place = [x[0] for x in test_results]
    # tr_wr = [x[1] for x in test_results]

    # results_dict = {"Test Results Places":tr_place, "Test Results Win Rate":tr_wr}
    # df = pd.DataFrame(results_dict) 
    # df.to_csv(r'results\qlearn_results_6.csv') 

    # agents = [QAgent("data/randbase_backprop_100000.p") for _ in range(7)]
    # learn_test(agents)

    final_tournament(draw, tick_speed)



# to run with graphics and control tick speed, call "python Scum.py -d <a number from 1 - 5>"
if __name__ == "__main__":
    draw = "-d" in sys.argv
    tick_speed = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    if "-g" in sys.argv:
        generate_data(100000, draw, tick_speed, 1)
    else:
        main(draw, tick_speed)
        quit_pygame()