from networking.registration.logic import register_subtype,register_packet
from networking.main import tile_map, entities
from entity.entity import Entity 
from typing import Dict, Any

@register_subtype('response', 'entities')
def handle_response_entities(data: Dict[str, Any]):
    """Handles receiving the list of entities from the server."""
    print(f"Received entities: {data}")
    #entities.clear()
    entity_data = data.get('data', {}).get('data', {})
    if entity_data:
        entities.clear()
        for entity_id, entity_info in entity_data.items():
            entity = Entity.from_dict(entity_info)
            entities[int(entity_id)] = entity
    print(f"Updated entities: {entities}")



@register_subtype('response', 'map')
def handle_response_map(data: Dict[str, Any]):
    """Handles receiving the map data from the server."""
    print(f"Received map: {data}")
    tile_map.clear()
    tile_map.update(data.get('data', {}).get('data', {}))

@register_subtype('response', 'join')
def handle_response_join(data: Dict[str, Any]):
    """recv fuking join data"""
    pass
