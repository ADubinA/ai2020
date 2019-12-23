import networkx as nx
import random

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
    heap = [(0, root)]
    G = nx.Graph()
    G.add_node(0, score=root.score, other_score=root.other_agent.score,
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
            G.add_node(node_index, score=child.score, other_score=child.other_agent.score,
                       name=child.name, alpha=child.alpha, beta=child.beta,
                       location=child.location, level=child.level, active_state=child.active_state)
            G.add_edge(parent_index, node_index)
            node_index += 1

    return G


def label_printer(G, pos, dict_key, spacing=1):
    pos_attrs = {}
    for node, coords in pos.items():
        pos_attrs[node] = (coords[0], coords[1] + spacing * 0.03)

    node_labels = nx.get_node_attributes(G, dict_key)
    custom_node_attrs = {}
    for node, attr in node_labels.items():
        custom_node_attrs[node] = str(dict_key) + ": " + str(attr)

    nx.draw_networkx_labels(G, pos_attrs, labels=custom_node_attrs, font_size=8)