import networkx as nx
class Agent:
    def __init__(self):
        """
        behavior (function of how to act on the graph)
        knowledge (what the agent know about the world)
        initial knowledge? and informed action super mega 10000.0 generatoralizationrator processing king
        """
        self.states = ["no_op", "terminated", "ready"]
        self.active_state = "ready"
        self.location = None
        self.local_environment = nx.Graph()
        self.carry_num = 0

    def set_environment(self,  global_env):
        pass

    def act(self,  global_env):
        pass


class User(Agent):
    def __init__(self):
        super().__init__()

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
    def __init__(self):
        super().__init__()

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
    def __init__(self):
        super().__init__()
        self.wait_time = 666

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