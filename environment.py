import networkx as nx


class Environment:
    def __init__(self, file_name):

        # here we insert the parser to the vars

        self.graph = nx.Graph()
        self.attributes = []
        self.agents = []
        self.time = 0
        raise NotImplemented()

    def add_vertex(self, data_dict):
        """
        Adds a vertex to the environment graph. Will name the vertex with the "name" key that is in data_dict
        if there isn't one, will add a numeric value name to the vertex.
        :param data_dict: (dictionary) the data to be added to the vertex
        :return: None
        """
        raise NotImplemented()

    def add_edge(self, start, end):
        """
        will create an edge between start to end
        :param start: (hashable)  name of the vertex
        :param end: (hashable)    name of the vertex
        :return: None
        """
        raise NotImplemented()

    def tick(self):
        """
        calculate the next turn in the environment
        :return: None
        """
        raise NotImplemented()

    def display(self, save_dir=None):
        """
        display the graph current state.
        :param save_dir: path to save the image. If None, will use plt.show()
        :return: None
        """
        raise NotImplemented()

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