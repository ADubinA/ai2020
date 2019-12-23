from ai import *
import networkx as nx
from tools.print_tools import *
MAX_LEVEL = 3
from tools.tools import *

class AdversarialAgent(LimitedAStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["minmax"] = self._act_minmax
        self.active_state = "minmax"
        self.alpha = -float("infinity")
        self.beta = float("infinity")
        self.score = None
        self.other_agent = None
        self.total_ad_score = None
        self.decision_type = "max"
        self.current_options = []  # a list of agents, where each agent is the rival.
        self.level = -1  # where in the tree the agent is been developed
        self.is_cutoff = False  # is used for graph visualization
    def _act_finished_traversing(self, global_env):
        self.change_state("minmax")

    def set_other_agent(self, other_agent):
        self.other_agent = other_agent

    #literally does nothing. If you're dead, you remain dead.
    def _simulate_terminated(self):
        pass

    def _simulate_traversing(self):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self._simulate_arrival()

    def _simulate_arrival(self):
        self.location = self.destination
        self._actions_for_arriving_at_node()

    def _simulate(self):
        """
        Given an internal state, the agent will simulate one tick in it's environment
        will update it's own active state if needed
        :return: None
        """
        # self.curr_time += 1
        if self.active_state == "traversing":
            self._simulate_traversing()
        if self.active_state == "terminated":
            self._simulate_terminated()

        if self.level % 2 == 0 and self.level != 0:
            self.local_environment.time += 1

    def _calculate_options(self):
        """
        will return a list of all the possible options for agent to do
        :return: Returns a list of updated Environments with the updated action
        """

        options = []
        # if traversing, keep traversing or if terminated, keep terminated
        if self.location != self.destination or self.active_state == "terminated":
            options.append(copy.deepcopy(self))

            if options[-1].active_state == "minmax":
                options[-1].active_state = "traversing"
        else:
            # loop on possible nodes
            options_graph = self.local_environment.get_passable_subgraph(self.curr_time(),
                                                                     keep_nodes=[self.location])[self.location]
            for option_node, option_data in options_graph.items():
                if ((self.curr_time() + option_data["weight"]) >
                        self.local_environment.get_node_deadline(option_node)):
                    continue

                # update a new agent
                options.append(copy.deepcopy(self))
                options[-1].destination = option_node
                options[-1].time_remaining_to_dest = option_data["weight"]

                if options[-1].active_state == "minmax":
                    options[-1].active_state = "traversing"

            # adding the terminate option
            options.append(copy.deepcopy(self))
            options[-1].active_state = "terminated"

        # update the environment for the other agent
        results = []
        for option in options:
            option._simulate()
            other_agent_copy = copy.deepcopy(self.other_agent)
            other_agent_copy.set_environment(option.local_environment)
            other_agent_copy.set_other_agent(option)

            if other_agent_copy.active_state == "minmax":
                other_agent_copy.active_state = "traversing"

            # update the agent in that environment
            results.append(other_agent_copy)

        return results


        # will call simulate here

    def ab_prune(self):
        """
        will prune the current_options variable using alpha beta pruning.
        :return:
        """
        # TODO this
        pass

    def _act_minmax(self, global_env):
        self.other_agent.current_options = []
        self.current_options = []

        optimal_option = self._minmax()
        self._extract_optimal_move(optimal_option, global_env)

        self.print_decision()

        self.other_agent.current_options = []
        self.current_options = []
        self.act(global_env)

    def _minmax(self):
        """
        expand a minmax node, where the node is an agent.
        with prune with current alpha beta values
        :return: the score from the current result of the minmax tree
        """
        # if agent node is a cut off, use heuristics of both agents.
        if self.level == MAX_LEVEL or is_terminated([self, self.other_agent]):
            self._calculate_leaf_node_score()
            return
        self.level += 1

        # calculate all possible actions. If traversing, will keep traversing
        self.current_options = self._calculate_options()
        # alpha beta prune
        self.ab_prune()

        # check every non pruned options
        for option in self.current_options:
            option._minmax()

        # get score (depends on type of class)  is all the children
        optimal_option = self._choose_optimal(self.current_options)
        self.score = optimal_option.other_agent.score
        self.other_agent.score = optimal_option.score
        if self.decision_type == "min":
            self.total_ad_score = self.score - self.other_agent.score
        else:
            self.total_ad_score = self.other_agent.score - self.score



        # extract the optimal movement for self
        return optimal_option

    def _extract_optimal_move(self, optimal_option, global_env):

        # terminate option
        if optimal_option.other_agent.active_state == "terminated":
            self.path = []
            super()._act_finished_traversing(global_env)
            self.change_state("terminated")

        # traversing option
        elif optimal_option.other_agent.active_state == "traversing":
            if self.location != optimal_option.other_agent.destination:
                self.traverse_to_node(optimal_option.other_agent.destination, global_env)
                self.path = [self.location, self.destination]
                self.destination_index = 1
            else:
                self.change_state("terminated")
                self.path =[]

    def _calculate_leaf_node_score(self):
        """
        update the score and others_score values using the heuristics
        :return:
        """
        self.score = self.calc_f()

        self.other_agent.score = self.other_agent.calc_f()
        self.total_ad_score = self.score - self.other_agent.score
        self.is_cutoff = True


    def _choose_optimal(self, option_list):
        """
        will calculate the score given a list of possible scores
        :param option_list: list of agents, as option for choosing
        :return: the proper score, depends on the type of agent and the self.decision_type
        """
        # TODO maybe the score in the other agent is the opposite here
        if self.decision_type == "max":
            return max(option_list, key=lambda x: x.score - x.other_agent.score)
        elif self.decision_type == "min":
            return min(option_list, key=lambda x: -x.score + x.other_agent.score)
        else:
            raise ValueError("unknown decision type")

    def print_decision(self, decision_tree=None, max_level=float("infinity")):
        """
        https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209
        :param decision_tree:
        :param max_level:
        :return:
        """
        # this will print radially the nodes
        G = covert_local_to_global_tree(self)
        pos = hierarchy_pos(G, 0, width=2 * math.pi, xcenter=0)
        # new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}

        node_labels = nx.get_node_attributes(G, 'total_ad_score')

        # print graph
        nx.draw(G, pos=pos, node_size=50, labels=node_labels)

        # print A1 nodes
        a1_node_list = [node for node in G.nodes if G.nodes[node]["name"]=="A1"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=a1_node_list, node_color='blue', node_size=200,  labels=node_labels)
        # print A2 nodes

        a2_node_list = [node for node in G.nodes if G.nodes[node]["name"]=="A2"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=a2_node_list, node_color='green', node_size=200,  labels=node_labels)

        terminated_list = [node for node in G.nodes if G.nodes[node]["active_state"] == "terminated"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=terminated_list, node_color='red', node_size=100,  labels=node_labels)
        # nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs, font_size=8)

        label_printer(G, pos, "location", 1)
        label_printer(G, pos, "other_score", -1)
        label_printer(G, pos, "score", -2.9999)

        # label_printer(G, pos, "location", 2)

        plt.show()

