import matplotlib.pyplot as plt
import heapq
import copy
import math
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from networkx.algorithms.shortest_paths.generic import shortest_path as shortest_path_algorithm
from networkx.algorithms.shortest_paths.weighted import single_source_dijkstra
from environment import Environment

K = 2
L = 10
expansion_limit = 100000
Time_Per_Expansion = 0
STATE_LIST = ["no_op", "terminated", "traversing",
              "user_input",
              "find_people", "find_shelter",
              "annihilate", "wait",
              "heuristic_calculation", "finished_traversing",
              "minmax"]


class Agent:

    def __init__(self, name, starting_node):
        """
        behavior (function of how to act on the graph)
        knowledge (what the agent know about the world)
        initial knowledge? and informed action super mega 10000.0 generatoralizationrator processing king
        """
        self.name = name
        self.states = {"no_op": self._act_no_op,
                       "terminated": self._act_terminated,
                       "traversing": self._act_traversing}
        self.active_state = None

        # ----- STATE DEFINITION -------------

        self.change_state("no_op")
        self.location = starting_node  # this is a key to a node in local_environment
        self.carry_num = 0  # number of people currently been carried
        self.people_saved = 0
        self.time_to_wait = 0
        self.nodes_containing_people = []
        self.local_environment = None
        # ------------------------------------

        self.score = 0
        self.icon = None
        self.time_remaining_to_dest = 0
        self.destination = self.location  # key to the node been traversed

    def __ge__(self, other):
        return self.location >= other.location

    def __le__(self, other):
        return self.location <= other.location

    def __lt__(self, other):
        return self.location < other.location

    def __gt__(self, other):
        return self.location > other.location

    def change_state(self, state):
        if state not in STATE_LIST:
            raise ValueError("state {} is not a valid name for a state. if it does, add it to "
                             "STATE_LIST".format(state))

        elif state not in set(self.states.keys()):
            raise ValueError("state {} is a valid state, but not for agent of type {}".format(state, self))

        else:
            self.active_state = state

    def curr_time(self):
        return self.local_environment.time

    def print_state(self, delim=True):
        print("Agent name: {}".format(self.name))
        print("Agent state: {}".format(self.active_state))
        print("Agent location: {}".format(self.location))
        print("Agent number of people carrying: {}".format(self.carry_num))
        print("Agent number of people saved: {}".format(self.people_saved))
        print("Agent current time: {}".format(self.curr_time()))
        print("Agent nodes containing people: {}".format(self.nodes_containing_people))
        if delim:
            print("-----------------------------------")

    def traverse_path(self, path):
        """
        :param path: Path is represented as a list of nodes representing stops on the path

        :return:
        """

    def heuristic(self):
        heuristic_value = 0
        if self.active_state != "terminated":
            for people_node in self.nodes_containing_people:
                heuristic_value += self.local_environment.get_attr(people_node, "people")
            people_paths = self.filter_savable(self.location,
                                               self.nodes_containing_people, "people", time = self.curr_time())
            for people_node, people_path in people_paths.items():
                if people_path is None:
                    continue
                    # if there is no path add to the heuristics
                    #heuristic_value -= self.local_environment.get_attr(people_node, "people")

                else:
                    # get all the shelter paths
                    nodes_containing_shelter = [node for node in self.local_environment.graph.nodes if
                                                self.local_environment.get_attr(node, "shelter") > 0]

                    shelter_paths = self.filter_savable(people_node, nodes_containing_shelter, "shelter",
                                                        time=self.local_environment.calculate_path_time(people_path) +
                                                             self.curr_time())
                    # filter that ones without a path
                    shelter_paths = [shelter_path for _, shelter_path in shelter_paths.items() if
                                     shelter_path is not None]
                    # if there
                    #if len(shelter_paths) < 1:
                     #   heuristic_value -= self.local_environment.get_attr(people_node, "people")
                    if len(shelter_paths) >= 1:
                        heuristic_value -= self.local_environment.get_attr(people_node, "people")
        heuristic_value -= self.carry_num
        return heuristic_value

    def filter_savable(self, source, nodes, key, time=0):
        # get all people nodes in the graph
        nodes = [node for node in nodes if
                 self.local_environment.get_attr(node, key) > 0]

        # find shortest paths if exist
        savable_path = self.find_reachable(source=source, node_list=nodes)

        for node, path in savable_path.items():

            # check if shortest path doesn't exceed deadline
            time_at_path = time + self.local_environment.calculate_path_time(path)

            # if it does, add num of people in that node to heuristic
            if self.local_environment.get_node_deadline(node, time_at_path) < 0:
                savable_path[node] = None

        return savable_path

    def set_environment(self, global_env):
        self.local_environment = global_env
        self.nodes_containing_people = [node for node in global_env.graph.nodes if
                                        global_env.get_attr(node, "people") > 0]

    def act(self, global_env):
        if self.active_state == "traversing":
           print("agent {} is in state {} and traversing to {} at time {}".format(self.name,
                                                                                  self.active_state,
                                                                                  self.destination,
                                                                                  self.local_environment.time))
        else:
            print("agent {} is in state {} and acting at time {}".format(self.name,
                                                                         self.active_state,
                                                                         self.local_environment.time))
        print("agent {} is carrying {} and acting at time {}".format(self.name,
                                                                     self.carry_num, self.local_environment.time))
        print("agent {} is has saved {} at time {}".format(self.name,
                                                                     self.people_saved, self.local_environment.time))
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
            if False: #weight > 1000:
                xy_from = pos[self.location]
                xy_to = pos[self.destination]
                pos_ratio = (weight - self.time_remaining_to_dest) / weight
                xy = (1 - pos_ratio) * xy_from + pos_ratio * xy_to
            else:
                xy = pos[self.location]

        ab = AnnotationBbox(imagebox, xy,
                            xybox=(50, 50),
                            xycoords='data',
                            boxcoords="offset points",
                            pad=0,

                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle,angleA=0,angleB=90,rad=3")
                            )
        ab.set_zorder(0)
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
        potential_nodes = [node for node in nodes if self.local_environment.get_node_deadline(node) >= 0]
        edges_to_potential_nodes = self.local_environment.graph.edges(self.location)

        for single_edge in edges_to_potential_nodes:

            # if edge is blocked
            if self.local_environment.graph[single_edge[0]][single_edge[1]]["blocked"]:
                potential_nodes.remove(single_edge[1])
        return potential_nodes

    def get_min_edge(self, edges_list):
        curr_min = 2000000000
        edge_to_ret = ["no_edge"]
        for single_edge in edges_list:
            if self.local_environment.graph[single_edge[0]][single_edge[1]]["weight"] < curr_min:
                if not self.local_environment.graph[single_edge[0]][single_edge[1]]["blocked"]:
                    curr_min = self.local_environment.graph[single_edge[0]][single_edge[1]]["weight"]
                    edge_to_ret = single_edge

        return edge_to_ret

    def traverse_to_node(self, node, global_env):
        """
        will move the agent to the node.
        :param node: (hashable) the name of the node
        :param global_env:
        :return:
        """
        self.time_remaining_to_dest = global_env.graph.get_edge_data(self.location, node)["weight"]
        self.destination = node

        self.change_state("traversing")
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
        passable_subgraph = self.local_environment.get_passable_subgraph(keep_nodes=[source])
        shortest_paths = single_source_dijkstra(passable_subgraph, source)[1]
        shortest_paths = {node: path for node, path in shortest_paths.items() if node in set(node_list)}
        return shortest_paths


