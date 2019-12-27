from ai import *
import networkx as nx
from tools.print_tools import *
MAX_LEVEL = 2
DEBUG = True
from tools.tools import *
from itertools import count
from networkx.algorithms.dag import descendants


class AdversarialAgent(LimitedAStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        # self.states["minmax"] = self._act_minmax
        self.active_state = "traversing"
        self.inner_score = None # will keep the heuristic score for the decision tree

    def _act_finished_traversing(self, global_env):
        if len(self.path) <= 1:
            self.change_state("terminated")
            score = self.people_saved
            if not global_env.get_attr(self.location, "shelter") > 0 or \
                    not (global_env.get_attr(self.location, "deadline") >= global_env.time):
                score -= (K + self.people_carried)
            self.score = score
        else:
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
        self.decision_type = "min"
        self.other_agent.decision_type = "max"

        self.other_agent.current_options = []
        self.current_options = []

        optimal_option = self._minmax()
        self._extract_optimal_move(optimal_option, global_env)

        if (DEBUG):
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
        # self.score = optimal_option.other_agent.score
        # self.other_agent.score = optimal_option.score
        self.temp_score = optimal_option.other_agent.temp_score
        self.other_agent.temp_score = optimal_option.temp_score
        if self.decision_type == "min":
            self.total_ad_score = self.temp_score - self.other_agent.temp_score
        else:
            self.total_ad_score = self.other_agent.temp_score - self.temp_score



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
                super()._act_finished_traversing(global_env)

    def _calculate_leaf_node_score(self):
        """
        update the score and others_score values using the heuristics
        :return:
        """
        self.temp_score = self.calc_f()
        self.other_agent.temp_score = self.other_agent.calc_f()
        # print("calculating leaf node. Score: {}   other score: {}".format(self.temp_score, self.other_agent.temp_score))
        self.total_ad_score = self.temp_score - self.other_agent.temp_score
        self.is_cutoff = True

    def _choose_optimal(self, option_list):
        """
        will calculate the score given a list of possible scores
        :param option_list: list of agents, as option for choosing
        :return: the proper score, depends on the type of agent and the self.decision_type
        """
        # TODO maybe the score in the other agent is the opposite here
        if self.decision_type == "max":
            return max(option_list, key=lambda x: -x.temp_score + x.other_agent.temp_score)
        elif self.decision_type == "min":
            return min(option_list, key=lambda x: -x.temp_score + x.other_agent.temp_score)
        else:
            raise ValueError("unknown decision type")

    def print_decision(self, decision_tree=None, max_level=float("infinity")):
        """
        https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3/29597209
        :param decision_tree:
        :param max_level:
        :return:
        """
        plt.figure(figsize=(40, 40), dpi=200)

        # this will print radially the nodes
        G = covert_local_to_global_tree(self)
        pos = hierarchy_pos(G, 0, width=2 * math.pi, xcenter=0)
        # new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}

        node_labels = nx.get_node_attributes(G, 'total_ad_score')

        # print graph
        nx.draw(G, pos=pos, node_size=10, labels=node_labels)

        # print A1 nodes
        a1_node_list = [node for node in G.nodes if G.nodes[node]["name"]=="A1"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=a1_node_list, node_color='blue',
                               node_size=50,  labels=node_labels, font_size=1)
        # print A2 nodes

        a2_node_list = [node for node in G.nodes if G.nodes[node]["name"]=="A2"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=a2_node_list, node_color='green', node_size=50,
                               labels=node_labels, font_size=1)

        terminated_list = [node for node in G.nodes if G.nodes[node]["active_state"] == "terminated"]
        nx.draw_networkx_nodes(G, pos=pos, nodelist=terminated_list, node_color='red', node_size=25,
                               labels=node_labels, font_size=1)
        # nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs, font_size=8)

        label_printer(G, pos, "location", 1)
        label_printer(G, pos, "other_score", -1)
        label_printer(G, pos, "score", -2.9999)

        # label_printer(G, pos, "location", 2)

        # plt.savefig("blorg.png")
        plt.show()


class AgentsManager:

    def __init__(self, agents):

        # nodes in this tree are agents that represent actions
        # are hashable by their entrance index
        self.tree = nx.DiGraph()
        self.agents = agents # the first agent in the list start first this is a tuple
        self.node_name_gen = count()

    def starting_minmax(self):
        self.tree.add_node(next(self.node_name_gen),agents=self.agents,
                           decision_type="min", optimal_child=None,
                           optimal_child_score=None, level=0)
        self.minmax_rec(0, 0)
        print_decision_tree(self.tree)

        # TODO extract action to do in the real world

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

        # get optimal child
        optimal_child, optimal_score = self._get_optimal_child(parent)

        # update parent
        self._update_parent(parent, optimal_child, optimal_score)

    def attach_agents_to_nodes(self, agents_tuple, parent, level):
        # adds the child to the tree and change decision_type
        child_index = next(self.node_name_gen)
        current_decision_string = self.tree.nodes[parent]["decision_type"]

        self.tree.add_node(child_index, agents=agents_tuple,
                           decision_type=self.change_decision(current_decision_string),
                           optimal_child=None, optimal_child_score=None, level=level)
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
            print(f"updating node {node}")

    def _update_parent(self, parent, optimal_child, optimal_score):
        """
        updates parent's score using the optimal child
        will updates the parent optimal_child field.
        """
        self.tree.nodes[parent]["optimal_child"] = optimal_child
        self.tree.nodes[parent]["optimal_child_score"] = optimal_score

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
        children = list(descendants(self.tree, parent))
        if self.tree.nodes[parent]["decision_type"] == "max":
            optimal_index = max(children,key=lambda x: self.optimality_opp(x))
        elif self.tree.nodes[parent]["decision_type"] == "min":
            optimal_index = min(children,key=lambda x: self.optimality_opp(x))
        else:
            raise ValueError()

        return optimal_index, self.optimality_opp(optimal_index)

    def get_max(self, children):
        curr_max = -10000000
        max_index = None
        curr_index = 0
        curr_score = -1000000
        for child in children:
            agents = self.tree.nodes[child]["agents"]
            curr_score = agents[0].inner_score - agents[1].inner_score
            if curr_score > curr_max:
                curr_max = curr_score
                max_index = curr_index
            curr_index += 1
        return max_index

    def get_min(self, children):
        curr_min = 10000000
        min_index = None
        curr_index = 0
        curr_score = 1000000
        for child in children:
            agents = self.tree.nodes[child]["agents"]
            curr_score = agents[0].inner_score - agents[1].inner_score
            if curr_score < curr_min:
                curr_min = curr_score
                min_index = curr_index
            curr_index += 1
        return min_index

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
        # TODO this
        env = copy.deepcopy(self.tree.nodes[node]["agents"][0].local_environment)
        if level % 2 == 0 and level !=0:
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
        if DEBUG:
            msg = "agent {} is simulating termination"
            print(msg.format(option.name))
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
