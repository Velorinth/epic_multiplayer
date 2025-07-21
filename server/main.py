from connection.main import TCPServer
from loader.content import load_content

if __name__ == "__main__":
    load_content()
    server = TCPServer()
    server.start() 