class Pc(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/monkey.png")
        self.states["user_input"] = self._act_user_input
        self.change_state("user_input")
        self.people_carried = 0
        self.terminate_once = 1

    def _act_traversing(self, global_env):
        print("remaining time: {}".format(self.time_remaining_to_dest))
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self.location = self.destination
            self.change_state("user_input")
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
        options = ["tr", "p", "d", "a", "te"]  # p - pick up, d - drop off, a - annihilate.
        if len(options) == 0:
            print("no option for Agent {} to traverse and is terminated".format(self.name))
            self.change_state("terminated")
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
                self.change_state("terminated")
                self._act_terminated(global_env)

            if ((user_input) == "p"):
                print("picked up: {} people".format(global_env.get_attr(self.location, "people")))
                self.people_carried += global_env.get_attr(self.location, "people")
                global_env.change_attr(self.location, "people", 0)

            if ((user_input == "d")):
                if self.local_environment.get_attr(self.location, "shelter") > 0:
                    print("Dropping off {} people".format(self.people_carried))
                    self.people_saved += self.people_carried
                    self.people_carried = 0
                else:
                    print("Not a valid drop-off location, NO MAN LEFT BEHIND!")

    def _act_terminated(self, global_env):
        if self.terminate_once > 0:
            print("Human agent will now terminate. Goodbye")
            self.score -= (K + self.people_carried) if (self.people_carried > 0) else 0
            print("Score: {}".format(self.score))
            self.terminate_once -= 1


class Greedy(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.icon = plt.imread("icons/brainstorm.png")
        self.states["find_people"] = self._act_find_people
        self.states["find_shelter"] = self._act_find_shelter
        self.change_state("find_people")
        self.people_carried = 0
        self.terminate_once = 1

    def calculate_real_score(self):
        real_score = 0
        if (self.active_state == "terminated"):
            real_score = self.local_environment.people_in_graph - self.people_saved
            #If you're not in a shelter, pay a penalty
            if (self.local_environment.get_attr(self.location, "shelter") == 0):
                real_score += K + self.people_carried
        return real_score

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if (self.time_remaining_to_dest <= 0):
            self.location = self.destination
            if self.people_carried < 1:
                self.change_state("find_people")
            else:
                self.change_state("find_shelter")
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
            self.change_state("terminated")
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
            curr_path_edges = zip(shortest_path, shortest_path[1:])
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
        people_in_location = global_env.get_attr(self.location, "people")
        if people_in_location > 0:
            print("picked up: {} people".format(people_in_location))
            # pickup people
            self.people_carried += people_in_location
            global_env.change_attr(self.location, "people", 0)
            self.change_state("find_shelter")
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
            self.change_state("find_people")
            self.act(global_env)

        else:
            self._act_find(global_env, "shelter")

    def _act_terminated(self, global_env):
        if self.terminate_once > 0:
            print("Greedy agent has been terminated.")
            self.people_saved -= K + self.people_carried
            print("Score: {}".format(self.score))
            self.terminate_once -= 1


class Annihilator(Agent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.wait_time = 0
        self.icon = plt.imread("icons/thunder-skull.png")
        self.states["annihilate"] = self._act_annihilate
        self.states["traversing"] = self._act_traversing
        self.states["wait"] = self._act_wait
        self.change_state("wait")

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            self.location = self.destination
            self.change_state("annihilate")
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
            self.change_state("terminated")
            return

        print("destroyer moved to node: {}".format(new_min_edge[1]))
        self.traverse_to_node(new_min_edge[1], global_env)

    def _act_wait(self, global_env):
        if global_env.time >= self.wait_time:
            self.change_state("annihilate")
            self._act_annihilate(global_env)


class AStarAgent(Greedy):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["heuristic_calculation"] = self._act_heuristic
        self.states["finished_traversing"] = self._act_finished_traversing
        self.states["wait"] = self._act_wait
        self.states["terminated"] = self._act_terminated
        self.change_state("heuristic_calculation")
        self.path = None
        self.destination_index = 1 # this is an index in the self.path
        self.num_of_expansions = 0
        self.expansion_limit = 0 # this is not used in astar

    def _act_wait(self, global_env):
        # if remaining path (including current node) is smaller then one, it has finished traversing
        self.time_to_wait -= 1

        # checks if while waiting, the place you're waiting at got destroyed
        if global_env.get_attr(self.location, "deadline") <= global_env.time:
            self.change_state("terminated")
            self.act(global_env)
        print("the time is: {}".format(global_env.time))
        # handles the time it waits to calculate
        if self.time_to_wait < 0:
            if len(self.path) <= 1:
                self.change_state("finished_traversing")
                self.act(global_env)
                return

            self.traverse_to_node(self.path[1], global_env)
            self.act(global_env)

    def _act_terminated(self, global_env):
        score = self.people_saved
        if global_env.get_attr(self.location, "shelter") == 0:
            score -= (K + self.carry_num)
        self.score = score
        msg = "inside _act_terminated, agent named: {} has a score of: {}"

    def calc_f(self):
        score = self.heuristic() + self.calculate_real_score()
        return score

    def _act_heuristic(self, global_env):
        self.path = self.calculate_astar_path()
        self.time_to_wait = math.ceil(self.num_of_expansions*Time_Per_Expansion)
        print("The heuristic agent will now take path:"
              " {} after {} expansions".format(self.path, self.num_of_expansions))

        print("The heuristic agent will now wait for {} time due to calculations.".format(self.time_to_wait))
        self.change_state("wait")
        self.act(global_env)

    def traverse_to_node(self, node, global_env):
        self.time_remaining_to_dest = global_env.graph.get_edge_data(self.location, node)["weight"]
        self.destination = node
        self.change_state("traversing")

    def _act_traversing(self, global_env):
        self.time_remaining_to_dest -= 1
        if self.time_remaining_to_dest <= 0:
            # perform checks if either destination or source were destroyed while travelling
            if global_env.get_attr(self.destination, "deadline") <= global_env.time:
                self.change_state("finished")
                self.act(global_env)
                return

            # break if trivial path
            if self.location == self.destination:
                self.change_state("terminated")
                self.act(global_env)
                return

            self.location = self.destination
            self._actions_for_arriving_at_node()
            # self.global_actions_for_arriving_at_node(global_env)

            # if remaining path (including current node) is smaller then one, it has finished traversing
            if len(self.path[self.destination_index:]) <= 1:
                self.change_state("finished_traversing")
                self.act(global_env)

            # else, will continue the path
            else:
                self.destination_index += 1
                self.traverse_to_node(self.path[self.destination_index], global_env)
                if self.location == self.destination:
                    self.change_state("terminated")

    def _actions_for_arriving_at_node(self):
        """
        Assuming that self.location is now updated
        will preform all actions and checks that are needed when landing on a new node.
        :return:
        """
        self.location = self.destination

        if self.local_environment.get_attr(self.location, "people") > 0:
            self.carry_num += self.local_environment.get_attr(self.location, "people")
            self.local_environment.change_attr(self.location, "people", 0)
            self.nodes_containing_people.remove(self.location)

        if self.local_environment.get_attr(self.location, "shelter") > 0:
            self.people_saved += self.carry_num
            self.carry_num = 0

    def global_actions_for_arriving_at_node(self, global_env):
        """
        Assuming that self.location is now updated
        will preform all actions and checks that are needed when landing on a new node.
        :return:
        """
        if global_env.get_attr(self.location, "people") > 0:
            self.carry_num += self.local_environment.get_attr(self.location, "people")
            global_env.change_attr(self.location, "people", 0)
            self.nodes_containing_people.remove(self.location)

        if global_env.get_attr(self.location, "shelter") > 0:
            self.people_saved += self.carry_num
            self.carry_num = 0

    def _act_finished_traversing(self, global_env):
        self.change_state("terminated")
        score = self.people_saved
        if not global_env.get_attr(self.location, "shelter") > 0 or \
                not (global_env.get_attr(self.location, "deadline") >= global_env.time):
            score -= (K + self.people_carried)
        self.score = score
        print("Astar agent score is: {}".format(score))

    def calculate_astar_path(self):
        self.num_of_expansions = 0
        self.destination_index = 1
        state_score_heap = []

        # first is f, second is agent, third is current path
        heapq.heappush(state_score_heap, (self.calc_f(), copy.deepcopy(self), [self.location]))
        return self._astar_main_loop(state_score_heap)

    def _astar_main_loop(self, min_heap):
        while self.num_of_expansions < expansion_limit:
            curr_node = heapq.heappop(min_heap)
            print("Agent score: {}".format(curr_node[0]))
            print("Agent path: {}".format(curr_node[2]))
            if curr_node[1].active_state == "terminated":
                return curr_node[2]
            self.num_of_expansions += 1
            self._expand_node(min_heap, curr_node)

        print("expansion limit of {} was exceeded."
              " Agent {} has failed and is now terminated".format(expansion_limit, self.name))
        return []

    def _expand_node(self, min_heap, curr_node):
        """
        if not terminated, return  h
        if terminated, return g
        """

        agent = curr_node[1]
        current_route = curr_node[2]
        # create new agents for every neighbors
        neighbors = agent.local_environment.get_passable_subgraph(agent.curr_time(),
                                                                  keep_nodes=[agent.location])[agent.location]
        for neighbor_node, neighbor_data in neighbors.items():
            if ((agent.curr_time() + neighbor_data["weight"]) >
                    agent.local_environment.get_node_deadline(neighbor_node)):
                continue
            new_agent = copy.deepcopy(agent)
            new_agent.location = neighbor_node
            new_agent.local_environment.time += neighbor_data["weight"]

            # if node has people in it
            if new_agent.location in set(new_agent.nodes_containing_people):
                new_agent.carry_num += new_agent.local_environment.get_attr(new_agent.location, "people")
                new_nodes_containing_people = set(new_agent.nodes_containing_people)
                new_nodes_containing_people.remove(neighbor_node)
                new_agent.nodes_containing_people = list(new_nodes_containing_people)

            # if node is a shelter
            if new_agent.local_environment.get_attr(new_agent.location, "shelter") > 0:
                new_agent.people_saved += new_agent.carry_num
                new_agent.carry_num = 0

            # add new agent to the heap
            new_route = copy.deepcopy(current_route)
            new_route.append(neighbor_node)
            heapq.heappush(min_heap, (new_agent.calc_f(), new_agent, new_route))
            print("Agent is terminated: {}".format(new_agent.active_state == "terminated"))
            print("Agent time is:{}".format(new_agent.curr_time()))
            print("Agent score: {}".format(new_agent.calc_f()))
            print("Agent path: {}".format(new_route))

        # add new agent for the case what it is terminated here
        new_agent = copy.deepcopy(agent)
        new_agent.change_state("terminated")
        print("Agent is terminated: {}".format(new_agent.active_state == "terminated"))
        print("Agent score: {}".format(new_agent.calc_f()))
        print("Agent path: {}".format(current_route))
        heapq.heappush(min_heap, (new_agent.calc_f(), new_agent, current_route))


class LimitedAStarAgent(AStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)
        self.states["heuristic_calculation"] = self._act_heuristic
        self.expansion_limit = L

    def calculate_astar_path(self):
        self.num_of_expansions = 0
        self.destination_index = 1
        state_score_heap = []

        # first is f, second is agent, third is current path
        copy_agent = copy.deepcopy(self)
        copy_agent.local_environment.time += self.expansion_limit*Time_Per_Expansion

        heapq.heappush(state_score_heap, (self.calc_f(), copy_agent, [self.location]))
        return self._astar_main_loop(state_score_heap)

    def _astar_main_loop(self, min_heap):
        while self.num_of_expansions < self.expansion_limit:
            curr_node = heapq.heappop(min_heap)
            if curr_node[1].active_state == "terminated":
                return curr_node[2]
            self.num_of_expansions += 1
            self._expand_node(min_heap, curr_node)
        return heapq.heappop(min_heap)[2][:2]


    def _act_finished_traversing(self, global_env):
        if len(self.path) <= 1:
            self.change_state("terminated")
            score = self.people_saved
            if not global_env.get_attr(self.location, "shelter") > 0 or \
                    not (global_env.get_attr(self.location, "deadline") >= global_env.time):
                score -= (K + self.people_carried)
            self.score = score
        else:
            self.change_state("heuristic_calculation")


class PureHeuristicAStarAgent(AStarAgent):
    def __init__(self, name, starting_node):
        super().__init__(name, starting_node)

    def calc_f(self):
        score = self.heuristic()
        return score



