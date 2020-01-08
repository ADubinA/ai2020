from environment import *

class BayesEnvironment(Environment):
    def __init__(self, file_name):
        super(BayesEnvironment, self).__init__(file_name)
        self.persistence = 0.7

class BayesNetwork:
    def __init__(self):
        self.bn = nx.Graph()

    def construct_bn(self, env):
        """
        construct the bayes network without computing the conditional probabilities

        :param env the environment ( will do at time 0 and 1)
        :return: None
        """
        pass

    def calculate_conditional(self, env):
        """
        Will calculate the conditional probabilities for the graph
        :param env: the environment
        :return: None
        """
        pass
    def _init_prob_edge(self, edge, env):
        """
        will calculate the probability that a given edge is blocked,
        conditioned by the nodes
        :param edge: an edge index
        :param env: you know
        :return: an array with 4 probabilities (connected node is flooded) as follow:
            [
            (false,false),
            (true, false),
            (false, true),
            (true, true)
            ]
        """
        pass
    def _init_prob_vertex(self, vertex, env):
        """
        will calculate the probability that a given vertex is flooded,
        conditioned by time
        :param vertex: index of the vertex from the env
        :param env:
        :return: an array with 2 probabilities ( node at time-1 is flooded) as follow:
            [
            P(flooded| previous_flooded == false),
            (true)
            ]
            at time = 0 return the same probability, twice
        """
        pass

    def prob_vertex_flooded(self, vertex, time):
        """
        will use bayesian inference on the tree to calculate the probability that
        at time time, the vertex will be flooded
        :param vertex: vertex index
        :param time: time (0 or 1)
        :return: (float) the probability
        """
        pass

    def prob_edge_blocked(self, edge, time):
        """
        will use bayesian inference on the tree to calculate the probability that
        at time time, the edge will be block

        :param edge: edge index
        :param time: time (0 or 1)
        :return: (float) the probability
        """
        pass

    def prob_path_ok(self, vertex_path):
        pass
