import networkx as nx
import matplotlib.pyplot as plt
import logging
from tools.parser import Parser


class Environment:
    def __init__(self, file_name):
        self.graph = nx.Graph()
        self.people_in_graph = 0
        self.time = 0

        # parser actions
        parser_instance = Parser(file_name)
        for vertex in parser_instance.vertex_list:
            self.add_vertex(**vertex)
            self.people_in_graph += vertex["people"]

        for edge in parser_instance.edge_list:
            self.add_edge(edge["from"], edge["to"], **edge)

        self.attributes = []

        # raise NotImplemented()

    def add_vertex(self, **kwargs):
        """
        Adds a vertex to the environment graph. Will name the vertex with the "name" key that is in data_dict
        if there isn't one, will add a numeric value name to the vertex.
        :param data_dict: (dictionary) the data to be added to the vertex
        :return: None
        """
        vertex_name = kwargs.get("name")
        if vertex_name is None:
            vertex_name = self.graph.number_of_nodes() + 1
            kwargs["name"] = vertex_name

        if "deadline" not in kwargs.keys():
            logging.warning("no deadline has been added to the edge {}, will assume deadline 10".format(vertex_name))
            kwargs["deadline"] = 10



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

    def change_attr(self, node, attr, value):
        """
        change the attribute of the node to the value
        :param node: (hashable) key to the node
        :param attr: (hashable) key to the attribute
        :param value: value to the attribute
        :return: None
        """
        self.graph.nodes[node][attr] = value

    def get_attr(self, node, attr):
        """
        get the attribute of the node to the value
        :param node: (hashable) key to the node
        :param attr: (hashable) key to the attribute
        :return: value to the attribute of the node
        """
        return self.graph.nodes[node][attr]

    def tick(self):
        """
        calculate the next turn in the environment
        :return: None
        """
        # each agent act on the world at his turn
        self._update_environment()

    def get_node_deadline(self, node, after_time=0):
        """
        returns the deadline of the node. this is the only proper way to get the right time of the deadline
        :param node: (hashable) the node wanted
        :param after_time: this function calculate the deadline at self.time.
         after_time will increate the time by this int
        :return: the true deadline
        """
        return max(-1, self.get_attr(node, "deadline") - after_time)

    def get_passable_subgraph(self, after_time=0, keep_nodes=None):
        """
        :at_time: (int) calculate the passable subgraph in the future after at_time ticks
        :return:
        """
        keep_nodes = {} if not keep_nodes else set(keep_nodes)

        non_destroyed_nodes = [node for node in self.graph.nodes if
                               self.get_node_deadline(node, after_time) > 0]

        non_destroyed_nodes = list(set(non_destroyed_nodes).union(keep_nodes))

        subgraph = nx.Graph(nx.subgraph(self.graph, non_destroyed_nodes))
        destroyed_edges = [edge for edge in self.graph.edges if self.graph.edges[edge]["blocked"]]
        subgraph.remove_edges_from(destroyed_edges)
        return subgraph

    def calculate_path_time(self, path):
        """
        calculate the time it takes to move in the given path
        :param path: list of hash nodes
        :return: time it takes
        """
        time = 0
        for node_index in range(len(path) - 1):
            time += self.graph.edges[path[node_index], path[node_index + 1]]["weight"]

        return time

        # raise NotImplemented()

    def _update_environment(self, time=1):
        self.time = self.time + time

    def print_node_data(self, pos, dict_key, spacing):

        # add spacing to text
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] + spacing*0.06)

        # print the wanted attributes
        node_attrs = nx.get_node_attributes(self.graph, name=dict_key)
        custom_node_attrs = {}
        for node, attr in node_attrs.items():
            if dict_key == "deadline":
                attr = self.get_node_deadline(node, self.time)
            custom_node_attrs[node] = str(dict_key) + ": " + str(attr)

        nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs, font_size=8)

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