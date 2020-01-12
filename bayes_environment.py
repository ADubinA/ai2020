from environment import *
from networkx.algorithms.dag import topological_sort
from networkx.algorithms.simple_paths import all_simple_paths

class BayesEnvironment(Environment):
    def __init__(self, file_name):
        super(BayesEnvironment, self).__init__(file_name)
        self.persistence = 0.7


class BayesNetwork:
    def __init__(self):
        self.bayesian_graph = nx.DiGraph()
        # evidence will be of the form "type_name_time": False\True
        # for example: self.evidence["n_1_0"] = False
        self.sample_num = 100
        self.vertex_iter = None

    def _reset_vertex_iter(self):
        self.vertex_iter = topological_sort(self.bayesian_graph)
    #
    # def _get_node_by_hierarchy(self):
    #     return next(self.vertex_iter)

    @staticmethod
    def get_evidence(display_message = True):
        """
        ------------NOTE------------
        Doesn't support nodes that their name include more than a single digit.
        Hence, a node called 12 won't be parsed.
        ------------NOTE------------

        :param display_message:
        :return[List, int], the first element signifying the details of the evidence, the second is the time:
        """
        edge_specifier = None
        vertex_specifier = None
        evidence_input = None
        at_time = -1
        print("Please type evidence:")
        if (display_message):
           print("Use the following format: \"E#num-#num #time\" or \"N#num #time\"")
           print("For example: \"E3-4 2\" to signify the edge between node 3 and node 4 during time 2")
           print("Or \"N1 7\" to signify the vertex N1 at time 7")
        while True:
            number_of_args = 23789
            while number_of_args != 2:
                user_input = input()
                arg_list = user_input.split(" ")
                print(arg_list)
                number_of_args = len(arg_list)
                if (number_of_args != 2):
                    print("Illegal number of arguments. Please try again")
            if not arg_list[1].isdigit() and arg_list[1] < 0:
                print("Illegal time value. Please try again.")
                continue
            at_time = arg_list[1]
            evidence_input = BayesNetwork.parse_first_part_of_evidence_input(arg_list[0])
            if (len(evidence_input)) == 0:
                print("Bad edge/node input. Please try again.")
                continue
            return [evidence_input, at_time]


    @staticmethod
    def parse_first_part_of_evidence_input(evidence_input):
        output_list = []
        evidence_details_list = list(evidence_input)
        if (evidence_details_list[0] == 'E'):
            if len(evidence_details_list) == 4:
                if evidence_details_list[1].isdigit() and evidence_details_list[3].isdigit():
                    output_list.append('E')
                    output_list.append(evidence_details_list[1])
                    output_list.append(evidence_details_list[3])

        elif (evidence_details_list[0] == 'N'):
            if len(evidence_details_list) == 2:
                if evidence_details_list[1].isdigit():
                    output_list.append('N')
                    output_list.append(evidence_details_list[1])
        return output_list


    @staticmethod
    def get_option_from_user(min_number_of_option = 0, number_of_options = 4, message = "Please select an option:"):
        """
        What is the probability that each of the vertices is flooded?
        What is the probability that each of the edges is blocked?
        What is the probability that a certain path (set of edges) is free from blockages? (Note that the distributions of blockages in edges are NOT necessarily independent.)
        :param number_of_options:
        :returns: an integer signifying the option selected
        """
        while True:
            option_selected = input(message)
            if not option_selected.isdigit():
                print("No number argument detected. Please try again")
            option_num = int(option_selected)
            if option_num > number_of_options or option_num < min_number_of_option:
                print("Option number not in range. Please try again")
            return option_num

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
        self._reset_vertex_iter()

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
        :return: a dictionary with 4 probabilities (connected node is flooded) as follow:
            [
            (false,false),
            (true, false),
            (false, true),
            (true, true)
            ]
        """
        edge_prob = 0.6 * 1.0 / env.graph.edges[edge]["weight"]
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

    def sample_bn_node(self, bn_node, current_evidences):
        """
        given the node from th ebn graph and the known facts, will return true or false.
        :param bn_node: node from self.bn_graph
        :param current_evidences: dict of facts with keys as bn nodes and values as true or false
        :return: True or False. will return None if result contradict facts
        """
        # if "n" in bn_node:
        #TODO this
        pass
        return True

    def sample_bn(self, evidences):
        """
        will sample the bn graph in topological order.
        will reset before every run the iterator
        :param evidences: dictionary with bn vertexes names and True\False values
        :return: dictionary of a sampling result. will return an empty sample
        """
        self._reset_vertex_iter()
        current_evidences = dict(evidences)
        samples = {}

        # in topological order, start a random sampling
        for current_vertex in self.vertex_iter:
            samples[current_vertex] = self.sample_bn_node(current_vertex, current_evidences)

            # if sample contradict fact break. else add to evidence dict
            if samples[current_vertex] != current_evidences.get(current_vertex, samples[current_vertex]):
                samples = {}
                break
            else:
                current_evidences[current_vertex] = samples[current_vertex]

        return samples

    def prob_bn_node(self, bn_vertex, evidences):
        """
        will use bayesian sampling on the tree to calculate the probability that
        the vertex condition is true.
        For graph nodes is the probability of been flooded
        For graph edges is the probability of been blocked
        :param bn_vertex: name of the vertex in the bn graph
        :param evidences: evidences that are true always
        :return: (float) the probability
        """

        # init the sample loop
        sample_i = 0
        good_samples = 0  # number of times vertex is indeed flooded
        while sample_i < self.sample_num:

            sample = self.sample_bn(evidences)
            if len(sample) == 0:
                continue

            sample_i += 1
            if sample.get(bn_vertex, False):
                good_samples += 1

        return good_samples/self.sample_num

    def prob_path_not_blocked(self, edge_list, time, evidences):
        """

        will use bayesian sampling on the tree to calculate the probability that
        the
        :param edge_list: a list of edges of the form (i,j) where i,j is a graph name
        :param time: time of calculation
        :param evidences: dict of evidences that are true always. keys are bn_vertex names
        :return:
        """
        # init the sample loop
        sample_i = 0
        edge_list_bn_nodes = [f"e_{edge}_{time}" for edge in edge_list]
        good_samples = 0  # number of times vertex is indeed flooded
        while sample_i < self.sample_num:

            sample = self.sample_bn(evidences)
            if len(sample) == 0:
                continue

            sample_i += 1

            # if one edge is blocked the whole path is blocked
            for bn_edge_vertex in edge_list_bn_nodes:
                if sample[bn_edge_vertex]:
                    continue
            good_samples += 1

        return good_samples / self.sample_num

    def find_best_prob_graph(self, source, target, time, evidences):

        # get all simple paths
        edges_path_lists = []
        nodes_paths_gen = all_simple_paths(self.bayesian_graph, source, target)
        for nodes_path in nodes_paths_gen:

            # convert to a list of edges
            new_path = []
            for i in range(len(nodes_path) - 1):
                new_path.append((nodes_path[i], nodes_path[i+1]))
            edges_path_lists.append(new_path)

        path_probs = []
        for path in edges_path_lists:
            path_probs.append(self.prob_path_not_blocked(path, time, evidences))

        return max(path_probs)
