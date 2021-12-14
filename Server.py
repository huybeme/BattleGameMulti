import asyncio
import socket
import json
import threading

import PlayerState
from typing import Dict
import datetime
import arcade
import Client2
import math
import game
import pathlib


class Player(arcade.Sprite):
    def __init__(self, xloc, yloc, player_num):
        super().__init__()
        self.center_x = xloc
        self.center_y = yloc

        if player_num == 1:
            self.texture = arcade.load_texture("./Assets/Player/pirateship.png")
            self.scale = 0.75
        else:
            self.texture = arcade.load_texture("./Assets/Player/lapras_start.png")
            self.scale = 1

        self.is_shooting = False
        self.weapon_shooting = False
        self.face_angle = None
        self.weapon_angle = None

        self.bullet_change_x = None
        self.bullet_change_y = None
        self.num_bullets = 3


class Bullet(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("./Assets/Player/spike_ball/spike_ball.png")
        self.scale = 0.15


class GameWindow(arcade.Window):
    def __init__(self, player1: Player, player2: Player):
        super().__init__(game.SCREEN_WIDTH, game.SCREEN_HEIGHT, title="server window")

        map_1_location = pathlib.Path.cwd() / "Assets/Battle_Ships_Map_1.json"
        tile_map1 = arcade.load_tilemap(
            map_1_location,
            layer_options=layer_options,
            scaling=game.SPRITE_SCALING_TILES,
        )
        self.wall_list = tile_map1.sprite_lists["Solids"]
        self.map_scene = arcade.Scene.from_tilemap(tile_map1)

        self.player1 = player1
        self.player2 = player2

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player1)
        self.player_list.append(self.player2)

        self.bullet_list = arcade.SpriteList()

    def on_update(self, delta_time: float):
        if self.player1.is_shooting or self.player2.is_shooting:
            bullet = Bullet()
            if self.player1.is_shooting:
                bullet.change_x = self.player1.bullet_change_x
                bullet.change_y = self.player1.bullet_change_y
                bullet.set_position(player1.center_x + (7 * bullet.change_x), player1.center_y + (7 * bullet.change_y))
            else:
                bullet.change_x = self.player2.bullet_change_x
                bullet.change_y = self.player2.bullet_change_y
                bullet.set_position(player2.center_x + (7 * bullet.change_x), player2.center_y + (7 * bullet.change_y))
            self.bullet_list.append(bullet)

        for bullet in self.bullet_list:
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()
            if arcade.check_for_collision_with_list(bullet, self.player_list):
                bullet.remove_from_sprite_lists()

        self.player_list.update()

    def on_draw(self):
        arcade.start_render()
        self.map_scene.draw()
        self.player_list.draw()
        self.bullet_list.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        pass

    def on_key_release(self, key, modifiers):
        pass


# global variables
SERVER_PORT = 25001
all_players: Dict[str, PlayerState.PlayerState] = {}

player1 = Player(0, 0, 1)
player2 = Player(0, 0, 2)

player_list = arcade.SpriteList()
player_list.append(player1)
player_list.append(player2)
bullet_list = arcade.SpriteList()
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
map_scene.add_sprite_list("players", sprite_list=player_list)
game_count = 0


def setup_server_connection(server: GameWindow, gamestate, server_address, UDPServerSocket):
    server_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_event_loop)
    server_event_loop.create_task(
        communication_with_client(server, server_event_loop, gamestate, server_address, UDPServerSocket))
    server_event_loop.run_forever()


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
        if player_info.id == 1:
            player1.center_y += 3
            player1.center_x += 3
        elif player_info.id == 2:
            player2.center_y += 3
            player2.center_x += 3
        delta_y = 3
        delta_x = 3
        player_info.face_angle = 45
    elif player_move.keys[str(arcade.key.UP)] and player_move.keys[str(arcade.key.LEFT)]:
        if player_info.id == 1:
            player1.center_y += 3
            player1.center_x -= 3
        elif player_info.id == 2:
            player2.center_y += 3
            player2.center_x -= 3
        delta_y = 3
        delta_x = -3
        player_info.face_angle = 135
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.LEFT)]:
        if player_info.id == 1:
            player1.center_y -= 3
            player1.center_x -= 3
        elif player_info.id == 2:
            player2.center_y -= 3
            player2.center_x -= 3
        delta_y = -3
        delta_x = -3
        player_info.face_angle = 225
    elif player_move.keys[str(arcade.key.DOWN)] and player_move.keys[str(arcade.key.RIGHT)]:
        if player_info.id == 1:
            player1.center_y -= 3
            player1.center_x += 3
        elif player_info.id == 2:
            player2.center_y -= 3
            player2.center_x += 3
        delta_y = -3
        delta_x = 3
        player_info.face_angle = 315
    elif player_move.keys[str(arcade.key.UP)]:
        if player_info.id == 1:
            player1.center_y += 3
        elif player_info.id == 2:
            player2.center_y += 3
        delta_y = 3
        player_info.face_angle = 90
    elif player_move.keys[str(arcade.key.DOWN)]:
        if player_info.id == 1:
            player1.center_y -= 3
        elif player_info.id == 2:
            player2.center_y -= 3
        delta_y = -3
        player_info.face_angle = 270
    elif player_move.keys[str(arcade.key.LEFT)]:
        if player_info.id == 1:
            player1.center_x -= 3
        elif player_info.id == 2:
            player2.center_x -= 3
        delta_x = -3
        player_info.face_angle = 180
    elif player_move.keys[str(arcade.key.RIGHT)]:
        if player_info.id == 1:
            player1.center_x += 3
        elif player_info.id == 2:
            player2.center_x += 3
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

    # shoot_delay = player_info.bullet_delay + datetime.timedelta(seconds=0.3) < now
    # player_info.weapon_shooting = False
    # player_info.shooting = False
    # if player_move.keys[str(arcade.key.SPACE)] and shoot_delay:
    #     player_info.shooting = True
    #     player_info.weapon_shooting = True
    #     player_info.bullet_delay = now
    #     player_info.num_bullets -= 1
    # if player_move.keys[str(arcade.key.F)] and shoot_delay:
    #     player_info.shooting = True
    #     player_info.bullet_delay = now
    #     player_info.num_bullets -= 1


