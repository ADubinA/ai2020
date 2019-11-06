import networkx as nx
import matplotlib.pyplot as plt

from matplotlib.offsetbox import AnnotationBbox,OffsetImage


class Agent:
    def __init__(self, name,  starting_node):
        """
        behavior (function of how to act on the graph)
        knowledge (what the agent know about the world)
        initial knowledge? and informed action super mega 10000.0 generatoralizationrator processing king
        """
        self.name = name
        self.states = {"no_op": self._act_no_op, "terminated": self._act_terminated}
        self.active_state = "no_op"
        self.location = starting_node  # this is a key to a node in local_environment
        self.local_environment = None
        self.carry_num = 0
        self.icon = None

    def set_environment(self,  global_env):
        pass

    def act(self,  global_env):
        print("agent {} is in state {} and will act now".format(self.name, self.active_state))
        self.states[self.active_state](global_env)

    def _act_no_op(self, gloval_env):
        print("agent {} is in state no-op and does nothing".format(self.name))

    def _act_terminated(self, gloval_env):
        # TODO might want this to be in logging.debug
        print("agent {} is in state terminated and does nothing".format(self.name))

    def get_current_location(self):
        return self.location

    def get_annotation_box(self, xy, ax):
        """
        adds an annotation box with the agent icon on the ax
        :param xy: coordinates of the node in the screen
        :param ax: axis from plt
        :return: None
        """
        imagebox = OffsetImage(self.icon, zoom=0.04, cmap='gray')
        imagebox.image.axes = ax
        ab = AnnotationBbox(imagebox, xy,
                            xybox=(20, 20),
                            xycoords='data',
                            boxcoords="offset points",
                            pad=0,

                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle,angleA=0,angleB=90,rad=3")
                            )

        ax.add_artist(ab)

    def _get_traversable_nodes(self):
        """
        Calculates the nodes which the agent can go to.
        For now, will only allow to traverse nodes that :
            1. Have an edge between them
            2. The edge is unblocked
            3. The destination node have deadline > 0
        :return: a list of passable nodes (by name)
        """
        nodes = self.local_environment.get_node_neighborhood(self.location)
        potential_nodes = [node for node in nodes if self.local_environment.graph.nodes[node]["deadline"] > 0]
        edges_to_potential_nodes = self.local_environment.graph.edges(self.location)

        for single_edge in edges_to_potential_nodes:
            #TODO Verify it still works on a directed graph
            if (self.local_environment.graph[single_edge[0]][single_edge[1]]["blocked"] == True):
                potential_nodes.remove(single_edge[1])
        return potential_nodes

    def get_min_edge(self, edges_list):
        curr_min = 2000000000
        edge_to_ret = ["no_edge"]
        for single_edge in edges_list:
            if (self.local_environment.graph[single_edge[0]][single_edge[1]]["weight"] < curr_min):
                if (self.local_environment.graph[single_edge[0]][single_edge[1]]["blocked"] == False):
                    curr_min = self.local_environment.graph[single_edge[0]][single_edge[1]]["weight"]
                    edge_to_ret = single_edge

        return edge_to_ret

class Pc(Agent):
    def __init__(self,name,  starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/monkey.png")
        self.states["user_input"] = self._act_user_input
        self.active_state = "user_input"

    def set_environment(self, global_env):
        super().set_environment(global_env)
        self.local_environment = global_env

    def _act_user_input(self, global_env):
        """
        get input from user and executes on the graph
        will not approve illegal actions and will ask again for legal action. TODO will make you coffee after that
        :param global_env:
        :return: None
        """
        # get input from user
        # validate input
        # update location and global_env

        print("please insert an action:")
        print("numbers: (1,2,3,...) will move the Pc if an edge allow it")
        options = self._get_traversable_nodes()
        if len(options) == 0:
            print("no option for Agent {} to traverse and is terminated".format(self.name))
            self.active_state = "terminated"
            return

        input_ok = False

        while not input_ok:
            try:
                user_input = int(input())
                if user_input in options:
                    input_ok = True
                else:
                    print("{} is not a neighbor to {}".format(user_input, self.location))

            except ValueError as e:
                print(" not a valid input, try again with numbers")

        self.location = user_input




class Greedy(Agent):
    def __init__(self,name, starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/brainstorm.png")

    def set_environment(self, global_env):
        super().set_environment(global_env)
        self.local_environment = global_env

    def act(self,  global_env):
        """
        the agent should compute the shortest currently unblocked path to the next vertex with people to be rescued,
        or to a shelter if it is carrying people, and try to follow it. If there is no such path, do terminate.
         Here and elsewhere, if needed, break ties by prefering lower-numbered vertices and/or edges.
        :param global_env:
        :return: None
        """
        # if carrying people find closest path to the shelter

        # if not find closest people

        raise NotImplemented()




class Annihilator(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.wait_time = 0 #TODO change wait time.
        self.icon = plt.imread("icons/thunder-skull.png")
        self.states["annihilate"] = self._act_annihilate
        self.states["wait"] = self._act_wait
        self.active_state = "wait"

    def set_environment(self, global_env):
        super().set_environment(global_env)
        self.local_environment = global_env

    def _act_annihilate(self, global_env):
        min_edge = self.get_min_edge(self.local_environment.graph.edges(self.location))
        print("destroyed edge: {}".format(min_edge))
        global_env.graph[min_edge[0]][min_edge[1]]["blocked"] = True
        new_min_edge = self.get_min_edge(self.local_environment.graph.edges(self.location))
        if (new_min_edge[0] == "no_edge"):
            print("no option for Agent {} to traverse and is terminated".format(self.name))
            self.active_state = "terminated"
            return

        print("destroyer moved to edge: {}".format(new_min_edge[1]))
        self.location = new_min_edge[1]

        """
        The vandal works as follows: it does wait_time no-ops,
        and then blocks the lowest-cost edge adjacent to its current vertex (takes 1 time unit).
        Then it traverses a lowest-cost remaining edge, and this is repeated.
        Prefer the lowest-numbered node in case of ties. If there is no edge to block or traverse, do terminate.
        :param global_env:
        :return: None
        """


    def _act_wait(self, global_env):
        if (global_env.time >= self.wait_time):
            self.active_state = "annihilate"
            self._act_annihilate(global_env)
