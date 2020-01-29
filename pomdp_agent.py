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
import random

class PomdpAgent(LimitedAStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["traversing"] = self._act_traversing
        # TODO Change the initial state
        self.active_state = "traversing"

    def move_agent_to_location(self, new_location):
        self.local_environment.time += self.local_environment.graph.edges(self.location, new_location)["weight"]
        self.location = new_location
        self.action_in_new_location()


    def action_in_new_location(self):
        """
        Updates the environment and the agent based on it's current location.
        :return None:
        """
        current_node = self.local_environment.graph.nodes[self.location]
        self.carry_num += current_node["people"]
        current_node["people"] = 0
        if current_node["shelter"]:
            self.people_saved += self.carry_num
            self.carry_num = 0

    def observe_immediate_blockages(self):
        """
        When in a given location, the agent will check if any of edges adjacent to it's current location
        are probabalistic. If any of them are, randomize a result and update the environment.
        :return:
        """
        neighboring_edges = self.local_environment.edges(self.location)
        for edge in neighboring_edges:
            random_number = random.uniform(0, 1)
            blockage_probability = self.local_environment.edges[edge]["blocked_prob"]
            self.local_environment.edges[edge]["blocked"] = random_number < blockage_probability



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
        print("if you see this twice, dont.")
        # init the graph with the first node (agent at starting point)
        self.tree.add_node(next(self.node_name_gen), agent=self.agent,
                           score=None, node_type="action")
        self._rec_generate_tree(0)
        self._calculate_nodes_score()
        print_pomdp_tree(self.tree)

    def _rec_generate_tree(self, node_index):

        """
        generate the self.tree that contain all to possible policies.
        this function will not calculate the score for each policy.
        
        :param node_index (int): The index for the node currently evaluated. 
        :return: None
        """
        """ Currently our data structure is a numbered tree where the the data contained
            in each node is the agent, representing the state."""

        # get all world options if there is a probability split
        available_probabalistic_options, probs = self.find_availble_probabalistic_options(node_index)



        # for every probability split
        for i in range(len(available_probabalistic_options)):
            # if number of options is greater then 1?, add  split node
            current_agent = self.tree.nodes[node_index]["agent"]
            decision_node_index = next(self.node_name_gen)
            self.tree.add_node(decision_node_index, agent=current_agent, score=None, node_type="decision")
            self.tree.add_edge(node_index, decision_node_index, prob=probs[i])

            # calculate all possible actions for option
            acted_agents = self.find_options(available_probabalistic_options[i])

            # add acted agents to tree
            for acted_agent in acted_agents:
                acted_agent_index = next(self.node_name_gen)
                self.tree.add_node(acted_agent_index, agent=acted_agent, score=None, node_type="action")
                self.tree.add_edge(decision_node_index, acted_agent_index)

                # call recursion for each nodes
                self._rec_generate_tree(acted_agent_index)

    def calculate_state_prob(self,edge_dict):
        """
        givin a dict of "state" will return the probability of the state
        :param edge_dict: dictionary where keys are edges and values are True or False
                          given by the state.
        :return: (float) the probability
        """
        prob = 1
        for edge, is_blocked in edge_dict.items():
            edge_prob = self.agent.local_environment.graph.edges[edge]["blocked_prob"]

            if not is_blocked:
                edge_prob = 1-edge_prob

            prob *= edge_prob
        return prob

    def _calculate_nodes_score(self):

        # sort by topological order and invert it
        reversed_topo_node_list = list(reversed(list(nx.topological_sort(self.tree))))
        for node_index in reversed_topo_node_list:
            current_node = self.tree.nodes[node_index]

            # if leaf calculate results
            if self.tree.out_degree(node_index) == 0:
                current_node["score"] = current_node["agent"].people_saved

            # if node is a max node:
            elif current_node["node_type"] == "decision":
                children = list(self.tree.neighbors(node_index))
                current_node["score"] = max([self.tree.nodes[child]["score"] for child in children])

            # if node is probability
            else:
                children = list(self.tree.neighbors(node_index))
                score = 0
                for child in children:
                    score += self.tree.edges[(node_index, child)]["prob"] * self.tree.nodes[child]["score"]
                current_node["score"] = score




        # do single value iteration


    def _calculate_optimal_plan(self):
        pass
        # do greedy path on the tree

    def find_availble_probabalistic_options(self, node_index):
        """
        :param node_index: The node from the tree we're deriving options from.
        :return: An array of agents, each contains a deterministic environment
        """
        # get all the neighboring edges
        current_agent = self.tree.nodes[node_index]["agent"]
        available_edges = current_agent.local_environment.graph.edges(current_agent.location)

        # find edges that have probability in them
        probalistic_edges = [edge for edge in available_edges
                             if 1 > current_agent.local_environment.graph.edges[edge].get("blocked_prob", 0) > 0]

        # get all possible true false combination
        combo_list = list(itertools.product([False, True], repeat=len(probalistic_edges)))

        # create all possible environment
        new_agent_list = []
        prob_list = []
        for combo in combo_list:
            new_agent = copy.deepcopy(current_agent)

            # Calculate the probability of the state
            edge_dict = {}
            for i in range(len(probalistic_edges)):
                edge_dict[probalistic_edges[i]] = combo[i]
            prob_list.append(self.calculate_state_prob(edge_dict))

                # set values of every option
            for i in range(len(probalistic_edges)):
                new_agent.local_environment.graph.edges[probalistic_edges[i]]["blocked"] = combo[i]
                new_agent.local_environment.graph.edges[probalistic_edges[i]]["blocked_prob"] = combo[i]

            new_agent_list.append(new_agent)
        return new_agent_list, prob_list

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
        will return an array of copies of the given agent, after performing the action.

        """

        # In case the agent is dead, return nothing.
        if agent.active_state == "terminated":
            return []

        available_options = []

        #Get all accessable neighbhors.
        local_neighborhood = agent.local_environment.get_node_neighborhood(agent.location)

        for neighbor in local_neighborhood:
            #Means the deadline is breached at a certain node.
            dest_deadline = agent.local_environment.get_node_deadline(neighbor)
            curr_time = agent.curr_time()
            traversal_time = agent.local_environment.graph.edges[agent.location, neighbor]["weight"]
            if dest_deadline < curr_time + traversal_time:
                continue #The option is not reachable.

            #The edge to that neighbhor is blocked
            if agent.local_environment.graph.edges[agent.location, neighbor]["blocked"]:
                continue

            #Meaning the deadline isn't breached, time to perform logic.
            new_agent = copy.deepcopy(agent)
            new_environment = copy.deepcopy(agent.local_environment)

            #If people are in the neighbhor, pick them up.
            new_agent.carry_num += new_environment.get_attr(neighbor, "people")  # Pick people up, if they exist.
            new_environment.change_attr(neighbor, "people", 0)

            #If the given node is a shelter, drop people off.
            if new_environment.get_attr(neighbor, "shelter") == True:
                new_agent.people_saved += new_agent.carry_num
                new_agent.carry_num = 0

            #Update the time for the env.
            new_environment.time = curr_time + traversal_time
            new_agent.location = neighbor
            new_agent.set_environment(new_environment)
            available_options.append(new_agent)

        #Simulate termination
        new_agent = copy.deepcopy(agent)
        new_environment = copy.deepcopy(agent.local_environment)
        new_agent.active_state = "terminated"
        new_agent.set_environment(new_environment)
        available_options.append(new_agent)
        return available_options