def update_game_state(game_info: PlayerState.GameInformation, gamestate: PlayerState.GameState):
    global map_string
    global game_map
    global wall_list
    global map_scene
    map_string = f"Assets/Battle_Ships_Map_{game_info.level_num}.json"
    game_map = arcade.load_tilemap(map_string, layer_options=layer_options,
                                   scaling=game.SPRITE_SCALING_TILES)
    wall_list = game_map.sprite_lists["Solids"]
    map_scene = arcade.Scene.from_tilemap(game_map)
    print("moving onto next round")


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

    if player2.collides_with_list(wall_list):
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
        player2.set_position(player_info.x_loc, player_info.y_loc)


def process_player_shooting(gamestate: PlayerState.GameState, client_address: str,
                            player_move: PlayerState.PlayerMovement):
    now = datetime.datetime.now()
    player_info = gamestate.player_states[client_address[0]]

    if player_info.last_update + datetime.timedelta(milliseconds=20) > now:
        return
    shoot_delay = player_info.bullet_delay + datetime.timedelta(seconds=0.3) < now
    player_info.weapon_shooting = False
    player_info.shooting = False
    if player_info.id == 1:
        player1.is_shooting = player_info.shooting
        player1.weapon_shooting = player_info.weapon_shooting
    if player_info.id == 2:
        player2.is_shooting = player_info.shooting
        player2.weapon_shooting = player_info.weapon_shooting

    if player_move.keys[str(arcade.key.SPACE)] and shoot_delay:
        player_info.shooting = True
        player_info.weapon_shooting = True
        player_info.bullet_delay = now
        player_info.num_bullets -= 1

        if player_info.id == 1:
            player1.is_shooting = player_info.shooting
            player1.weapon_shooting = player_info.weapon_shooting
            player1.num_bullets -= 1
        if player_info.id == 2:
            player2.is_shooting = player_info.shooting
            player2.weapon_shooting = player_info.weapon_shooting
            player2.num_bullets -= 1
    if player_move.keys[str(arcade.key.F)] and shoot_delay:
        player_info.shooting = True
        player_info.bullet_delay = now
        player_info.num_bullets -= 1

        if player_info.id == 1:
            player1.is_shooting = player_info.shooting
            player1.num_bullets -= 1
        if player_info.id == 2:
            player2.is_shooting = player_info.shooting
            player2.num_bullets -= 1

    dist_to_next_point = 10
    cf = 7

    global bullet_list
    global map_scene
    if player_info.shooting:
        bullet = Bullet()
        if player_info.weapon_shooting:
            bullet.change_x = math.cos(math.radians(player_info.weapon_angle)) * dist_to_next_point
            bullet.change_y = math.sin(math.radians(player_info.weapon_angle)) * dist_to_next_point
        else:
            bullet.change_x = math.cos(math.radians(player_info.face_angle)) * dist_to_next_point
            bullet.change_y = math.sin(math.radians(player_info.face_angle)) * dist_to_next_point
        bullet.set_position(player_info.x_loc + (cf * bullet.change_x), player_info.y_loc + (cf * bullet.center_y))
        bullet_list.append(bullet)

        if player_info.id == 1:
            player1.bullet_change_x = bullet.change_x
            player1.bullet_change_y = bullet.change_y
        if player_info.id == 2:
            player2.bullet_change_x = bullet.change_x
            player2.bullet_change_y = bullet.change_y

    for bullet in bullet_list:
        bullet.center_x += bullet.change_x
        bullet.center_y += bullet.change_y
        if bullet.collides_with_list(wall_list):
            print("hit map wall")
            bullet.remove_from_sprite_lists()
        if bullet.collides_with_list(player_list):
            print("hit someone")
            bullet.remove_from_sprite_lists()
    map_scene.add_sprite_list(name="bullets", sprite_list=bullet_list)


