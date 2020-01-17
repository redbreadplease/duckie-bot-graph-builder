from graphviz import Digraph

TURN_RIGHT, TURN_LEFT, STRAIGHT = 'TURN_RIGHT', 'TURN_LEFT', 'STRAIGHT'


def get_vertex_id_by_qr(vertex_qr_code: int):
    return vertex_qr_code


def get_turn_types_by_qr(turns_qr_code: int):
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
        return STRAIGHT


def get_reversed_turn_type(turn_type):
    if turn_type == TURN_RIGHT:
        return TURN_LEFT
    elif turn_type == TURN_LEFT:
        return TURN_RIGHT
    else:
        return STRAIGHT


def insert_to_dict(d: dict, key, value):
    if key in list(d.keys()):
        if value not in d[key]:
            d[key].append(value)
    else:
        d[key] = [value]
    return d


class TripleVertex:
    def __init__(self, v1_id: int, v2_id: int, v3_id: int, turn_type_between):
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.v3_id = v3_id
        self.turn_type_between = turn_type_between

    def __repr__(self):
        return 'v1: ' + str(self.v1_id) + '  v2: ' + str(self.v2_id) + '  v3: ' + str(
            self.v3_id) + '  turn type: ' + self.turn_type_between


class VertexPair:
    def __init__(self, v1_id: int, v2_id: int, turn_type):
        self.v1_id = v1_id
        self.v2_id = v2_id
        self.turn_type = turn_type

    def __repr__(self):
        return 'v1: ' + str(self.v1_id) + '  v2: ' + str(self.v2_id), '  turn_type: ' + self.turn_type

    def is_equal(self, to_compare_with):
        if self.v1_id in [to_compare_with.v1_id, to_compare_with.v2_id] and \
                self.v2_id in [to_compare_with.v1_id, to_compare_with.v2_id] and \
                self.turn_type == to_compare_with.turn_type:
            return True
        else:
            return False


def is_vertex_pair_here(vertex_pairs: list, checking_vertex_pair: VertexPair):
    for cur_vertex_pair in vertex_pairs:
        if checking_vertex_pair.is_equal(to_compare_with=cur_vertex_pair):
            return True
    return False


class GraphBuilder:
    def __init__(self):
        self.graph = Digraph('G', filename='graph.gv')
        self.last_vertex_id = None
        self.last_turn_type = None
        self.pre_last_vertex_id = None
        self.graph = Digraph('G', filename='hello.gv', engine='sfdp')
        self.triple_vertexes = list()
        self.dif_vertexes_ids = list()

    def update_state(self, vertex_id: int, last_turn_type):
        self.pre_last_vertex_id = self.last_vertex_id
        self.last_vertex_id = vertex_id
        self.last_turn_type = last_turn_type

    def get_state(self):
        return 'Last vertex id: ' + str(self.last_vertex_id) + '  pre last vertex id: ' + str(
            self.pre_last_vertex_id) + '  last turned type: ' + str(self.last_turn_type)

    def get_optimal_turns(self, prev_last_ver_id: int, last_ver_id: int, turns_qr_code: int):
        possible_turns = get_turn_types_by_qr(turns_qr_code=turns_qr_code)
        old_data = self.triple_vertexes
        for triple_vertexe in old_data:
            try:
                if triple_vertexe.v1_id == prev_last_ver_id and triple_vertexe.v2_id == last_ver_id:
                    possible_turns.remove(triple_vertexe.turn_type_between)
            except ValueError:
                print('Cannot remove. Has: ', possible_turns, '  trying remove: ', triple_vertexe.turn_type_between)
            try:
                if triple_vertexe.v3_id == prev_last_ver_id and triple_vertexe.v2_id == last_ver_id:
                    possible_turns.remove(get_reversed_turn_type(triple_vertexe.turn_type_between))
            except ValueError:
                print('Cannot remove. Has: ', possible_turns, '  trying remove: ',
                      get_reversed_turn_type(triple_vertexe.turn_type_between))
        return possible_turns

    def add_triple_vertex(self, v1_id: int, v2_id: int, v3_id: int, turn_type):
        old_data = self.triple_vertexes
        old_data.append(TripleVertex(v1_id=v1_id, v2_id=v2_id, v3_id=v3_id, turn_type_between=turn_type))

    def is_graph_built(self):
        if not self.dif_vertexes_ids:
            return False
        from_first_vertex_to_another_connections = dict()
        for triple_vertex in self.triple_vertexes:
            v1, v2, v3 = triple_vertex.v1_id, triple_vertex.v2_id, triple_vertex.v3_id
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v1, value=v2)
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v1, value=v3)
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v2, value=v1)
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v3, value=v1)
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v2, value=v3)
            from_first_vertex_to_another_connections = insert_to_dict(d=from_first_vertex_to_another_connections,
                                                                      key=v3, value=v2)
        summary = 0
        for arr in list(from_first_vertex_to_another_connections.values()):
            summary += len(arr)
        return summary == len(self.dif_vertexes_ids) * 3

    def get_next_turn(self, vertex_qr_code: int, turns_qr_code: int):
        cur_vertex = get_vertex_id_by_qr(vertex_qr_code=vertex_qr_code)

        if self.is_graph_built():
            return -1

        if cur_vertex not in self.dif_vertexes_ids:
            self.dif_vertexes_ids.append(cur_vertex)

        if self.last_vertex_id is None or self.pre_last_vertex_id is None:
            to_turn_to = get_turn_types_by_qr(turns_qr_code=turns_qr_code)[0]
            self.update_state(vertex_id=cur_vertex, last_turn_type=to_turn_to)
        else:
            to_turn_to = self.get_optimal_turns(prev_last_ver_id=self.pre_last_vertex_id,
                                                last_ver_id=self.last_vertex_id, turns_qr_code=turns_qr_code)
            if not to_turn_to:
                to_turn_to = get_turn_types_by_qr(turns_qr_code=turns_qr_code)
            to_turn_to = to_turn_to[0]
            self.add_triple_vertex(v1_id=self.pre_last_vertex_id, v2_id=self.last_vertex_id, v3_id=cur_vertex,
                                   turn_type=to_turn_to)
            self.update_state(vertex_id=cur_vertex, last_turn_type=to_turn_to)
        return get_turn_code_by_turn_type(to_turn_to)

    def visualize(self):
        old_data = self.triple_vertexes
        vertex_pairs = list()
        for triple_vertex in old_data:
            vertex_pair1, vertex_pair2 = VertexPair(v1_id=triple_vertex.v1_id, v2_id=triple_vertex.v2_id,
                                                    turn_type=triple_vertex.turn_type_between), VertexPair(
                v1_id=triple_vertex.v3_id, v2_id=triple_vertex.v2_id, turn_type=triple_vertex.turn_type_between)
            if not is_vertex_pair_here(vertex_pairs=vertex_pairs, checking_vertex_pair=vertex_pair1):
                vertex_pairs.append(vertex_pair1)
            if not is_vertex_pair_here(vertex_pairs=vertex_pairs, checking_vertex_pair=vertex_pair2):
                vertex_pairs.append(vertex_pair2)
        for vertex_pair in vertex_pairs:
            self.graph.edge(str(vertex_pair.v1_id), str(vertex_pair.v2_id))
        self.graph.view()
        self.graph.clear()
