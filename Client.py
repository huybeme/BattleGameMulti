import game
import arcade
import threading
import asyncio
import socket
import json
import PlayerState

CLIENT_ADDR = None
SERVER_ADDR = None
SERVER_PORT = None

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

def setup_client_connection(client: game.TiledWindow):
    client_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(client_event_loop)
    client_event_loop.create_task(communication_with_server(client, client_event_loop))
    client_event_loop.run_forever()

async def communication_with_server(client: game.TiledWindow, event_loop):  # client pulls from TiledWindow class
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        keystate = json.dumps(client.actions.keys)
        UDPClientSocket.sendto(str.encode(keystate), (client.server_address, int(client.server_port)))
        data_packet = UDPClientSocket.recvfrom(1024)
        data = data_packet[0]   # get the encoded string
        decoded_data: PlayerState.GameState = PlayerState.GameState.from_json(data)
        player_dict = decoded_data.player_states
        player_info: PlayerState.PlayerState = player_dict[client.ip_addr]

        # game.TiledWindow.player_1.center_y = player_info.y_loc
        # game.TiledWindow.player_1.center_x = player_info.x_loc



def main():

    SERVER_ADDR = "10.0.0.241"
    SERVER_PORT = "25001"

    CLIENT_ADDR = find_ip_address()
    # SERVER_ADDR = input("enter the IP address to the game server:\n")     # uncomment before submission
    # SERVER_PORT = input("enter the port to the game server:\n")

    window = game.TiledWindow(CLIENT_ADDR, SERVER_ADDR, SERVER_PORT)

    client_thread = threading.Thread(target=setup_client_connection, args=(window,), daemon=True)
    client_thread.start()
    arcade.run()


if __name__ == '__main__':
    main()
