from networking.registration.logic import register_packet, register_subtype
from networking.main import yml_content, entities
from typing import Dict, Tuple, Any, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from networking.main import TCPServer

@register_packet('join')
def handle_join(server: 'TCPServer', addr: Tuple[str, int], data: Dict[str, Any]):
    """Handles a client joining the server."""
    print(f"Client joined: {addr}, sending map and entities.")
    #data['data']['type']
    server.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'entities', 'data': entities}}))
    server.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'map', 'data': yml_content['map']}}))

@register_subtype('update', 'player')
def handle_update_player(server: 'TCPServer', addr: Tuple[str, int], data: Dict[str, Any]):
    """Handles player movement updates from the client."""
    # Player movement is received, but no action is taken on the server side yet.
    # In the future, you might update the player's state and broadcast it.
    pass

@register_subtype('get', 'entities')
def handle_get_entities(server: 'TCPServer', addr: Tuple[str, int], data: Dict[str, Any]):
    """Handles requests for entity data from the client."""
    server.send_to_client(addr, json.dumps({'type': 'response', 'data': {'type': 'entities', 'data': entities}}))