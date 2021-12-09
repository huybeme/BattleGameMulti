import socket
import json
import PlayerState
from typing import Dict
import datetime
import arcade

import game

SERVER_PORT = 25001
all_players: Dict[str, PlayerState.PlayerState] = {}

def find_ip_address():
    server_address = ""
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.connect(('10.255.255.255', 1))   # dummy address that doesn't need to be reached
        server_address = connection.getsockname()[0]
    except IOError:
        server_address = '127.0.0.1'    # localhost loopback address
    finally:
        connection.close()
    return server_address

def process_player_movement(player_move: PlayerState.PlayerMovement, client_address: str, gamestate: PlayerState.GameState):
    player_info = gamestate.player_states[client_address[0]]
    now = datetime.datetime.now()
    if player_info.last_update + datetime.timedelta(milliseconds=20) > now:
        return
    player_info.last_update = now
    delta_x = 0
    delta_y = 0

    if player_move.keys[str(arcade.key.UP)]:
        delta_y = 3
    elif player_move.keys[str(arcade.key.DOWN)]:
        delta_y = -3
    elif player_move.keys[str(arcade.key.LEFT)]:
        delta_x = -3
    elif player_move.keys[str(arcade.key.RIGHT)]:
        delta_x = 3

    player_info.x_loc += delta_x
    player_info.y_loc += delta_y


def main():

    server_address = find_ip_address()
    print(f"Server address is {server_address} on port {SERVER_PORT}")
    gameState = PlayerState.GameState(all_players)

    # create a socket and bind it to the address and port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((server_address, SERVER_PORT))

    while(True):
        data_packet = UDPServerSocket.recvfrom(1024)    # sets the packet size, next lines won't run until this receives
        message = data_packet[0]            # data stored here within tuple
        client_address = data_packet[1]     # client IP addr is stored here, nothing beyond [1]

        if not client_address[0] in all_players:
            print(f"player: {client_address[0]} added")
            first_player: PlayerState.PlayerState = PlayerState.PlayerState(80, 80, 0, datetime.datetime.now())
            all_players[client_address[0]] = first_player


        json_data = json.loads(message)
        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data
        process_player_movement(player_move, client_address, gameState)
        response = gameState.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)

if __name__ == '__main__':
    main()