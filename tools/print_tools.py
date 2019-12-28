import networkx as nx
import random
import math
import matplotlib.pyplot as plt


def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''

    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children)!=0:
            dx = width/len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap,
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def covert_local_to_global_tree(root):
    """
    Given an agent will return a proper networkx decision tree
    :param root: the root of the tree, aka the agent to begin in
    :return: networkx tree
    """

    # start the heap and set the graph with a root of root
    raise  NotImplemented("dont use this function, it's for the old code")
    heap = [(0, root)]
    G = nx.Graph()
    G.add_node(0, score=root.temp_score, other_score=root.other_agent.temp_score,total_ad_score=root.temp_score,
               name=root.name, alpha=root.alpha, beta=root.beta, location=root.location,
               level=root.level, active_state=root.active_state)

    # loop until the heap is empty
    node_index = 1
    while len(heap) != 0:
        parent_index, parent = heap.pop()

        # for every agent check if it's not a leaf add children to heap
        for child in parent.current_options:
            if not child.is_cutoff:
                heap.append((node_index, child))

            # add the kid to the tree
            score_msg_preformat = "{}:{}"
            score_msg = score_msg_preformat.format(child.name, child.temp_score)
            G.add_node(node_index, score=score_msg, other_score=child.other_agent.temp_score
                       , total_ad_score=child.total_ad_score,
                       name=child.name, alpha=child.alpha, beta=child.beta,
                       location=child.location, level=child.level, active_state=child.active_state)
            G.add_edge(parent_index, node_index)
            node_index += 1

    return G


DEBUG = True
RATIO = 3


def print_decision_tree(tree):
    """
    will print the tree for the use of AgentsManager
    """

    G = tree

    for node in G.nodes:
        G.nodes[node]["de_score"] = G.nodes[node]["agents"][G.nodes[node]["level"] % 2].inner_score
        G.nodes[node]["de_state"] = G.nodes[node]["agents"][G.nodes[node]["level"] % 2].active_state
        G.nodes[node]["otr_score"] = G.nodes[node]["agents"][1].inner_score
        G.nodes[node]["loc"] = G.nodes[node]["agents"][G.nodes[node]["level"] % 2].location
        G.nodes[node]["dest"] = G.nodes[node]["agents"][G.nodes[node]["level"] % 2].destination


    pos = hierarchy_pos(G, 0, width=RATIO * math.pi, xcenter=0)
    # new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}


    # print graph
    node_number_size = 0
    if DEBUG:
        node_number_size = 12
    nx.draw(G, pos=pos, node_size=10, labels=None, font_size=node_number_size)

    # print A1 nodes
    a1_node_list = [node for node in G.nodes if G.nodes[node]["level"] % 2 == 0]
    nx.draw_networkx_nodes(G, pos=pos, nodelist=a1_node_list, node_color='blue',
                           node_size=50, labels=None, font_size=1)
    # print A2 nodes

    a2_node_list = [node for node in G.nodes if G.nodes[node]["level"] % 2 == 1]
    nx.draw_networkx_nodes(G, pos=pos, nodelist=a2_node_list, node_color='green', node_size=50,
                           labels=None, font_size=1)

    terminated_list = [node for node in G.nodes if
                       G.nodes[node]["agents"][G.nodes[node]["level"] % 2].active_state == "terminated"]
    nx.draw_networkx_nodes(G, pos=pos, nodelist=terminated_list, node_color='red', node_size=25,
                           labels=None, font_size=1)
    # nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs, font_size=8)

    label_printer(G, pos, "de_score", -RATIO*2)
    label_printer(G, pos, "otr_score", -RATIO)
    label_printer(G, pos, "opt_child_score", 0)
    label_printer(G, pos, "optimal_child", RATIO)
    label_printer(G, pos, "dest", RATIO*2)
    label_printer(G, pos, "loc", RATIO*3)
    label_printer(G, pos, "level", RATIO * 4)


    # label_printer(G, pos, "location", 2)

    decider = tree.nodes[0]["agents"][0]
    plt.title("Current decider is {}".format(decider))
    plt.show()

def label_printer(G, pos, dict_key, spacing=1):
    pos_attrs = {}
    for node, coords in pos.items():
        pos_attrs[node] = (coords[0], coords[1] + spacing * 0.005)

    node_labels = nx.get_node_attributes(G, dict_key)
    custom_node_attrs = {}
    for node, attr in node_labels.items():
        custom_node_attrs[node] = str(dict_key) + ": " + str(attr)

    nx.draw_networkx_labels(G, pos_attrs, labels=custom_node_attrs, font_size=RATIO*1.7)