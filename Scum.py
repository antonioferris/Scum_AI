from ScumController import ScumController
from Agents import get_random_agent, Agent, baseline_action
from graphics import quit_pygame

def test_random_agents(n_agents, n_rounds):
    agents = [Agent(baseline_action)] + [get_random_agent() for _ in range(n_agents-1)]
    controller = ScumController(agents, draw=True)
    results = controller.game(n_rounds)
    print(results)


def main():
    test_random_agents(6, 3)

if __name__ == "__main__":
    main()
    quit_pygame()