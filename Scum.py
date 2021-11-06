from ScumController import ScumController
from Agents import get_random_agent, Agent, baseline_action
from graphics import quit_pygame
import sys

def test_random_agents(n_agents, n_rounds, draw, tick_speed):
    agents = [Agent(baseline_action)] + [get_random_agent() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=draw, tick_speed=tick_speed)
    results = controller.game(n_rounds)
    print(results)


def main(draw, tick_speed):
    test_random_agents(6, 3, draw, tick_speed)

# to run with graphics and control tick speed, call "python Scum.py -d <a number from 1 - 5>"
if __name__ == "__main__":
    draw = "-d" in sys.argv
    tick_speed = 3 if len(sys.argv) <= 2 else int(sys.argv[2])
    main(draw, tick_speed)
    quit_pygame()