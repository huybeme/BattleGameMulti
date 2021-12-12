import socket
import json
import PlayerState
from typing import Dict
import datetime
import arcade
import Client2
import math
import game


class Player(arcade.Sprite):
    def __init__(self, xloc, yloc):
        super().__init__()
        self.center_x = xloc
        self.center_y = yloc
        player_block = arcade.make_soft_square_texture(64, [0, 0, 0])
        self.texture = player_block


# global variables
SERVER_PORT = 25001
all_players: Dict[str, PlayerState.PlayerState] = {}

layer_options = {
    "Water": {"use_spatial_hash": True},
    "Beach": {"use_spatial_hash": True},
    "Ice": {"use_spatial_hash": True},
    "Lower_Decorative": {"use_spatial_hash": True},
    "Solids": {"use_spatial_hash": True},
    "Upper_Decorative": {"use_spatial_hash": True},
}
map_string = "Assets/Battle_Ships_Map_1.json"
game_map = arcade.load_tilemap(map_string, layer_options=layer_options,
                               scaling=game.SPRITE_SCALING_TILES)
wall_list = game_map.sprite_lists["Solids"]
map_scene = arcade.Scene.from_tilemap(game_map)
player1 = Player(0, 0)
player2 = Player(0, 0)


def find_ip_address():
    server_address = ""
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.connect(('10.255.255.255', 1))  # dummy address that doesn't need to be reached
        server_address = connection.getsockname()[0]
    except IOError:
        server_address = '127.0.0.1'  # localhost loopback address
    finally:
        connection.close()
    return server_address


def process_player_movement(player_move: PlayerState.PlayerMovement, client_address: str,
                            gamestate: PlayerState.GameState):
    player_info = gamestate.player_states[client_address[0]]
    now = datetime.datetime.now()
    if player_info.last_update + datetime.timedelta(milliseconds=20) > now:
        return
    player_info.last_update = now
    delta_x = 0
    delta_y = 0

    if player_move.keys[str(arcade.key.UP)] and player_move.keys[str(arcade.key.RIGHT)]:
        player1.center_y += 3
        player1.center_x += 3
        delta_y = 3
        delta_x = 3
        player_info.face_angle = 45
    elif player_move.keys[str(arcade.key.UP)] and player_move.keys[str(arcade.key.LEFT)]:
        player1.center_y += 3
        player1.center_x -= 3
        delta_y = 3
        delta_x = -3
        player_info.face_angle = 135
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.LEFT)]:
        player1.center_y -= 3
        player1.center_x -= 3
        delta_y = -3
        delta_x = -3
        player_info.face_angle = 225
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.RIGHT)]:
        player1.center_y -= 3
        player1.center_x += 3
        delta_y = -3
        delta_x = 3
        player_info.face_angle = 315
    elif player_move.keys[str(arcade.key.UP)]:
        delta_y = 3
        player1.center_y += 3
        player_info.face_angle = 90
    elif player_move.keys[str(arcade.key.DOWN)]:
        delta_y = -3
        player1.center_y -= 3
        player_info.face_angle = 270
    elif player_move.keys[str(arcade.key.LEFT)]:
        player1.center_x -= 3
        delta_x = -3
        player_info.face_angle = 180
    elif player_move.keys[str(arcade.key.RIGHT)]:
        player1.center_x += 3
        delta_x = 3
        player_info.face_angle = 0
    player_info.x_loc += delta_x
    player_info.y_loc += delta_y

    delta_weapon = 0
    if player_move.keys[str(arcade.key.S)] or player_move.keys[str(arcade.key.A)]:
        delta_weapon = -3
    elif player_move.keys[str(arcade.key.W)] or player_move.keys[str(arcade.key.D)]:
        delta_weapon = 3
    player_info.weapon_angle += delta_weapon

    shoot_delay = player_info.bullet_delay + datetime.timedelta(seconds=0.3) < now
    player_info.weapon_shooting = False
    player_info.shooting = False
    if player_move.keys[str(arcade.key.SPACE)] and shoot_delay:
        player_info.shooting = True
        player_info.weapon_shooting = True
        player_info.bullet_delay = now
    if player_move.keys[str(arcade.key.F)] and shoot_delay:
        player_info.shooting = True
        player_info.bullet_delay = now


def check_for_collision(gamestate: PlayerState.GameState, client_address: str):
    cf = 3
    player_info = gamestate.player_states[client_address[0]]
    if player1.collides_with_list(wall_list):
        if player_info.face_angle == 135:
            player_info.x_loc += cf
            player_info.y_loc -= cf
        elif player_info.face_angle == 45:
            player_info.x_loc -= cf
            player_info.y_loc -= cf
        elif player_info.face_angle == 225:
            player_info.x_loc += cf
            player_info.y_loc += cf
        elif player_info.face_angle == 315:
            player_info.x_loc -= cf
            player_info.y_loc += cf
        elif player_info.face_angle == 90:
            player_info.y_loc -= cf
        elif player_info.face_angle == 180:
            player_info.x_loc += cf
        elif player_info.face_angle == 270:
            player_info.y_loc += cf
        elif player_info.face_angle == 0:
            player_info.x_loc -= cf
        player1.set_position(player_info.x_loc, player_info.y_loc)


def main():
    server_address = find_ip_address()
    print(f"Server address is {server_address} on port {SERVER_PORT}")
    gameState = PlayerState.GameState(all_players, False, 1)

    # create a socket and bind it to the address and port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((server_address, SERVER_PORT))

    addresses = []

    # sort who is who for players
    while len(all_players) != 2:
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        if not client_address[0] in all_players and len(all_players) < 2:
            if len(all_players) < 1:
                print(f"player 1: {client_address[0]} added")
                player1_state: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=1, x_loc=80, y_loc=80, face_angle=90, weapon_angle=0, shooting=False, weapon_shooting=False,
                    last_update=datetime.datetime.now(), bullet_delay=datetime.datetime.now()
                )
                player1.set_position(player1_state.x_loc, player1_state.y_loc)
                all_players[client_address[0]] = player1_state
                addresses.append(client_address)
            elif len(all_players) == 1:
                print(f"player 2: {client_address[0]} added")
                player2_state: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=2, x_loc=Client2.SCREEN_WIDTH - 64, y_loc=Client2.SCREEN_HEIGHT - 64, face_angle=270,
                    weapon_angle=0, shooting=False, weapon_shooting=False, last_update=datetime.datetime.now(),
                    bullet_delay=datetime.datetime.now()
                )
                player2.set_position(player2_state.x_loc, player2_state.y_loc)
                all_players[client_address[0]] = player2_state
                addresses.append(client_address)

        # get initial stuff from client, used to send data to client to determine who is who on client side
        json_data = json.loads(message)
        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data
        response = gameState.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)

    # send list of IP addresses to client
    message = json.dumps(addresses)
    UDPServerSocket.sendto(str.encode(message), addresses[0])
    UDPServerSocket.sendto(str.encode(message), addresses[1])

    while (True):
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        json_data = json.loads(message)
        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data
        process_player_movement(player_move, client_address, gameState)
        check_for_collision(gameState, client_address)
        response = gameState.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)



if __name__ == '__main__':
    main()
