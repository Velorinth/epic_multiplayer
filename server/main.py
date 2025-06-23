from connection.main import TCPServer
from loader.content import loader

if __name__ == "__main__":
    loader()
    server = TCPServer()
    server.start() 