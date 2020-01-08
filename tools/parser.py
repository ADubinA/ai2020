import json

class Parser:
    def __init__(self, file_name):
        opened_file = open(file_name)
        data_dict = json.load(opened_file)
        self.vertex_list = data_dict["vertexes"]
        self.edge_list = data_dict["edges"]
        pass
