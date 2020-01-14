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
    nx.draw(bn_graph, pos, with_labels=True, font_weight='bold', arrowsize=20, font_size=8 )
    plt.show()

def printer():
    print("Hello fellow BNer,")
    print("for adding evidence do as follow:")
    print("for edges ")
    print("f(1,3): true")
    print("for nodes ")
    print("f4: true")
    print("for querys:")
    print("n4t0")
    print("e1,4t1")
    print("p1,4,3,3t1")
    print("b1,4t0")


def main(save_dir, seconds_per_tick, max_tick=1000):

    env = BayesEnvironment(save_dir)
    display(env, [])

    bn = BayesNetwork()
    bn.construct_bn(env)
    # display_bn(bn.bayesian_graph)
    # print(bn.prob_bn_node("e_(2, 3)_0", {}))
    # print(bn.prob_path_not_blocked([(1, 2), (2, 4), (4,3)], 0, {}))
    bn.user_input()
    # print(bn.find_best_prob_graph(env, 1, 4, 0, {"e_(3, 4)_0": False}))# TODO this bug
    # bn.get_evidence()

if __name__ == "__main__":
    # Manager = AgentsManager
    main("test/babyzian/probability_graph1.json", 1.55)
