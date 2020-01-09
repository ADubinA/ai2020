from environment import *

class BayesEnvironment(Environment):
    def __init__(self, file_name):
        super(BayesEnvironment, self).__init__(file_name)
        self.persistence = 0.7

class BayesNetwork:
    def __init__(self):
        self.bayesian_graph = nx.DiGraph()


    def construct_bn(self, env):
        """
        construct the bayes network without computing the conditional probabilities
        vertices in the bn will be named with the format (type_name_time)
        :param env the environment ( will do at time 0 and 1)
        :return: None
        """
        # will add every node from the env graph to a vertex in the bn
        for node in env.graph.nodes:
            bn_name_zero = f"n_{node}_0" #
            bn_name_one = f"n_{node}_1"

            self.bayesian_graph.add_node(bn_name_zero)
            self.bayesian_graph.add_node(bn_name_one)
            self.bayesian_graph.add_edge(bn_name_zero, bn_name_one)

        # add edges at time = 0
        for time in [0, 1]:
            for edge in env.graph.edges:
                bn_edge_name = f"e_{edge}_{time}"
                bn_edge_parent1 = f"n_{edge[0]}_{time}"
                bn_edge_parent2 = f"n_{edge[1]}_{time}"

                self.bayesian_graph.add_node(bn_edge_name)
                self.bayesian_graph.add_edge(bn_edge_parent1, bn_edge_name)
                self.bayesian_graph.add_edge(bn_edge_parent2, bn_edge_name)

        self._calculate_conditional(env)

    def _calculate_conditional(self, env):
        """
        Will calculate the conditional probabilities for the graph
        :param env: the environment
        :return: None
        """
        for node in env.graph.nodes:
            for time in [0, 1]:
                bn_node_name = f"n_{node}_{time}"
                self.bayesian_graph.nodes[bn_node_name]["prob"] =\
                    self._init_prob_vertex(node, env, time)

        for edge in env.graph.edges:
            for time in [0, 1]:
                bn_node_name = f"e_{edge}_{time}"
                self.bayesian_graph.nodes[bn_node_name]["prob"] =\
                    self._init_prob_edge(edge, env, time)


    def _init_prob_edge(self, edge, env, time):
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
        edge_prob = 0.6 * 1 / env.graph.edges[edge]["weight"]
        return [
            0.001,
            edge_prob,
            edge_prob,
            1 - pow(1-edge_prob, 2)
        ]

    def _init_prob_vertex(self, vertex, env, time):
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
        if time == 0:
            return env.graph.nodes[vertex]["flood_prob"]
        elif time > 0:
            return [  # previous was false, previous was true
                env.graph.nodes[vertex]["flood_prob"],
                env.persistence
            ]
        else:
            raise ValueError("NO")

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
