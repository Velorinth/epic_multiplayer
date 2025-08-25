import socket
import threading
import json
import time
from types import SimpleNamespace
from networking.registration.logic import packet_handler, tile_map,entities
from networking.registration.entity import handle_response_entities, handle_response_map, handle_response_join
isConnectedToServer = True

def receive_messages(sock):
    global isConnectedToServer
    isConnectedToServer = True
    buffer = b''
    while isConnectedToServer:
        try:
            data = sock.recv(65536)
            if not data:
                print("Disconnected from server")
                isConnectedToServer = False
                break
            buffer += data
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                if line:
                    try:
                        message = json.loads(line.decode())
                        # Use the new packet handler to process the message
                        packet_handler(message)
                    except json.JSONDecodeError:
                        print(f"Received invalid JSON: {line.decode(errors='ignore')}")

        except (ConnectionError, ConnectionResetError):
            print("Connection lost")
            isConnectedToServer = False
            break

def get_tile_map():
    return tile_map

def get_entities():
    return entities

def send_messages(socket: socket.socket,player):
    s = socket
    message = {
        "type": "update",
        "data": {
            "type": "player",
            "data": {
                "x": player.x,
                "y": player.y
            }
        }
    }
    s.sendall((json.dumps(message) + '\n').encode())  # Convert entire message to JSON once
def start_client(player, auth, host='127.0.0.1', port=5555):
    global isConnectedToServer
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            isConnectedToServer = True

            # Start receiving messages in a separate thread
            recv_thread = threading.Thread(target=receive_messages, args=(s,), daemon=True)
            recv_thread.start()

            # The player object is a class instance, which is not JSON serializable by default.
            # We should convert it to a dictionary of primitive types (like numbers and strings).
            player_data = {
                "x": player.x,
                "y": player.y
            }

            message = {
                "type": "join",
                "data": {
                    "67": 51,
                    "auth": {
                        "id": auth['id'],
                        "name": auth['name'],
                        "password": auth['password']
                    }
                }
            }
            s.sendall((json.dumps(message) + '\n').encode())  # Convert entire message to JSON once
            # Send messages from user input
            while isConnectedToServer:
                send_messages(s,player)
                # Add a delay to prevent 100% CPU usage and network flooding
                time.sleep(1/30) # Send updates at ~30Hz

        except ConnectionRefusedError:
            print(f"Could not connect to {host}:{port}")
            isConnectedToServer = False

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            isConnectedToServer = False

        except Exception as e:
            print(f"Error: {e}")
            isConnectedToServer = False


if __name__ == '__main__':
    # Create mock objects for testing
    mock_player = SimpleNamespace(x=5, y=10)
    from networking.auth import auth
    

    print("Starting client in test mode...")
    start_client(mock_player, auth=auth)