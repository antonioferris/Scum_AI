from ScumController import ScumController
from Agents import get_random_agent, get_baseline_agent, Agent, heuristic_action
from graphics import quit_pygame
import sys
from State import test_state

def test_agent_against(agent, opponent_func, n_rounds, n_agents=7, draw=False, tick_speed=3):
    agents = [agent] + [opponent_func() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.game(n_rounds)
    return results

def display_results(results):
    for p in range(len(results)):
        print(f"Player {p}: {results[p][0]} Wins")


def main(draw, tick_speed):
    test_state()
    a = Agent(heuristic_action)
    n_rounds = 100
    r1 = test_agent_against(a, get_random_agent, n_rounds, 7, draw=draw, tick_speed=tick_speed)
    r2 = test_agent_against(a, get_baseline_agent, n_rounds, 7, draw=draw, tick_speed=tick_speed)
    print(f"Against random opponents, heuristic agent won {r1[0][0]} / {n_rounds} rounds")
    print(f"Against baseline opponents, heuristic agent won {r2[0][0]} / {n_rounds} rounds")

# to run with graphics and control tick speed, call "python Scum.py -d <a number from 1 - 5>"
if __name__ == "__main__":
    draw = "-d" in sys.argv
    tick_speed = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    main(draw, tick_speed)
    quit_pygame()