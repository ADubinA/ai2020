import networkx as nx
import matplotlib.pyplot as plt
from scipy.ndimage import imread
from matplotlib.offsetbox import AnnotationBbox,OffsetImage
class Agent:
    def __init__(self, starting_node):
        """
        behavior (function of how to act on the graph)
        knowledge (what the agent know about the world)
        initial knowledge? and informed action super mega 10000.0 generatoralizationrator processing king
        """
        self.states = ["no_op", "terminated", "ready"]
        self.active_state = "ready"
        self.location = starting_node  # this is a node from networtx graph
        self.local_environment = nx.Graph()
        self.carry_num = 0
        self.icon = None

    def set_environment(self,  global_env):
        pass

    def act(self,  global_env):
        pass

    def get_current_location(self):
        return self.location

    def get_anotation_box(self,xy,ax):

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

class Pc(Agent):
    def __init__(self, starting_node):
        super().__init__(starting_node)
        self.icon = plt.imread("icons/monkey.png")

    def set_environment(self, global_env):
        super().set_environment(global_env)
        self.local_environment = global_env

    def act(self,  global_env):
        """
        get input from user and executes on the graph
        will not approve illegal actions and will ask again for legal action. TODO will make you coffee after that
        :param global_env:
        :return: None
        """
        # get input from user
        # validate input
        # update location and global_env

        raise NotImplemented()



class Greedy(Agent):
    def __init__(self, starting_node):
        super().__init__(starting_node)
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
    def __init__(self, starting_node):
        super().__init__(starting_node)
        self.wait_time = 666
        self.icon = plt.imread("icons/thunder-skull.png")

    def set_environment(self, global_env):
        super().set_environment(global_env)
        self.local_environment = global_env

    def act(self,  global_env):
        """
        The vandal works as follows: it does wait_time no-ops,
        and then blocks the lowest-cost edge adjacent to its current vertex (takes 1 time unit).
        Then it traverses a lowest-cost remaining edge, and this is repeated.
        Prefer the lowest-numbered node in case of ties. If there is no edge to block or traverse, do terminate.
        :param global_env:
        :return: None
        """

        raise NotImplemented()