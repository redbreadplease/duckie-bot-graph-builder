from graphviz import Graph

import copy

TURN_RIGHT, TURN_LEFT, STRAIGHT = 'TURN_RIGHT', 'TURN_LEFT', 'STRAIGHT'


def get_vertex_id_by_qr(vertex_qr_code):
    # vertex_qr_code: int
    return vertex_qr_code


def get_turn_types_by_qr(turns_qr_code):
    # turns_qr_code: int
    if turns_qr_code == 9:
        return [STRAIGHT, TURN_RIGHT]
    elif turns_qr_code == 10:
        return [TURN_LEFT, STRAIGHT]
    else:
        return [TURN_LEFT, TURN_RIGHT]


def get_turn_code_by_turn_type(turn_type):
    if turn_type == TURN_RIGHT:
        return 2
    if turn_type == TURN_LEFT:
        return 0
    else:
        return 1


def get_reversed_turn_type(turn_type):
    if turn_type == TURN_RIGHT:
        return TURN_LEFT
    elif turn_type == TURN_LEFT:
        return TURN_RIGHT
    else:
        return STRAIGHT


class TripleVertex:
    def __init__(self, v1_id, v2_id, v3_id, turn_type_between):
        # v1_id: int, v2_id: int, v3_id: int
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.v3_id = v3_id
        self.turn_type_between = turn_type_between

    def to_string(self):
        return 'v1: ' + str(self.v1_id) + '  v2: ' + str(self.v2_id) + '  v3: ' + str(
            self.v3_id) + '  turn type: ' + self.turn_type_between

    def __repr__(self):
        return 'v1: ' + str(self.v1_id) + '  v2: ' + str(self.v2_id) + '  v3: ' + str(
            self.v3_id) + '  turn type: ' + self.turn_type_between


class VertexPair:
    def __init__(self, v1_id, v2_id, turn_type):
        # v1_id: int, v2_id: int
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.turn_type = turn_type

    def __repr__(self):
        return 'v1: ' + str(self.v1_id) + '  v2: ' + str(self.v2_id), '  turn_type: ' + self.turn_type

    def is_equal(self, to_compare_with):
        if self.v1_id in [to_compare_with.v1_id, to_compare_with.v2_id] and \
                self.v2_id in [to_compare_with.v1_id, to_compare_with.v2_id]:
            return True
        else:
            return False


def is_vertex_pair_here(vertex_pairs, checking_vertex_pair):
    # vertex_pairs: list, checking_vertex_pair: VertexPair
    for cur_vertex_pair in vertex_pairs:
        if checking_vertex_pair.is_equal(to_compare_with=cur_vertex_pair):
            return True
    return False