async def communication_with_client(server: GameWindow, event_loop, gamestate, server_address, UDPServerSocket):
    while (True):
        # get key movements from client
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        json_data = json.loads(message)

        player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
        player_move.keys = json_data

        process_player_shooting(gamestate, client_address, player_move)
        process_player_movement(player_move, client_address, gamestate)
        check_for_collision(gamestate, client_address)

        # send client playerstate positions
        response = gamestate.to_json()
        UDPServerSocket.sendto(str.encode(response), client_address)

        global game_count
        game_count += 1
        if game_count % 1000 == 0:
            # print(gameInfo)
            # print(gameState)
            try:
                print(bullet_list[len(bullet_list) - 1].center_x, bullet_list[len(bullet_list) - 1].center_y)
                print(bullet_list[len(bullet_list) - 1].change_x, bullet_list[len(bullet_list) - 1].change_y)
                print(len(bullet_list), game_count)
            except:
                print("no bullets")


def main():
    server_address = find_ip_address()
    print(f"Server address is {server_address} on port {SERVER_PORT}")
    gameInfo = PlayerState.GameInformation(level_switch=False, level_num=1, player1_lives=5, player1_score=0,
                                           player2_lives=5, player2_score=0)
    gameState = PlayerState.GameState(all_players, gameInfo)

    # create a socket and bind it to the address and port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((server_address, SERVER_PORT))

    addresses = []

    # sort who is who for players
    while len(all_players) != 1:
        data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
        message = data_packet[0]  # data stored here within tuple
        client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]

        if not client_address[0] in all_players and len(all_players) < 2:
            if len(all_players) < 1:
                print(f"player 1: {client_address[0]} added")
                player1_state: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=1, x_loc=80, y_loc=80, face_angle=90, weapon_angle=0, shooting=False, weapon_shooting=False,
                    last_update=datetime.datetime.now(), bullet_delay=datetime.datetime.now(), num_bullets=3
                )
                player1.set_position(player1_state.x_loc, player1_state.y_loc)
                all_players[client_address[0]] = player1_state
                addresses.append(client_address)
            elif len(all_players) == 1:
                print(f"player 2: {client_address[0]} added")
                player2_state: PlayerState.PlayerState = PlayerState.PlayerState(
                    id=2, x_loc=Client2.SCREEN_WIDTH - 64, y_loc=Client2.SCREEN_HEIGHT - 64, face_angle=270,
                    weapon_angle=0, shooting=False, weapon_shooting=False, last_update=datetime.datetime.now(),
                    bullet_delay=datetime.datetime.now(), num_bullets=3
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
    print("all players connected")

    # send list of IP addresses to client
    message = json.dumps(addresses)
    UDPServerSocket.sendto(str.encode(message), addresses[0])
    # UDPServerSocket.sendto(str.encode(message), addresses[1])
    print("addresses sent to client")

    window = GameWindow(player1, player2)
    server_thread = threading.Thread(target=setup_server_connection,
                                     args=(window, gameState, server_address, UDPServerSocket),
                                     daemon=True)
    server_thread.start()
    arcade.run()

    # while (True):
    #     # get key movements from client
    #     data_packet = UDPServerSocket.recvfrom(1024)  # sets the packet size, next lines won't run until this receives
    #     message = data_packet[0]  # data stored here within tuple
    #     client_address = data_packet[1]  # client IP addr is stored here, nothing beyond [1]
    #
    #     json_data = json.loads(message)
    #
    #     player_move: PlayerState.PlayerMovement = PlayerState.PlayerMovement()
    #     player_move.keys = json_data
    #
    #     process_player_shooting(gameState, client_address, player_move)
    #     process_player_movement(player_move, client_address, gameState)
    #     check_for_collision(gameState, client_address)
    #
    #     # send client playerstate positions
    #     response = gameState.to_json()
    #     UDPServerSocket.sendto(str.encode(response), client_address)
    #
    #     global game_count
    #     game_count += 1
    #     if game_count % 1000 == 0:
    #         # print(gameInfo)
    #         # print(gameState)
    #         try:
    #             print(bullet_list[len(bullet_list)-1].center_x, bullet_list[len(bullet_list)-1].center_y)
    #             print(bullet_list[len(bullet_list)-1].change_x, bullet_list[len(bullet_list)-1].change_y)
    #             print(len(bullet_list), game_count)
    #         except:
    #             print("no bullets")

    # get game information from client (next level and level number)
    # game_info_data = UDPServerSocket.recvfrom(1024)
    # game_info_string = game_info_data[0]    # type bytes
    # game_data = json.loads(game_info_string)    # type list
    # print(game_info_string, type(game_info_string))
    # if get_game_info(game_info_string.decode())[0] == "false":
    #     gameInfo.level_switch = False
    # elif get_game_info(game_info_string.decode())[0] == "true":
    #     gameInfo.level_num += 1
    #     gameInfo.level_switch = False
    #     if gameInfo.level_num == 4:
    #         gameInfo.level_num = 1
    #     update_game_state(gameState.game_state, gameState)


if __name__ == '__main__':
    main()
