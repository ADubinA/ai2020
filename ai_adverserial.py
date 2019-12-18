from ai import *
import networkx as nx
from tools.print_tools import *
MAX_LEVEL = 5

class AdversarialAgent(AStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states = {"minmax": self._act_minmax}
        self.alpha = -float("infinity")
        self.beta = float("infinity")
        self.score = None
        self.decision_type = "max"
        self.current_options = []  # a list of agents, where each agent is the rival.
        self.level = 0  # where in the tree the agent is been developed
        self.is_cutoff = False  # is used for graph visualization

    def _act_minmax(self):
        """
        expand a minmax node, where the node is an agent.
        with prune with current alpha beta values
        :return: the score from the current result of the minmax tree
        """
        # if agent node is a cut off, use heuristics of both agents.
        if self.level > MAX_LEVEL:
            self.score = self.heuristic()  # TODO do the same for the next agent?
            self.is_cutoff = True

        # update the level that we are working on
        self.level += 1

        # calculate all possible actions. If traversing, will keep traversing
        if self.active_state == "traversing":
            neighbors = {self.destination: self.local_environment.nodes}# TODO first to the right format
        else:
            neighbors = self.local_environment.get_passable_subgraph(self.curr_time,
                                                                     keep_nodes=[self.location])[self.location]
        # add the terminate action to the possibilities
        # TODO think how to write this + update the score here (similar to the cutoff)

        # TODO alpha beta prune

        # get other agent (if more then one, will pick the first)
        other_agent = [agent for agent in self.local_environment.agents if agent.name != self.name][0]

        # update the environment for each other agent, depending on the action taken by the self agent
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
            self.current_options.append(new_other_agent)

            # do the minmax for the other agent
            new_other_agent._act_minmax()

        # get score (depends on type of class)  is all the children
        self.score = self._get_score(self.current_options)
        # TODO handle the empty list

        # change to action traverse to the optimal move

    def _get_score(self, score_list):
        """
        will calculate the score given a list of possible scores
        :param score_list: list of values
        :return: the proper score, depends on the type of agent and the self.decision_type
        """
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
        nx.draw(G, pos=new_pos, node_size=50)
        nx.draw_networkx_nodes(G, pos=new_pos, nodelist=[0], node_color='blue', node_size=200)
