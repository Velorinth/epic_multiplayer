import socket
import threading
from typing import Dict, Tuple
from connection.logic import packet_handler
from update.data import entities
from loader.content import get_object_properties as get_content, yml_content
import json

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.clients: Dict[Tuple[str, int], socket.socket] = {}  # (ip, port) -> socket
        self.lock = threading.Lock()  # For thread-safe client dictionary access
        self.running = False

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int]):
        print(f"Client connected: {addr}")
        with self.lock:
            self.clients[addr] = conn

        buffer = b''
        try:
            while self.running:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data
                
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line:
                        message = line.decode()
                        data = json.loads(message)
                        if data['type'] == 'join':
                            print(f"Client joined: {addr}, sending map ")
                            self.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'entities', 'data': entities}}))
                            self.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'map', 'data':yml_content['map']}}))
                        if data['type'] == 'update':
                            if data['data']['type'] == 'player':
                                pass
                                #print(f"Player moved to ({data['data']['data']['x']}, {data['data']['data']['y']})")
                        elif data['type'] == 'get':
                            if data['data']['type'] == 'entities':
                                self.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'entities', 'data': entities}}))
        except (ConnectionResetError, ConnectionAbortedError):
            print(f"Client disconnected: {addr}")
        finally:
            with self.lock:
                self.clients.pop(addr, None)
            conn.close()
            print(f"Connection closed: {addr}")

    def send_to_client(self, client_addr: Tuple[str, int], message: str) -> bool:
        """Send a message to a specific client"""
        with self.lock:
            client_socket = self.clients.get(client_addr)
        
        if client_socket:
            try:
                if not message.endswith('\n'):
                    message += '\n'
                client_socket.sendall(message.encode())
                return True
            except (ConnectionResetError, BrokenPipeError):
                print(f"Failed to send to {client_addr}: Client disconnected")
                with self.lock:
                    self.clients.pop(client_addr, None)
        return False

    def broadcast(self, message: str, exclude_addr: Tuple[str, int] = None) -> None:
        """Send a message to all connected clients except the excluded one"""
        if not message.endswith('\n'):
            message += '\n'
            
        with self.lock:
            clients = list(self.clients.items())
            
        for addr, sock in clients:
            if exclude_addr and addr == exclude_addr:
                continue
            try:
                sock.sendall(message.encode())
            except (ConnectionResetError, BrokenPipeError):
                print(f"Failed to broadcast to {addr}")
                with self.lock:
                    self.clients.pop(addr, None)

    def start(self):
        self.running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server started on {self.host}:{self.port}")

            try:
                while self.running:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                    thread.start()
            except KeyboardInterrupt:
                print("\nShutting down server...")
            finally:
                self.running = False
                with self.lock:
                    for client in self.clients.values():
                        try:
                            client.close()
                        except:
                            pass
                    self.clients.clear()

if __name__ == "__main__":
    server = TCPServer()
    server.start()