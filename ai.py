import networkx as nx
import matplotlib.pyplot as plt

from matplotlib.offsetbox import AnnotationBbox,OffsetImage
from networkx.algorithms.shortest_paths.generic import shortest_path as shortest_path_algorithm
from networkx.algorithms.shortest_paths.weighted import single_source_dijkstra

K = 2

class Agent:
    def __init__(self, name,  starting_node):
        """
        behavior (function of how to act on the graph)
        knowledge (what the agent know about the world)
        initial knowledge? and informed action super mega 10000.0 generatoralizationrator processing king
        """
        self.name = name
        self.states = {"no_op": self._act_no_op,
                       "terminated": self._act_terminated,
                       "traversing": self._act_traversing}

        ##### STATE DEFINITION #####
        self.active_state = "no_op"
        self.location = starting_node  # this is a key to a node in local_environment
        self.carry_num = 0  # number of people currently been carried
        self.score = 0
        self.curr_time = 0
        self.nodes_containing_people = []
        self.nodes_containing_shelter = []
        ##### STATE DEFINITION #####

        self.local_environment = None
        self.icon = None
        self.time_remaining_to_dest = 0
        self.destination = self.location  # key to the node been traversed

    def heuristic(self):

        heuristic_value = 0

        people_paths = self.filter_savable(self.location, self.nodes_containing_people, "people")

        for people_node, people_path in people_paths.items():
            if people_path is None:
                # if there is no path add to the heuristics
                heuristic_value += self.local_environment.get_attr(people_node, "people")

            else:
                # get all the shelter paths
                shelter_paths = self.filter_savable(people_node,self.nodes_containing_shelter, "shelter",
                                                    time=self.local_environment.calculate_path_time(people_path))
                # filter that ones without a path
                shelter_paths = [shelter_path for _, shelter_path in shelter_paths.items() if shelter_path is not None]
                # if there
                if len(shelter_paths) < 1:
                    heuristic_value += self.local_environment.get_attr(people_node, "people")


        return heuristic_value

    def filter_savable(self,source, nodes, key, time=0):
        # get all people nodes in the graph
        nodes = [node for node in nodes if
                 self.local_environment.get_attr(node, key) > 0]

        # find shortest paths if exist
        savable_path = self.find_reachable(source=self.location, node_list=nodes)

        for node, path in savable_path.items():

            # check if shortest path doesn't exceed deadline
            time_at_path = time + self.local_environment.calculate_path_time(path)

            # if it does, add num of people in that node to heuristic
            if time_at_path >= self.local_environment.get_attr(node, "deadline"):
                savable_path[node] = None

        return savable_path


    def set_environment(self,  global_env):
        self.local_environment = global_env
        self.nodes_containing_people = [node for node in global_env.graph.nodes if
                                        global_env.get_attr(node, "people")>0]
        self.nodes_containing_shelter = [node for node in global_env.graph.nodes if
                                        global_env.get_attr(node, "shelter")>0]

    def act(self,  global_env):
        print("agent {} is in state {} and will act now".format(self.name, self.active_state))
        print("heuristics = " + str(self.heuristic()))
        self.states[self.active_state](global_env)

    def _act_no_op(self, gloval_env):
        print("agent {} is in state no-op and does nothing".format(self.name))

    def _act_terminated(self, gloval_env):
        # TODO might want this to be in logging.debug
        print("agent {} is in state terminated and does nothing".format(self.name))

    def _act_traversing(self, gloval_env):
        raise NotImplemented()

    def get_current_location(self):
        return self.location

    def get_annotation_box(self, pos, ax):
        """
        adds an annotation box with the agent icon on the ax
        :param pos: coordinates of all  of the nodes in the screen
        :param ax: axis from plt
        :return: None
        """
        imagebox = OffsetImage(self.icon, zoom=0.04, cmap='gray')
        imagebox.image.axes = ax

        if self.destination == self.location:
            xy = pos[self.location]

        else:
            weight = self.local_environment.graph.edges[self.location, self.destination]["weight"]
            if weight > 0:
                xy_from = pos[self.location]
                xy_to = pos[self.destination]
                pos_ratio = (weight - self.time_remaining_to_dest) / weight
                xy = (1 - pos_ratio) * xy_from + pos_ratio * xy_to
            else:
                xy = pos[self.location]

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

    def traverse_to_node(self, node,  global_env):
        """
        will move the agent to the node.
        :param node: (hashable) the name of the node
        :param global_env:
        :return:
        """
        self.time_remaining_to_dest = global_env.graph.get_edge_data(self.location, node)["weight"]
        self.destination = node

        self.active_state = "traversing"
        self.act(global_env)

    def find_reachable(self, source, node_list):
        """

        :param source: starting node hash local env
        :param node_list: list of nodes from local env that we want to find shortest path to
        :return: A list of the the same size as node_list containing  the shortest path in local env from start
                or None if doesn't exist
        """
        # get the subgraph
        # I choose here a random node, but other options will be better and slower
        passable_subgraph = self.local_environment.get_passable_subgraph()

        shortest_paths = single_source_dijkstra(passable_subgraph, source)[1]
        shortest_paths = {node:path for node, path in shortest_paths.items() if node in set(node_list)}
        return shortest_paths


