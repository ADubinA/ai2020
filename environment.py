import networkx as nx
import matplotlib.pyplot as plt
import logging
from parser import Parser
from ai import Pc
from ai import Annihilator
from ai import Greedy
from ai import AStarAgent

class Environment:
    def __init__(self, file_name):
        parser_instance = Parser("test_graph.json")
        active_agents = 1 ##TODO update this in a concise way
        # here we insert the parser to the vars
        self.graph = nx.Graph()
        self.people_in_graph = 0
        for vertex in parser_instance.vertex_list:
            self.add_vertex(**vertex)
            self.people_in_graph += vertex["people"]
        for edge in parser_instance.edge_list:
            self.add_edge(edge["from"], edge["to"], **edge)
        self.attributes = []
        #self.agents = [Pc("pc 1",1)] # TODO make this a node not a number
        #self.agents = [Greedy("Greed 1", 1)]
        self.agents = [AStarAgent("420Ass_Master_69", 1)]
        self.score = 0
        # update the world for every agent at startup
        for agent in self.agents:
            agent.set_environment(self)

        #self.agents = [Annihilator("Anna frank 1", 3)]
        self.time = 0
        # raise NotImplemented()

    def add_vertex(self, **kwargs):
        """
        Adds a vertex to the environment graph. Will name the vertex with the "name" key that is in data_dict
        if there isn't one, will add a numeric value name to the vertex.
        :param data_dict: (dictionary) the data to be added to the vertex
        :return: None
        """
        vertex_name = kwargs.get("name")
        if not vertex_name:
            vertex_name = self.graph.number_of_nodes() + 1
            kwargs["name"] = vertex_name

        if "deadline" not in kwargs.keys():
            logging.warning("no deadline has been added to the edge {}, will assume weight 10".format(vertex_name))
            kwargs["deadline"] = 2



        self.graph.add_node(vertex_name, **kwargs)

    def add_edge(self, start, end, **kwargs):
        """
        will create an edge between start to end
        :param start: (hashable)  name of the vertex
        :param end: (hashable)    name of the vertex
        :return: None
        """
        if not kwargs.get("weight"):
            logging.warning("no weight has been added to the edge ({},{}), will assume weight 1".format(start,end))
            kwargs["weight"] = 1

        self.graph.add_edge(start, end, **kwargs)
    def change_attr(self,node,attr,value):
        """
        change the attribute of the node to the value
        :param node: (hashable) key to the node
        :param attr: (hashable) key to the attribute
        :param value: value to the attribute
        :return: None
        """
        self.graph.nodes[node][attr] = value

    def get_attr(self,node,attr):
        """
        get the attribute of the node to the value
        :param node: (hashable) key to the node
        :param attr: (hashable) key to the attribute
        :return: value to the attribute of the node
        """
        return self.graph.nodes[node][attr]

    def tick(self):
        """
        calculate the next turn in the environment
        :return: None
        """
        # update the world for every agent
        for agent in self.agents:
            agent.set_environment(self)
            agent.curr_time += 1

        # each agent act on the world at his turn
        for agent in self.agents:
            agent.act(self)

        self._update_environment()

    def get_passable_subgraph(self, at_time=0):
        """
        :at_time: (int) calculate the passable subgraph in the future after at_time ticks
        :return:
        """

        non_destroyed_nodes = [node for node in self.graph.nodes if self.get_attr(node, "deadline") > at_time]
        subgraph = nx.Graph(nx.subgraph(self.graph,non_destroyed_nodes))
        destroyed_edges = [edge for edge in self.graph.edges if self.graph.edges[edge]["blocked"]]
        subgraph.remove_edges_from(destroyed_edges)
        return subgraph

    def calculate_path_time(self, path):
        """
        calculate the time it takes to move in the given path
        :param path: list of hash nodes
        :return: time it takes
        """
        time = 0
        for node_index in range(len(path) - 1):
            time += self.graph.edges[path[node_index], path[node_index + 1]]["weight"]

        return time

    def display(self, save_dir=None):
        """
        display the graph current state.
        :param save_dir: path to save the image. If None, will use plt.show()
        :return: None
        """
        # ---------------display parameters--------------------
        color_dict = {

            # players
            'annihilator': 'red',
            'greedy': 'blue',
            'pc': 'yellow',

            # edges
            'passable': 'black',
            'broken': 'red',

            # nodes
            'shelter': 'green',
            'people': 'purple'

        }


        # -----------------------------------------------------

        # create figure with title
        fig, ax = plt.subplots()
        plt.title("Graph at time: {}".format(self.time))

        # even spaced shell layout
        pos = nx.circular_layout(self.graph, scale=2)
        pos = {node:node_pos*0.5 for node,node_pos in pos.items()}

        # add the weight labels to the figure
        edge_labels = dict([((u, v,), d['weight']) for u, v, d in self.graph.edges(data=True)])
        nx.draw_networkx_edge_labels(self.graph, pos,
                                     edge_labels=edge_labels,
                                     node_size=100)

        self._print_node_data(ax, pos, "people", 1)
        self._print_node_data(ax, pos, "shelter", 2)

        self._print_agents_data(ax, pos)
        # draw the rest of the graph
        nx.draw(self.graph, pos, with_labels=True, font_weight='bold')


        if not save_dir:
            plt.show()

        # raise NotImplemented()

    def _update_environment(self):
        self.time = self.time + 1
        for node in self.graph.nodes:
            print(self.graph.nodes[node]["deadline"])
            if self.graph.nodes[node]["deadline"] > 0:
                self.graph.nodes[node]["deadline"] -= 1
        """for agent in self.agents:
            if (agent.active_state == "terminated"):
                self.active_agents -= 1"""



    def _print_node_data(self, ax, pos, dict_key, spacing):

        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] + spacing*0.08)

        node_attrs = nx.get_node_attributes(self.graph, name=dict_key)
        custom_node_attrs = {}
        for node, attr in node_attrs.items():
            custom_node_attrs[node] = str(dict_key) + ": " + str(attr)

        nx.draw_networkx_labels(self.graph, pos_attrs, labels=custom_node_attrs, font_size=8)

    def _print_agents_data(self, ax, pos):

        for agent in self.agents:
            agent.get_annotation_box(pos, ax)
            if (agent.__getattribute__("score") != None):
                print("Current agent score is: {}".format(agent.score))

    def get_node_neighborhood(self, node_key):
        """
        return a list of the neighbors to the node
        :param node_key: (hashable) the key to the node
        :return:
        """
        return self.graph[node_key]

    def save(self, save_dir):
        """
        Save the environment variable to text
        :param save_dir: save location
        :return: (bool) True if success
        """
        raise NotImplemented()

    def load(self, save_dir):
        """
        does what the save function do, but in reverse.
        :param save_dir:
        :return: (bool) True if success
        """

        raise NotImplemented()

    def is_terminated(self):
        """
        will check if all the agents are terminated ;)
        :return: (bool) true if terminated
        """