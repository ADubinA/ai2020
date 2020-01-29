from ai import *
import networkx as nx
import itertools
from tools.print_tools import *
MAX_LEVEL = 8
DEBUG = True
# DEBUG = False
from tools.tools import *
from itertools import count
from networkx import DiGraph


class PomdpAgent(LimitedAStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["traversing"] = self._act_traversing
        # TODO Change the initial state
        self.active_state = "traversing"

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self._actions_for_arriving_at_node()

class AgentsManager:

    def __init__(self, agent):
        # nodes in this tree are agents that represent actions
        # are hashable by their entrance index
        # nodes in the tree have 2 types of node_type: "action" and "decision" type.
        self.tree = nx.DiGraph()
        self.agent = agent  # the first agent in the list start first this is a tuple
        self.node_name_gen = count()

    def generate_tree(self):
        """"""
        # init the graph with the first node (agent at starting point)
        self.tree.add_node(next(self.node_name_gen), agent=self.agent,
                           score=None, node_type="action")
        self._rec_generate_tree(0)

    def _rec_generate_tree(self, node_index):
        print("if you see this twice, dont.")
        """
        generate the self.tree that contain all to possible policies.
        this function will not calculate the score for each policy.
        
        :param node_index (int): The index for the node currently evaluated. 
        :return: None
        """
        """ Currently our data structure is a numbered tree where the the data contained
            in each node is the agent, representing the state."""

        # get all world options if there is a probability split
        available_probabalistic_options = self.find_availble_probabalistic_options(node_index)

        # if number of options is greater then 1?, add  split node
        current_agent = self.tree.nodes[node_index]["agent"]
        decision_node_index = next(self.node_name_gen)
        self.tree.add_node(decision_node_index, agent=current_agent, score=None, node_type="decision")
        self.tree.add_edge(node_index, decision_node_index)

        # for every probability split
        for option in available_probabalistic_options:

            # calculate all possible actions for option
            acted_agents = self.find_options(option)

            # add acted agents to tree
            for acted_agent in acted_agents:
                acted_agent_index = next(self.node_name_gen)
                self.tree.add_node(acted_agent_index, agent=acted_agent, score=None, node_type="action")
                self.tree.add_edge(decision_node_index, acted_agent_index)

                # call recursion for each nodes
                self._rec_generate_tree(acted_agent_index)

    # def calculate_nodes_score():

        # sort by topological order and invert it

        # do single value iteration


    # def calculate_optimal_plan():
        # do greedy path on the tree

    def find_availble_probabalistic_options(self, node_index):
        """
        :param node_index: The node from the tree we're deriving options from.
        :return: An array of agents, each contains a deterministic environment
        """
        # get all the neighboring edges
        current_agent = self.tree.nodes[node_index]["agent"]
        available_edges = current_agent.local_environment.graph.edges(node_index)

        # find edges that have probability in them
        probalistic_edges = [edge for edge in available_edges
                             if 1 > current_agent.local_environment.graph.edges[edge].get("flood_prob", 0) > 0]

        # get all possible true false combination
        combo_list = list(itertools.product([False, True], repeat=len(probalistic_edges)))

        # create all possible environment
        new_agent_list = []
        for combo in combo_list:
            new_agent = copy.deepcopy(current_agent)

            # set values of every option
            for i in range(len(probalistic_edges)):
                new_agent.local_environment.graph.edges[probalistic_edges[i]]["blocked"] = combo[i]

            new_agent_list.append(new_agent)
        return new_agent_list

    def attach_agents_to_nodes(self, agents_tuple, parent, level):
        # TODO this
        pass

    def _calculate_leaf_node_score(self, node):
        """
        calculate the node score using the heuristics
        """
        # TODO this
        pass

    def _update_parent(self, parent, optimal_child, optimal_score):
        """
        updates parent's score using the optimal child
        will updates the parent optimal_child field.
        """
        # TODO this
        pass

    def _get_optimal_child(self, parent):
        """
        from a parent will calculate the optimal child
        optimality is determined by the level ( and game type)
        returns the optimal child and the score used to calculate it's optimality
        """
        # TODO this
        pass

    def _generate_child_node(self, parent, acted_agent):
        """
        Copies the environment from new_agent to old one.
        Refers to A1' and A2 or A2' and A1
        Returns (A1', A2') Where A#' is the updated agent.
        """
        parent_agents = self.tree.nodes[parent]["agents"]
        child_agents = copy.deepcopy(parent_agents)

        for i in range(len(child_agents)):
            child_agents[i].set_environment(acted_agent.local_environment)
            if child_agents[i].name == acted_agent.name:
                child_agents[i] = acted_agent

        return child_agents

    def find_options(self, agent):
        """
        for a given agent will return all possible actions for the agent
        will return an array of copies of the given agent, after preforming the action.

        """
        # TODO this
        raise NotImplemented("AENVKLADFVNADFVLNADFVKLADFNV")
        available_options = []

        if agent.active_state == "traversing":
            if agent.location != agent.destination:
                available_options.append(self._option_keep_traversing(agent))

            else:
                available_options = self._option_arriving_at_destination(agent)
                available_options.append(self._option_now_terminating(agent))

        elif agent.active_state == "terminated":
            available_options.append(self._option_keep_terminated(agent))

        # TODO make sure that after terminated, returns NONE
        return available_options

    def _simulate_options(self, options):
        """
        options is a list of agents
        will simulate one tick for each of them and return them
        """
        # TODO this
        raise NotImplemented("")
        for option in options:
            if option.active_state == "traversing":
                self._simulate_traversing(option)
            if option.active_state == "terminated":
                self._simulate_terminated(option)

        return options

    def _simulate_traversing(self, option):
        option.time_remaining_to_dest -= 1
        if option.time_remaining_to_dest <= 0:
            self._simulate_arrival(option)

    def _simulate_arrival(self, option):
        option.location = option.destination
        option._actions_for_arriving_at_node()

    def _simulate_terminated(self, option):
        pass

    def _option_keep_traversing(self, agent):
        new_agent = copy.deepcopy(agent)
        return new_agent

    def _option_keep_terminated(self, agent):
        new_agent = copy.deepcopy(agent)
        return new_agent

    def _option_now_terminating(self, agent):
        new_dead_agent = copy.deepcopy(agent)
        new_dead_agent.active_state = "terminated"
        return new_dead_agent

    def _option_arriving_at_destination(self, agent):
        possible_destinations = []
        # loop on possible nodes
        options_graph = agent.local_environment.get_passable_subgraph(agent.curr_time(),
                                                                     keep_nodes=[agent.location])[agent.location]
        for option_node, option_data in options_graph.items():
            if ((agent.curr_time() + option_data["weight"]) >
                    agent.local_environment.get_node_deadline(option_node)):
                continue
            # update a new agent
            new_agent = copy.deepcopy(agent)
            new_agent.destination = option_node
            new_agent.time_remaining_to_dest = option_data["weight"]
            possible_destinations.append(new_agent)
        return possible_destinations