class Pc(Agent):
    def __init__(self, name,  starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/monkey.png")
        self.states["user_input"] = self._act_user_input
        self.states["traversing"] = self._act_traversing
        self.states["terminated"] = self._act_terminated
        self.active_state = "user_input"
        self.people_carried = 0
        self.terminate_once = 1

    def _act_traversing(self, global_env):
        print("remaining time: {}".format(self.time_remaining_to_dest))
        self.time_remaining_to_dest -= 1
        if (self.time_remaining_to_dest <= 0):
            self.location = self.destination
            self.active_state = "user_input"
            self.act(global_env)


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
        print("letters: \"tr\" to traverse, \"p\" to pick up people, \"d\" to drop off at shelter ")
        print("letters: \"a\" to annihilate an adjacent edge, \"te\" to terminate")
        traversable_nodes = self._get_traversable_nodes()
        options = ["tr", "p", "d", "a", "te"] # p - pick up, d - drop off, a - annihilate.
        if len(options) == 0:
            print("no option for Agent {} to traverse and is terminated".format(self.name))
            self.active_state = "terminated"
            return

        input_ok = False
        user_input = None
        while not input_ok:
            user_input = input()
            if not (user_input in options):
                print("{} is not a valid option".format(user_input, self.location))
                continue
            if (user_input == "tr"):
                print("Please type destination: ")
                try:
                    destination = int(input())
                    if (destination) in traversable_nodes:
                        self.traverse_to_node(destination, global_env)
                        input_ok = True
                        continue
                    else:
                        print("{} is not a neighbor to {}".format(destination, self.location))
                        continue
                except ValueError as e:
                    print("{} is not a valid input as destination".format(user_input))
                    input_ok = False

            if ((user_input) == "te"):
                input_ok = True
                self.active_state = "terminated"
                self._act_terminated(global_env)

            if ((user_input) == "p"):
                print("picked up: {} people".format(global_env.get_attr(self.location, "people")))
                self.people_carried += global_env.get_attr(self.location, "people")
                global_env.change_attr(self.location, "people", 0)

            if ((user_input == "d")):
                if self.local_environment.get_attr(self.location, "shelter") > 0:
                    print("Dropping off {} people".format(self.people_carried))
                    self.score += self.people_carried
                    self.people_carried = 0
                else:
                    print("Not a valid drop-off location, NO MAN LEFT BEHIND!")

    def _act_terminated(self, global_env):
        if self.terminate_once > 0:
            print("Human agent will now terminate. Goodbye")
            self.score -= K + self.people_carried
            print("Score: {}".format(self.score))
            self.terminate_once -= 1


class Greedy(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/brainstorm.png")
        self.states["find_people"] = self._act_find_people
        self.states["find_shelter"] = self._act_find_shelter
        self.states["traversing"] = self._act_traversing
        self.states["terminated"] = self._act_terminated
        self.active_state = "find_people"
        self.people_carried = 0
        self.terminate_once = 1

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if (self.time_remaining_to_dest <= 0):
            self.location = self.destination
            if self.people_carried < 1:
                self.active_state = "find_people"
            else:
                self.active_state = "find_shelter"
            # self.act(global_env)

    # Returns a dictionary of nodes and shortest weight to nodes.
    def _act_find(self, global_env, find_by):
        if find_by == "people":
            search_attribute = "people"
        else:
            search_attribute = "shelter"

        shortest_paths_to_target = []
        # filter nodes that have only people in them ( >0 )
        node_options = self.local_environment.graph.nodes
        node_options = [node for node, data in node_options.items() if data[search_attribute] > 0]

        # terminate if there is no option
        if len(node_options) == 0:
            self.active_state = "terminated"
            self.score -= self.people_carried
            self.act(global_env)
            return

        # I choose here a random node, but other options will be better and slower
        best_path_length = float("inf")
        best_path = None
        curr_path_length = 0
        curr_path_edges = []
        for node_option in node_options:
            curr_path_length = 0
            # find the shortest path from the filtered ones

            shortest_path = shortest_path_algorithm(self.local_environment.graph, self.location, node_option,
                                                   weight="weight")
            curr_path_edges = zip(shortest_path,shortest_path[1:])
            for edge in curr_path_edges:
                curr_path_length += self.local_environment.graph[edge[0]][edge[1]]["weight"]

            if curr_path_length < best_path_length:
                best_path_length = curr_path_length
                best_path = shortest_path

        # move to the next path
        self.traverse_to_node(best_path[1], global_env)

    def _act_find_people(self, global_env):
        """
        the agent should compute the shortest currently unblocked path to the next vertex with people to be rescued,
        or to a shelter if it is carrying people, and try to follow it. If there is no such path, do terminate.
         Here and elsewhere, if needed, break ties by prefering lower-numbered vertices and/or edges.
        :param global_env:
        :return: None
        """
        # if there are people in this node
        if self.local_environment.get_attr(self.location, "people") > 0:
            print("picked up: {} people".format(global_env.get_attr(self.location, "people")))
            # pickup people
            self.people_carried += global_env.get_attr(self.location, "people")
            global_env.change_attr(self.location, "people", 0)
            self.active_state = "find_shelter"
            self.act(global_env)

        else:
            self._act_find(global_env, "people")

    def _act_find_shelter(self, global_env):
        # In case we encounter people on the road to the shelter.
        if self.local_environment.get_attr(self.location, "people") > 0:
            print("picked up: {} people".format(global_env.get_attr(self.location, "people")))
            self.people_carried += global_env.get_attr(self.location, "people")
            global_env.change_attr(self.location, "people", 0)

        # if the current node is a shelter
        if self.local_environment.get_attr(self.location, "shelter") > 0:
            # remove people into the shelter #TODO will not add people the shelter
            self.score += self.people_carried
            self.people_carried = 0
            global_env.change_attr(self.location, "people", 0)
            self.active_state = "find_people"
            self.act(global_env)

        else:
            self._act_find(global_env, "shelter")

    def _act_terminated(self, global_env):
        if self.terminate_once > 0:
            print("Greedy agent has been terminated.")
            self.score -= K + self.people_carried
            print("Score: {}".format(self.score))
            self.terminate_once -= 1


class Annihilator(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.wait_time = 0 #TODO change wait time.
        self.icon = plt.imread("icons/thunder-skull.png")
        self.states["annihilate"] = self._act_annihilate
        self.states["traversing"] = self._act_traversing
        self.states["wait"] = self._act_wait
        self.active_state = "wait"

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self.location = self.destination
            self.active_state = "annihilate"
            # self.act(global_env)

    def _act_annihilate(self, global_env):

        """
        The vandal works as follows: it does wait_time no-ops,
        and then blocks the lowest-cost edge adjacent to its current vertex (takes 1 time unit).
        Then it traverses a lowest-cost remaining edge, and this is repeated.
        Prefer the lowest-numbered node in case of ties. If there is no edge to block or traverse, do terminate.
        :param global_env:
        :return: None
        """

        min_edge = self.get_min_edge(self.local_environment.graph.edges(self.location))
        print("destroyed edge: {}".format(min_edge))
        global_env.graph[min_edge[0]][min_edge[1]]["blocked"] = True
        new_min_edge = self.get_min_edge(self.local_environment.graph.edges(self.location))
        if (new_min_edge[0] == "no_edge"):
            print("no option for Agent {} to traverse and is terminated".format(self.name))
            self.active_state = "terminated"
            return

        print("destroyer moved to node: {}".format(new_min_edge[1]))
        self.traverse_to_node(new_min_edge[1], global_env)



    def _act_wait(self, global_env):
        if (global_env.time >= self.wait_time):
            self.active_state = "annihilate"
            self._act_annihilate(global_env)


class HeuristicAgent(Greedy):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)

    ##Checks if current state was terminate. If it wasn't, expand nodes.
    """
        Stages:
        while true:
            1. Pop the first state in the state-min-heap, calculated by score.
            2. If it's terminate, return the path leading up to it.
            3. If it's not, expand it by checking all neighbhors+immediate terminate
            4. Add each expansion to the min heap
    """
    def initilizer(self):
        """
        minHeap = create_empty_heap() #to be sorted by f
        minHeap.add(initial state)
        return main_loop(minHeap) ##expect a path
        ##If the path is empty, it means terminate.
        """
        pass

    def main_loop(self, minHeap):
        """
        expansions = 0
        while(curr_expansion < limit):
            curr_node = minHeap.pop()
            #if destinatin is -1, it means terminate
            neighbhors = get_neighbhors(curr_node)
            for neighbhor in neighbhors:
                minHeap.add(expand_node(self, destination, weight)

            #if destinatin is -1, it means terminate
            minHeap.add(expand_Node(self, destination, weight, termiante = True), curr_node.append(destination))
            expansions += 1
        """
        pass



    def expand_node(self, destination, weight, terminate = False):
        ##returns the score of the node expanded
        """
        if not terminated, return  h
        if terminated, return g
        """
        pass