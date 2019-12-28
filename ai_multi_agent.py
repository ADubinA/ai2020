from ai import *
import networkx as nx
from tools.print_tools import *
MAX_LEVEL = 4
DEBUG = False
from tools.tools import *
from itertools import count
from networkx.algorithms.dag import descendants


class AdversarialAgent(LimitedAStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["traversing"] = self._act_traversing
        # TODO Change the initial state
        self.active_state = "traversing"
        self.inner_score = None # will keep the heuristic score for the decision tree

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self._actions_for_arriving_at_node()

class AgentsManager:

    def __init__(self, agents):
        # nodes in this tree are agents that represent actions
        # are hashable by their entrance index
        self.tree = nx.DiGraph()
        self.agents = agents # the first agent in the list start first this is a tuple
        self.node_name_gen = count()

    def starting_minmax(self):
        node_type = "min"
        level_num = 0
        self.tree.add_node(next(self.node_name_gen), agents=self.agents,
                           decision_type=node_type, optimal_child=None,
                           opt_child_score=None, level=level_num)
        self.minmax_rec(0, level_num)
        if DEBUG:
            print_decision_tree(self.tree)
        actions_to_perform = self.extract_action(self.tree.nodes[0]["optimal_child"])
        self.agents[0].active_state = actions_to_perform["active_state"]
        self.agents[0].destination = actions_to_perform["destination"]
        self.agents[0].time_remaining_to_dest = actions_to_perform["time_to_dest"]
        return actions_to_perform
        # blorg
        # TODO extract action to do in the real world


    def extract_action(self, optimal_child_index):
        """
        Given an optimal child index, it will extract the action that child has taken.
        """
        optimal_agent = self.tree.nodes[optimal_child_index]["agents"][0]
        optimal_agent_actions = {}
        optimal_agent_actions["active_state"] = optimal_agent.active_state
        optimal_agent_actions["destination"] = optimal_agent.destination
        optimal_agent_actions["time_to_dest"] = optimal_agent.time_remaining_to_dest + 1
        return optimal_agent_actions


    def minmax_rec(self, parent, level):
        """
        a recursive function that act on a node on self.tree
        parent is a nx node from the self.tree
        """

        # update time of the environment if needed
        new_env = self._env_updater(parent, level)

        # stop condition and update score TODO maybe add dual terminate as condition
        if level == MAX_LEVEL:
            self._calculate_leaf_node_score(parent)
            return

        # select from the parent node, the acting agent
        acting_agent = self._agent_select(parent, level)
        acting_agent_in_new_env = copy.deepcopy(acting_agent)
        acting_agent_in_new_env.set_environment(new_env)
        # find all children for parent
        options_list = self.find_options(acting_agent_in_new_env)
        acted_agents_list = self._simulate_options(options_list)

        # TODO ab pruning

        # calculate each child for given parent
        for acted_agent in acted_agents_list:
            agents_tuple_post_activation = self._generate_child_node(parent, acted_agent)

            new_child_index = self.attach_agents_to_nodes(agents_tuple_post_activation, parent, level)
            # calls recursion
            self.minmax_rec(new_child_index, level + 1)

        # get optima l child
        optimal_child, optimal_score = self._get_optimal_child(parent)

        # update parent
        self._update_parent(parent, optimal_child, optimal_score)

    def attach_agents_to_nodes(self, agents_tuple, parent, level):
        # adds the child to the tree and change decision_type
        child_index = next(self.node_name_gen)
        current_decision_string = self.tree.nodes[parent]["decision_type"]

        self.tree.add_node(child_index, agents=agents_tuple,
                           decision_type=self.change_decision(current_decision_string),
                           optimal_child=None, opt_child_score=None, level=level)
        self.tree.add_edge(parent, child_index)

        return child_index

    @staticmethod
    def change_decision(decision_string):
        """
        return the proper decision string (min or max) to change after one node
        """
        if decision_string == "min":
            return "max"
        elif decision_string == "max":
            return "min"
        else:
            raise ValueError("unknown decision string")

    def _calculate_leaf_node_score(self, node):
        """
        calculate the node score using the heuristics
        """
        agents_in_node = self.tree.nodes[node]["agents"]
        for agent in agents_in_node:
            agent.inner_score = agent.calc_f()

    def _update_parent(self, parent, optimal_child, optimal_score):
        """
        updates parent's score using the optimal child
        will updates the parent optimal_child field.
        """
        self.tree.nodes[parent]["optimal_child"] = optimal_child
        self.tree.nodes[parent]["opt_child_score"] = optimal_score

        optimal_child_agents = self.tree.nodes[optimal_child]["agents"]
        agents = self.tree.nodes[parent]["agents"]

        agents[0].inner_score = optimal_child_agents[0].inner_score
        agents[1].inner_score = optimal_child_agents[1].inner_score

    def _get_optimal_child(self, parent):
        """
        from a parent will calculate the optimal child
        optimality is determined by the level ( and game type)
        returns the optimal child and the score used to calculate it's optimality
        """
        children = neighbors = self.tree.neighbors(parent)
        if self.tree.nodes[parent]["decision_type"] == "max":
            optimal_index = max(children, key=lambda x: self.optimality_opp(x))
        elif self.tree.nodes[parent]["decision_type"] == "min":
            optimal_index = min(children, key=lambda x: self.optimality_opp(x))
        else:
            raise ValueError()
        return optimal_index, self.optimality_opp(optimal_index)

    def optimality_opp(self, node):
        agents = self.tree.nodes[node]["agents"]
        return agents[0].inner_score - agents[1].inner_score

    def _agent_select(self,node, level):
        """
        select the agent from the node, as a function of the level
        """
        acting_index = level % 2
        return self.tree.nodes[node]["agents"][acting_index]

    def _env_updater(self, node, level):
        """
        updates the environment of the node by one tick.
        will update only when the level is correct (level%2 ==0)
        """
        env = copy.deepcopy(self.tree.nodes[node]["agents"][0].local_environment)
        if level % 2 == 0 and level != 0:
            env.tick()
        return env

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
        available_options = []

        if agent.active_state == "traversing":
            if agent.location != agent.destination:
                available_options.append(self._option_keep_traversing(agent))

            else:
                available_options = self._option_arriving_at_destination(agent)
                available_options.append(self._option_now_terminating(agent))

        elif agent.active_state == "terminated":
            available_options.append(self._option_keep_terminated(agent))

        return available_options

    def _simulate_options(self, options):
        """
        options is a list of agents
        will simulate one tick for each of them and return them
        """
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

    def simulate(self):
        pass
