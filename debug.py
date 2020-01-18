from graph import GraphBuilder


def get_vertex_qr_code():
    print('Write vertex qr code:', end=' ')
    try:
        return int(input())
    except ValueError:
        print('Try again:', end=' ')
        return int(input())


def convert_turn_qr_code(turn_qr_code):
    return turn_qr_code + 8


def get_turns_qr_code():
    print('Write turn qr code:', end=' ')
    try:
        return int(input())
    except ValueError:
        print('Try again: ')
        return int(input())


def convert_to_turn_string(turn_code):
    if turn_code == 0:
        return 'TURN LEFT!'
    if turn_code == 1:
        return 'Go STRAIGHT!'
    if turn_code == 2:
        return 'TURN RIGHT!'
    if turn_code == -1:
        return 'GRAPH BUILT!'
    else:
        return 'Something strange: ' + str(turn_code)


gb = GraphBuilder()

for i in range(100):
    print(convert_to_turn_string(
        gb.get_next_turn(vertex_qr_code=get_vertex_qr_code(), turns_qr_code=convert_turn_qr_code(get_turns_qr_code()))))
    print(gb.get_state())
    if i > 3:
        gb.visualize()
