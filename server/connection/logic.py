import json

def packet_handler(message: str):
    data = json.loads(message)
    if data['type'] == 'update':
        if data['data']['type'] == 'player':
            print(f"Player moved to ({data['data']['data']['x']}, {data['data']['data']['y']})")
    elif data['type'] == 'get':
        if data['data']['type'] == 'entities':
            pass