import time
from bayes_environment import *
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

    # env.print_node_data(pos, "people", 1)
    # env.print_node_data(pos, "shelter", 2)
    # env.print_node_data(pos, "deadline", 3)
    env.print_node_data(pos, "flooded", 1)
    env.print_node_data(pos, "flood_prob", 2)

    # draw the rest of the graph
    ax.margins(0.4, 0.4)
    nx.draw(env.graph, pos, with_labels=True, font_weight='bold')

    if not save_dir:
        plt.show()

def display_bn(bn_graph):
    # create figure with title
    fig, ax = plt.subplots()

    # even spaced shell layout
    pos = nx.circular_layout(bn_graph, scale=2)
    pos = {node: node_pos*0.5 for node,node_pos in pos.items()}
    # TODO make layput different, by partition?/ time?

    # draw the rest of the graph
    ax.margins(0.4, 0.4)
    nx.draw(bn_graph, pos, with_labels=True, font_weight='bold', arrowsize=20)
    plt.show()

def main(save_dir, seconds_per_tick, max_tick=1000):

    env = BayesEnvironment(save_dir)
    # display(env, [])
    bn = BayesNetwork()

    bn.get_evidence()
    # bn.construct_bn(env)
    # display_bn(bn.bayesian_graph)

if __name__ == "__main__":
    # Manager = AgentsManager
    main("test/babyzian/probability_graph1.json", 1.55)