class GraphBuilder:
    def __init__(self):
        self.last_vertex_id = None
        self.last_turn_type = None
        self.pre_last_vertex_id = None
        self.graph = Graph('G', filename='graph.gv')
        self.triple_vertexes = list()
        self.dif_vertexes_ids = list()
        self.from_first_vertex_to_another_connections = dict()
        self.vertexes_path_ids = list()
        self.vertex_path_to_id = None
        self.vertexes_path_turns_types = list()

    def update_state(self, vertex_id, last_turn_type):
        # vertex_id: int
        self.pre_last_vertex_id = self.last_vertex_id
        self.last_vertex_id = vertex_id
        self.last_turn_type = last_turn_type

    def get_state(self):
        return 'Last vertex id: ' + str(self.last_vertex_id) + '  pre last vertex id: ' + str(
            self.pre_last_vertex_id) + '  last turned type: ' + str(self.last_turn_type)

    def get_optimal_turns(self, prev_last_ver_id, last_ver_id, turns_qr_code):
        # prev_last_ver_id: int, last_ver_id: int, turns_qr_code: int
        possible_turns = get_turn_types_by_qr(turns_qr_code=turns_qr_code)
        old_data = self.triple_vertexes
        for triple_vertex in old_data:
            try:
                if triple_vertex.v1_id == prev_last_ver_id and triple_vertex.v2_id == last_ver_id:
                    possible_turns.remove(triple_vertex.turn_type_between)
            except ValueError:
                print('Cannot remove. Has: ', possible_turns, '  trying remove: ', triple_vertex.turn_type_between)
            try:
                if triple_vertex.v3_id == prev_last_ver_id and triple_vertex.v2_id == last_ver_id:
                    possible_turns.remove(get_reversed_turn_type(triple_vertex.turn_type_between))
            except ValueError:
                print('Cannot remove. Has: ', possible_turns, '  trying remove: ',
                      get_reversed_turn_type(triple_vertex.turn_type_between))
        return possible_turns

    def add_triple_vertex(self, v1_id, v2_id, v3_id, turn_type):
        # v1_id: int, v2_id: int, v3_id: int
        old_data = self.triple_vertexes
        old_data.append(TripleVertex(v1_id=v1_id, v2_id=v2_id, v3_id=v3_id, turn_type_between=turn_type))

    def is_graph_built(self):
        if not self.dif_vertexes_ids or not self.triple_vertexes:
            return False
        triple_vertex = self.triple_vertexes[-1]
        v1, v2, v3 = triple_vertex.v1_id, triple_vertex.v2_id, triple_vertex.v3_id
        if v2 not in self.from_first_vertex_to_another_connections[v1]:
            self.from_first_vertex_to_another_connections[v1].append(v2)
        if v2 not in self.from_first_vertex_to_another_connections[v3]:
            self.from_first_vertex_to_another_connections[v3].append(v2)
        if v1 not in self.from_first_vertex_to_another_connections[v2]:
            self.from_first_vertex_to_another_connections[v2].append(v1)
        if v1 not in self.from_first_vertex_to_another_connections[v3]:
            self.from_first_vertex_to_another_connections[v3].append(v1)
        if v3 not in self.from_first_vertex_to_another_connections[v1]:
            self.from_first_vertex_to_another_connections[v1].append(v3)
        if v3 not in self.from_first_vertex_to_another_connections[v2]:
            self.from_first_vertex_to_another_connections[v2].append(v3)
        summary = 0
        print(self.from_first_vertex_to_another_connections)
        for arr in list(self.from_first_vertex_to_another_connections.values()):
            summary += len(arr)
        return bool(summary >= len(self.dif_vertexes_ids) * 3)

    def write_down_triple_vertexes(self):
        with open('TripleVertexes.txt', 'w') as f:
            for triple_vertex in self.triple_vertexes:
                f.write(triple_vertex.to_string())
                f.write("\n")

    def make_wave(self, vertexes_path_ids_temp):
        last_vertex_checked = vertexes_path_ids_temp[-1]
        if last_vertex_checked == self.vertex_path_to_id:
            if len(self.vertexes_path_ids) > len(vertexes_path_ids_temp) or not self.vertexes_path_ids:
                self.vertexes_path_ids = copy.copy(vertexes_path_ids_temp)
        else:
            vertexes_to_check = self.from_first_vertex_to_another_connections[last_vertex_checked]
            for vertex_to_check in vertexes_to_check:
                if vertex_to_check not in vertexes_path_ids_temp:
                    vertexes_path_ids_temp_copy = copy.copy(vertexes_path_ids_temp)
                    vertexes_path_ids_temp_copy.append(vertex_to_check)
                    self.make_wave(vertexes_path_ids_temp=vertexes_path_ids_temp_copy)

    def get_optimal_way_vertexes_ids(self, vertex_from_id, vertex_to_id):
        # vertex_from: int, vertex_to: int
        self.vertex_path_to_id = vertex_to_id
        self.make_wave(vertexes_path_ids_temp=[vertex_from_id])

    def get_turn_type_by_path(self, v1_id, v2_id, v3_id):
        for triple_vertex in self.triple_vertexes:
            if v1_id == triple_vertex.v1_id and v2_id == triple_vertex.v2_id and v3_id == triple_vertex.v3_id:
                return triple_vertex.turn_type_between
            elif v3_id == triple_vertex.v1_id and v2_id == triple_vertex.v2_id and v1_id == triple_vertex.v3_id:
                return get_reversed_turn_type(turn_type=triple_vertex.turn_type_between)
        print('Error: No way to get from: ' + str(v1_id) + '  through: ' + str(v2_id) + '  to: ' + str(v3_id))
        return STRAIGHT

    def find_first_undiscovered_vertex_id(self):
        for vertex_connections_key in self.from_first_vertex_to_another_connections.keys():
            if len(self.from_first_vertex_to_another_connections[vertex_connections_key]) < 3:
                return vertex_connections_key
        print('Error: All vertexes have discovered')
        return -1

    def find_optimal_way_to_undiscovered_vertex(self, vertex_from_id, vertex_to_id):
        self.get_optimal_way_vertexes_ids(vertex_from_id=vertex_from_id, vertex_to_id=vertex_to_id)
        optimal_way_to_undiscovered_vertex_ids = self.vertexes_path_ids
        for i in range(len(optimal_way_to_undiscovered_vertex_ids) - 2):
            self.vertexes_path_turns_types.append(
                self.get_turn_type_by_path(v1_id=optimal_way_to_undiscovered_vertex_ids[i],
                                           v2_id=optimal_way_to_undiscovered_vertex_ids[i + 1],
                                           v3_id=optimal_way_to_undiscovered_vertex_ids[i + 2]))

    def get_next_step_turn_type(self):
        turn_type_to_return = self.vertexes_path_turns_types[0]
        self.vertexes_path_turns_types.pop(0)
        return turn_type_to_return

    def get_next_turn(self, vertex_qr_code, turns_qr_code):
        #  vertex_qr_code: int, turns_qr_code: int
        cur_vertex = get_vertex_id_by_qr(vertex_qr_code=vertex_qr_code)

        if self.is_graph_built():
            self.write_down_triple_vertexes()
            return -1

        if self.vertexes_path_turns_types:
            return self.get_next_step_turn_type()

        if cur_vertex not in self.dif_vertexes_ids:
            self.dif_vertexes_ids.append(cur_vertex)
            self.from_first_vertex_to_another_connections[cur_vertex] = list()

        if self.last_vertex_id is None or self.pre_last_vertex_id is None:
            to_turn_to = get_turn_types_by_qr(turns_qr_code=turns_qr_code)[0]
            self.update_state(vertex_id=cur_vertex, last_turn_type=to_turn_to)
        else:
            to_turn_to = self.get_optimal_turns(prev_last_ver_id=self.pre_last_vertex_id,
                                                last_ver_id=self.last_vertex_id, turns_qr_code=turns_qr_code)
            if not to_turn_to:
                vertex_id_to_go = self.find_first_undiscovered_vertex_id()
                print('We\'re going to go to the ' + str(vertex_id_to_go) + ' vertex')
                self.find_optimal_way_to_undiscovered_vertex(vertex_from_id=cur_vertex, vertex_to_id=vertex_id_to_go)
                return self.get_next_step_turn_type()

            to_turn_to = to_turn_to[0]
            self.add_triple_vertex(v1_id=self.pre_last_vertex_id, v2_id=self.last_vertex_id, v3_id=cur_vertex,
                                   turn_type=to_turn_to)
            self.update_state(vertex_id=cur_vertex, last_turn_type=to_turn_to)
        return get_turn_code_by_turn_type(to_turn_to)

    def visualize(self):
        for vertex_connections_key in self.from_first_vertex_to_another_connections.keys():
            for vertex_connections_value in self.from_first_vertex_to_another_connections[vertex_connections_key]:
                self.graph.edge(str(vertex_connections_key), str(vertex_connections_value))
        self.graph.save()
        self.graph.clear()
        self.graph = Graph('G', filename='graph.gv')
