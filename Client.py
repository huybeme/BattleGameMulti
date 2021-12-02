import game
import threading
import asyncio
import socket
import json
import PlayerState


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

def setup_client_connection():
    client_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(client_event_loop)
    client_event_loop.create_task(communication_with_server(client_event_loop))
    client_event_loop.run_forever()

async def communication_with_server(event_loop):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        message = input("type something: ")
        UDPClientSocket.sendto(str.encode(message), ("10.0.0.246", 25001))
        data_packet = UDPClientSocket.recvfrom(1024)
        data = data_packet[0]   # get the encoded string



def main():
    client_address = find_ip_address()
    server_address = input("enter the IP address to the server:\n")
    setup_client_connection()
    client_thread = threading.Thread(target=setup_client_connection, daemon=True)
    client_thread.start()


if __name__ == '__main__':
    main()
