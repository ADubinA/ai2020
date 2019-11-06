import json

class Parser:
    def __init__(self, file_name):
        opened_file = open(file_name)
        data_dict = json.load(opened_file)
        self.vertex_list = self.create_vertexes(data_dict["vertexes"])
        self.edge_list = self.create_edges(data_dict["edges"])
        pass

    def create_vertexes(self, vertex_dict):
        vertex_arr = []
        for entry in vertex_dict:
            vertex_arr.append(self.handle_single_vertex(entry))
        return vertex_arr

    def handle_single_vertex(self, single_entry):
        ret_vertex = []
        ret_vertex.append(single_entry["name"])
        single_entry.pop("name")
        ret_vertex.append(single_entry)
        return ret_vertex

    def create_edges(self, edge_dict):
        edge_arr = []
        for entry in edge_dict:
            edge_arr.append(self.handle_single_edge(enftry))
        return edge_arr

    def handle_single_edge(self, single_entry):
        ret_edge = []
        ret_edge.append(single_entry["from"])
        ret_edge.append(single_entry["to"])
        single_entry.pop("from")
        single_entry.pop("to")
        ret_edge.append(single_entry)
        return ret_edge