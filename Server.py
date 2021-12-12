import asyncio
import socket
import json
import threading

import PlayerState
from typing import Dict
import datetime
import arcade
from random import randint
import pathlib
import game

from arcade import buffered_draw_commands
from arcade import Window

SERVER_PORT = 25001
all_players: Dict[str, PlayerState.PlayerState] = {}


class Player(arcade.Sprite):
    def __init__(self, xloc, yloc):
        super().__init__()
        self.center_x = xloc
        self.center_y = yloc
        player_block = arcade.make_soft_square_texture(64, [0, 0, 0])
        self.texture = player_block


class GameWindow(arcade.Window):
    def __init__(self, player1: Player):
        super().__init__(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, title="server window")

        # self.player2 = player2

        layer_options = {
            "Water": {"use_spatial_hash": True},
            "Beach": {"use_spatial_hash": True},
            "Ice": {"use_spatial_hash": True},
            "Lower_Decorative": {"use_spatial_hash": True},
            "Solids": {"use_spatial_hash": True},
            "Upper_Decorative": {"use_spatial_hash": True},
        }
        map_1_location = pathlib.Path.cwd() / "Assets/Battle_Ships_Map_1.json"
        tile_map1 = arcade.load_tilemap(
            map_1_location,
            layer_options=layer_options,
            scaling=game.SPRITE_SCALING_TILES,
        )
        self.wall_list = tile_map1.sprite_lists["Solids"]
        self.map_scene = arcade.Scene.from_tilemap(tile_map1)

        self.player1 = player1

        self.player1_physics = arcade.PhysicsEngineSimple(self.player1, self.wall_list)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)

    def on_update(self, delta_time: float):
        self.player1_physics.update()
        self.player_list.update()

    def on_draw(self):
        arcade.start_render()
        self.map_scene.draw()
        self.player_list.draw()


    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, key, modifiers):
        pass

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
    speed = 3
    delta_x = 0
    delta_y = 0

    if player_move.keys[str(arcade.key.UP)] and player_move.keys[str(arcade.key.RIGHT)]:
        # delta_y = speed
        # delta_x = speed
        player_info.y_loc += speed
        player_info.x_loc += speed
        player_info.face_angle = 45
    elif player_move.keys[str(arcade.key.UP)] and player_move.keys[str(arcade.key.LEFT)]:
        # delta_y = speed
        # delta_x = -speed
        player_info.y_loc += speed
        player_info.x_loc -= speed
        player_info.face_angle = 135
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.LEFT)]:
        # delta_y = -speed
        # delta_x = -speed
        player_info.y_loc -= speed
        player_info.x_loc -= speed
        player_info.face_angle = 225
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.RIGHT)]:
        # delta_y = -speed
        # delta_x = speed
        player_info.y_loc -= speed
        player_info.x_loc += speed
        player_info.face_angle = 315
    elif player_move.keys[str(arcade.key.UP)]:
        # delta_y = speed
        player_info.y_loc += speed
        player_info.face_angle = 90
    elif player_move.keys[str(arcade.key.DOWN)]:
        # delta_y = -speed
        player_info.y_loc -= speed
        player_info.face_angle = 270
    elif player_move.keys[str(arcade.key.LEFT)]:
        # delta_x = -speed
        player_info.x_loc -= speed
        player_info.face_angle = 180
    elif player_move.keys[str(arcade.key.RIGHT)]:
        # delta_x = speed
        player_info.x_loc += speed
        player_info.face_angle = 0
    # player_info.x_loc += delta_x
    # player_info.y_loc += delta_y

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


def check_if_at_item(player: PlayerState.PlayerMovement, item: PlayerState.ItemState, gamestate: PlayerState.GameState):
    item_info = gamestate.item
    if not item_info.present:
        item_info.x_loc = randint(16, game.SCREEN_WIDTH - 16)
        item_info.y_loc = randint(16, game.SCREEN_HEIGHT - 16)
        item_info.rand_power_up = randint(0, 2)
        item_info.present = True


