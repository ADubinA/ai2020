from ai import *
import networkx as nx
from tools.print_tools import *
MAX_LEVEL = 5

class AdversarialAgent(AStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states = {"minmax": self._act_minmax}
        self.active_state = "terminated"
        self.alpha = -float("infinity")
        self.beta = float("infinity")
        self.score = None
        self.others_score = None  # score for the other agent in the tree. the score is for the same tick.
        self.decision_type = "max"
        self.current_options = []  # a list of agents, where each agent is the rival.
        self.level = 0  # where in the tree the agent is been developed
        self.is_cutoff = False  # is used for graph visualization

    def _simulate(self, state):
        """
        Given a state, the agent will simulate one tick in it's environment
        will update it's own active state if needed
        :param state:
        :return: None
        """
        """       
         for neighbor_node, neighbor_data in neighbors.items():

            # checks again for some reason that self can go to the node # TODO is that necessary (is from expand node)
            if ((self.curr_time + neighbor_data["weight"]) >
                    self.local_environment.get_node_deadline(neighbor_node)):
                continue

            # create a copy of the other agent and it's environment
            new_other_agent = copy.deepcopy(other_agent)

            # update the effect of self after taken action
            self_after_action = copy.deepcopy(self)
            self_after_action.curr_time += 1
            self_after_action.path.append(neighbor_node)

            # TODO finish updating the self_agent after action, USING action (_act_traversing ect...)
            # check if action will lead to a new node
            # if it does, use _actions_for_arriving_at_node

            # TODO update the environment (of self_after_action, after the action was taken

            # updated the new_other_agent env with the updates that self_after_action did.
            new_other_agent.set_environment(self_after_action.local_environment)
            self.current_options.append(new_other_agent)"""
        # will update the time self.level%num_agents==0 and level!=0
        pass

    def _calculate_options(self, other_agent):
        """
        will return a list of all the possible options for agent to do
        :param other_agent: the other agent for duplication. will be a deep copy
        :return: Returns a list of updated Environments with the updated action
        """
        """       
         if self.active_state == "traversing":
            neighbors = {self.destination: self.local_environment.nodes}# TODO first to the right format
        else:
            neighbors = self.local_environment.get_passable_subgraph(self.curr_time,
                                                                     keep_nodes=[self.location])[self.location]
        # TODO add the terminate action to the possibilities
        # TODO think how to write this + update the score here (similar to the cutoff)
        """
        # will call simulate here


    def ab_prune(self):
        """
        will prune the current_options variable using alpha beta pruning.
        :return:
        """
        pass

    def _act_minmax(self, global_env):
        self._minmax()

        #calculate the path after minmax calculation (by which child has the same score)

    def _minmax(self):
        """
        expand a minmax node, where the node is an agent.
        with prune with current alpha beta values
        :return: the score from the current result of the minmax tree
        """
        # if agent node is a cut off, use heuristics of both agents.
        if self.level > MAX_LEVEL:
            self._calculate_leaf_node_score()
            return

        # update the level that we are working on
        self.level += 1

        # get other agent (if more then one, will pick the first)
        other_agent = [agent for agent in self.local_environment.agents if agent.name != self.name][0]

        # calculate all possible actions. If traversing, will keep traversing
        self.current_options = self._calculate_options(other_agent)

        # alpha beta prune
        self.ab_prune()

        for option in self.current_options:
            option._act_minmax()

        # get score (depends on type of class)  is all the children
        score_list = [agent.score for agent in self.current_options]
        self.score = self._get_score(score_list)

        # change to action traverse to the optimal move

    def _calculate_leaf_node_score(self):
        """
        update the score and others_score values using the heuristics
        :return:
        """
        self.score = self.heuristic()

        # TODO do the same for the next agent?
        other_agent = [agent for agent in self.local_environment.agents if agent.name != self.name][0]
        self.others_score = other_agent.heuristics()
        self.is_cutoff = True


    def _get_score(self, score_list):
        """
        will calculate the score given a list of possible scores
        :param score_list: list of values
        :return: the proper score, depends on the type of agent and the self.decision_type
        """
        # TODO handle the empty list

        if self.decision_type == "max":
            return max(score_list)
        elif self.decision_type == "min":
            return min(score_list)
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
        new_pos = {u: (r * math.cos(theta), r * math.sin(theta)) for u, (theta, r) in pos.items()}
        nx.draw(G, pos=new_pos, node_size=50,with_labels="score")
        nx.draw_networkx_nodes(G, pos=new_pos, nodelist=[0], node_color='blue', node_size=200)
