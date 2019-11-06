import networkx as nx
import matplotlib.pyplot as plt
import logging
from parser import Parser
from ai import Pc

class Environment:
    def __init__(self, file_name):
        parser_instance = Parser("test_graph.json")
        # here we insert the parser to the vars
        self.graph = nx.Graph()
        self.graph.add_nodes_from(parser_instance.vertex_list)
        self.graph.add_edges_from(parser_instance.edge_list)
        self.attributes = []
        self.agents = [Pc("pc 1",1)] # TODO make this a node not a number
        self.time = 0
        # raise NotImplemented()

    def add_vertex(self, **kwargs):
        """
        Adds a vertex to the environment graph. Will name the vertex with the "name" key that is in data_dict
        if there isn't one, will add a numeric value name to the vertex.
        :param data_dict: (dictionary) the data to be added to the vertex
        :return: None
        """
        vertex_name = kwargs.get("name")
        if not vertex_name:
            vertex_name = self.graph.number_of_nodes() + 1
            kwargs["name"] = vertex_name

        if "deadline" not in kwargs.keys():
            logging.warning("no deadline has been added to the edge {}, will assume weight 10".format(vertex_name))
            kwargs["deadline"] = 2



        self.graph.add_node(vertex_name, **kwargs)

    def add_edge(self, start, end, **kwargs):
        """
        will create an edge between start to end
        :param start: (hashable)  name of the vertex
        :param end: (hashable)    name of the vertex
        :return: None
        """
        if not kwargs.get("weight"):
            logging.warning("no weight has been added to the edge ({},{}), will assume weight 1".format(start,end))
            kwargs["weight"] = 1

        self.graph.add_edge(start, end, **kwargs)

    def tick(self):
        """
        calculate the next turn in the environment
        :return: None
        """

        self._update_environment()

        # update the world for every agent
        for agent in self.agents:
            agent.set_environment(self)

        # each agent act on the world at his turn
        for agent in self.agents:
            agent.act(self)


    def display(self, save_dir=None):
        """
        display the graph current state.
        :param save_dir: path to save the image. If None, will use plt.show()
        :return: None
        """
        # ---------------display parameters--------------------
        color_dict = {

            # players
            'annihilator': 'red',
            'greedy': 'blue',
            'pc': 'yellow',

            # edges
            'passable': 'black',
            'broken': 'red',

            # nodes
            'shelter': 'green',
            'people': 'purple'

        }


        # -----------------------------------------------------

        # create figure with title
        fig, ax = plt.subplots()
        plt.title("Graph at time: {}".format(self.time))

        # even spaced shell layout
        pos = nx.shell_layout(self.graph)

        # add the weight labels to the figure
        edge_labels = dict([((u, v,), d['weight']) for u, v, d in self.graph.edges(data=True)])
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        self._print_node_data(ax, pos, "deadline", 1)

        self._print_agents_data(ax, pos)
        # draw the rest of the graph
        nx.draw(self.graph, pos, with_labels=True, font_weight='bold')


        if not save_dir:
            plt.show()

        # raise NotImplemented()

    def _update_environment(self):
        self.time = self.time + 1
        for node in self.graph.nodes:
            if self.graph.nodes[node]["deadline"] > 0:
                self.graph.nodes[node]["deadline"] -= 1

    def _print_node_data(self, ax, pos, dict_key, spacing):

        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] + spacing*0.08)

        node_attrs = nx.get_node_attributes(self.graph, name=dict_key)
        custom_node_attrs = {}
        for node, attr in node_attrs.items():
            custom_node_attrs[node] = str(dict_key) + ": " + str(attr)

        nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs)

    def _print_agents_data(self, ax, pos):

        for agent in self.agents:
            agent_node = agent.get_current_location()
            # xy = pos[agent_node.name]
            xy = pos[agent_node]
            agent.get_annotation_box(xy, ax)

    def get_node_neighborhood(self, node_key):
        """
        return a list of the neighbors to the node
        :param node_key: (hashable) the key to the node
        :return:
        """
        return self.graph[node_key]

    def save(self, save_dir):
        """
        Save the environment variable to text
        :param save_dir: save location
        :return: (bool) True if success
        """
        raise NotImplemented()

    def load(self, save_dir):
        """
        does what the save function do, but in reverse.
        :param save_dir:
        :return: (bool) True if success
        """

        raise NotImplemented()

    def is_terminated(self):
        """
        will check if all the agents are terminated ;)
        :return: (bool) true if terminated
        """