def check_for_map_collision(player, tile):
    wall_list = tile.sprite_lists["Solids"]
    player_physics = arcade.PhysicsEngineSimple(player, wall_list)
    dimension = 100
    p1 = (-dimension / 2, -dimension / 2)
    p2 = (dimension / 2, -dimension / 2)
    p3 = (dimension / 2, dimension / 2)
    p4 = (-dimension / 2, dimension / 2)
    hit_box_points = p1, p2, p3, p4
    shape = buffered_draw_commands.create_line_loop(point_list=hit_box_points,
                                                    color=arcade.csscolor.HOTPINK, line_width=1)
    hit_box_shape = buffered_draw_commands.ShapeElementList()
    hit_box_shape.append(shape)
    hit_box_shape.center_x = player.center_x
    hit_box_shape.center_y = player.center_y
    hit_box_shape.draw()

    player.set_hit_box(points=hit_box_points)
    player_physics.update()


def setup_server_connection(server: GameWindow, gamestate, server_address, UDPServerSocket):
    server_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_event_loop)
    server_event_loop.create_task(communication_with_client(server, server_event_loop, gamestate, server_address, UDPServerSocket))
    server_event_loop.run_forever()


async def communication_with_client(server: GameWindow, event_loop, gamestate, server_address, UDPServerSocket):

    while (True):
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        json_data = json.loads(message)

        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data
        process_player_movement(player_move, client_address, gamestate)
        response = gamestate.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)

        player1_info: PlayerState.PlayerState = gamestate.player_states[client_address[0]]
        server.player1.center_x = player1_info.x_loc
        server.player1.center_y = player1_info.y_loc
        server.player1_physics.update()


def main():
    server_address = find_ip_address()
    print(f"Server address is {server_address} on port {SERVER_PORT}")
    items = PlayerState.ItemState(randint(16, game.SCREEN_WIDTH - 16), randint(16, game.SCREEN_HEIGHT - 16),
                                  randint(0, 2), False, datetime.datetime.now())
    gameState = PlayerState.GameState(all_players, items)

    # create a socket and bind it to the address and port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((server_address, SERVER_PORT))

    addresses = []
    player_info = None

    # # sort who is who for players
    while len(all_players) != 1:
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        if not client_address[0] in all_players and len(all_players) < 2:
            if len(all_players) < 1:
                print(f"player 1: {client_address[0]} added")
                player1: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=1, x_loc=80, y_loc=80, face_angle=90, weapon_angle=0, shooting=False, weapon_shooting=False,
                    last_update=datetime.datetime.now(),
                    bullet_delay=datetime.datetime.now()
                )
                all_players[client_address[0]] = player1
                addresses.append(client_address)
            elif len(all_players) == 1:
                print(f"player 2: {client_address[0]} added")
                player2: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=2, x_loc=game.SCREEN_WIDTH - 64, y_loc=game.SCREEN_HEIGHT - 64, face_angle=270,
                    weapon_angle=0, shooting=False, weapon_shooting=False, last_update=datetime.datetime.now(),
                    bullet_delay=datetime.datetime.now()
                )
                all_players[client_address[0]] = player2
                addresses.append(client_address)

        # get initial stuff from client, used to send data to client to determine who is who on client side
        json_data = json.loads(message)
        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data
        response = gameState.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)
    print("all players connected")

    player_info = gameState.player_states[addresses[0][0]]
    player = Player(player_info.y_loc, player_info.y_loc)

    # send list of IP addresses to client
    message = json.dumps(addresses)
    UDPServerSocket.sendto(str.encode(message), addresses[0])
    # UDPServerSocket.sendto(str.encode(message), addresses[1])
    print("addresses sent")

    window = GameWindow(player)

    server_thread = threading.Thread(target=setup_server_connection, args=(window, gameState, server_address, UDPServerSocket),
                                     daemon=True)
    server_thread.start()
    arcade.run()


if __name__ == '__main__':
    main()
