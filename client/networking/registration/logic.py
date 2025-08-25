from typing import Callable, Dict, Any

packet_handlers: Dict[str, Callable] = {}
packet_sub_handlers: Dict[str, Dict[str, Callable]] = {}
entities = {}
tile_map = {}

def register_packet(packet_type: str):
    """A decorator to register a function as a handler for a specific packet type."""
    def decorator(func: Callable):
        packet_handlers[packet_type] = func
        print(f"Registered client handler for packet type '{packet_type}'")
        return func
    return decorator

def register_subtype(packet_type: str, sub_type: str):
    """A decorator to register a function as a handler for a specific packet type and subtype."""
    def decorator(func: Callable):
        if packet_type not in packet_sub_handlers:
            packet_sub_handlers[packet_type] = {}
        packet_sub_handlers[packet_type][sub_type] = func
        print(f"Registered client sub-handler for packet type '{packet_type}' with subtype '{sub_type}'")
        return func
    return decorator

def packet_handler(packet_data: Dict[str, Any]):
    """
    Looks up and executes the appropriate handler for a given packet.
    It prioritizes subtype handlers over general type handlers.
    """
    packet_type = packet_data.get('type')
    if not packet_type:
        print(f"Received packet with no type: {packet_data}")
        return

    handler = None
    handler_id = f"type '{packet_type}'"
    sub_type = None

    sub_type_data = packet_data.get('data', {})
    if isinstance(sub_type_data, dict):
        sub_type = sub_type_data.get('type')
        if sub_type:
            handler = packet_sub_handlers.get(packet_type, {}).get(sub_type)
            if handler:
                handler_id = f"type '{packet_type}' with subtype '{sub_type}'"

    if not handler:
        handler = packet_handlers.get(packet_type)

    if handler:
        try:
            handler(packet_data)
        except Exception as e:
            print(f"Error handling packet {handler_id}: {e}")
    else:
        if sub_type:
            handler_id = f"type '{packet_type}' with subtype '{sub_type}'"
        print(f"No client handler registered for packet {handler_id}")

