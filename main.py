import time
from environment import Environment
from ai_multi_agent import *
import networkx as nx
import matplotlib.pyplot as plt
from tools.tools import *

def display(env,agents, save_dir=None):
    """                                                                                                                                                                                                                     z
    display the graph current state.
    :param save_dir: path to save the image. If None, will use plt.show()
    :return: None
    """

    # create figure with title
    fig, ax = plt.subplots()
    plt.title("Graph at time: {}".format(env.time))

    # even spaced shell layout
    pos = nx.circular_layout(env.graph, scale=2)
    pos = {node: node_pos*0.5 for node,node_pos in pos.items()}

    for agent in agents:
        agent.get_annotation_box(pos, ax)
    # add the weight labels to the figure
    edge_labels = dict([((u, v,), d['weight']) for u, v, d in env.graph.edges(data=True)])
    nx.draw_networkx_edge_labels(env.graph, pos,
                                 edge_labels=edge_labels,
                                 node_size=100,
                                 label_pos=0.3)

    env.print_node_data(pos, "people", 1)
    env.print_node_data(pos, "shelter", 2)
    env.print_node_data(pos, "deadline", 3)

    # draw the rest of the graph
    ax.margins(0.4, 0.4)
    nx.draw(env.graph, pos, with_labels=True, font_weight='bold')

    if not save_dir:
        plt.show()

def main(save_dir, seconds_per_tick, max_tick=1000):

    env = Environment(save_dir)

    agents = [AdversarialAgent("A1", 0),
              AdversarialAgent("A2", 2)]


    # agents[0].decision_type = "min"
    # agents[1].decision_type = "max"
    # update the world for every agent at startup
    for agent in agents:
        agent.set_environment(env)
    iteration = 0
    while iteration < max_tick:
        display(env, agents)
        # asd = input()
        if is_terminated(agents):
            break

        for i in range(len(agents)):
            manager = Manager([agents[i], agents[not i]])
            actions_to_perform = manager.starting_minmax()
            agents[i].act(env)
            agents[0].set_environment(env)
            agents[1].set_environment(env)
        # update the world for every agent

        env.tick()
        for agent in agents:
            agent.set_environment(env)

        time.sleep(seconds_per_tick)
        iteration += 1
    for agent in agents:
        print(f"agent {agent.name} has score {agent.score}")
    display(env, agents)


if __name__ == "__main__":
    Manager = CoopManager
    main("test/adv/semi-Coop-Graph.json", 0.55)
