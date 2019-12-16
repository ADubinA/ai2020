from ai import *


class AdversarialAgent(AStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states = {"minmax":self._act_minmax}
        self.alpha = -float("infinity")
        self.beta = float("infinity")
        self.score = None
        self.game_state = "max"
        # self. decision tree

    def _act_minmax(self):
        pass
        # alpha beta prune

        # calculate all possible actions (includes terminated)

        # get other agent

        # call other agent in the current state (after the agent has moved)

        # if agent node is a cut off, use heuristics of both agents.

        # get score (depends on type of class




    def _get_score(self, score_list):
        pass
        # you're mom is gay

    def print_decision(self, decision_tree=None, max_level=float("infinity")):
        pass