import networkx as nx
import matplotlib.pyplot as plt


class Environment:
    def __init__(self, file_name):

        # here we insert the parser to the vars

        self.graph = nx.Graph()
        self.attributes = []
        self.agents = []
        self.time = 0
        # raise NotImplemented()

    def add_vertex(self, data_dict={}):
        """
        Adds a vertex to the environment graph. Will name the vertex with the "name" key that is in data_dict
        if there isn't one, will add a numeric value name to the vertex.
        :param data_dict: (dictionary) the data to be added to the vertex
        :return: None
        """
        vertex_name = data_dict.get("name")
        if not vertex_name:
            vertex_name = self.graph.number_of_nodes() + 1

        self.graph.add_node(vertex_name, attr_dict=data_dict)

    def add_edge(self, start, end, data_dict={}):
        """
        will create an edge between start to end
        :param start: (hashable)  name of the vertex
        :param end: (hashable)    name of the vertex
        :return: None
        """
        self.graph.add_edge(start, end, attr_dict=data_dict)

    def tick(self):
        """
        calculate the next turn in the environment
        :return: None
        """

        self.time = self.time + 1
        raise NotImplemented()

    def display(self, save_dir=None):
        """
        display the graph current state.
        :param save_dir: path to save the image. If None, will use plt.show()
        :return: None
        """
        fig = plt.figure()
        plt.title("Graph at time: {}".format(self.time))
        nx.draw(self.graph, with_labels=True, font_weight='bold')

        # nx.draw_shell(, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')

        if not save_dir:
            plt.show()

        # raise NotImplemented()

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