import time
from bayes_environment import *
from pomdp_agent import  *
import networkx as nx
import matplotlib.pyplot as plt


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

    edge_labels = dict([((u, v,), "P:" + str(d['blocked_prob'])) for u, v, d in env.graph.edges(data=True)
                        if 0 < d.get("blocked_prob", 0) < 1])
    nx.draw_networkx_edge_labels(env.graph, pos,
                                 edge_labels=edge_labels,
                                 node_size=100,
                                 label_pos=0.7)

    env.print_node_data(pos, "people", 1)
    env.print_node_data(pos, "shelter", 2)
    env.print_node_data(pos, "deadline", 3)
    # env.print_node_data(pos, "flooded", 1)
    # env.print_node_data(pos, "flood_prob", 2)
    edge_colors = ["red" if env.graph[u][v]['blocked'] else "black" for u,v in env.graph.edges()]
    # draw the rest of the graph
    ax.margins(0.4, 0.4)
    nx.draw(env.graph, pos, with_labels=True, font_weight='bold', edge_color=edge_colors)

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
    agent = PomdpAgent("A1", 1)
    agent.set_environment(env)
    display(env, [agent])
    am = AgentsManager(agent)
    am.generate_tree()
    # am.print_tree()

    done = False
    while not done:
        agent.policy = am.tree
        agent.select_action()
        display(agent.local_environment, [agent])
        am = AgentsManager(agent)
        am.generate_tree()
        done = agent.active_state == "terminated"

    print(f"agent score is {agent.people_saved}")



if __name__ == "__main__":
    # Manager = AgentsManager
    main("test/babyzian/pomdp_graph2.json", 1.55)
