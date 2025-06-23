import socket
import threading
import json
from loader.content import yml_content
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server")
                break
            #print(f"Received: {data.decode()}")
            message = json.loads(data.decode())
            if message['type'] == 'response':
                if message['data']['type'] == 'entities':
                    pass
                elif message['data']['type'] == 'map':
                    yml_content['map'] = message['data']['data']
                    pass
            
        except ConnectionError:
            print("Connection lost")
            break

def start_client(player, host='127.0.0.1', port=5555):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            # Start receiving messages in a separate thread
            recv_thread = threading.Thread(target=receive_messages, args=(s,), daemon=True)
            recv_thread.start()
            
            # Send messages from user input
            while True:
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
                
        except ConnectionRefusedError:
            print(f"Could not connect to {host}:{port}")
        except KeyboardInterrupt:
            print("\nDisconnecting...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    start_client()