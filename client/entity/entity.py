from networking.main import tile_map,entities
from loader.content import get_object_properties as get_content

class Entity:
    def __init__(self,id, x=0, y=0, rot=0, proto=""):
        self.id = id
        self.x = x
        self.y = y
        self.rot = rot
        self.proto = proto
        self.params = get_content(self.proto)
        self.dx = 0
        self.dy = 0
        self.dr = 0
        self.sprite = None
        self.draw = True
        self.inventory_id = None
        self.should_update = True

    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def update(self):
        if self.should_update:
            self.x += self.dx  
            self.y += self.dy
            self.rot += self.dr

    def to_dict(self):
        """
        Converts the entity's state to a dictionary for serialization.
        Note: We don't serialize the 'sprite' or 'params' as they can be
        re-created on the receiving end from the 'proto'.
        """
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "rot": self.rot,
            "proto": self.proto,
            "dx": self.dx,
            "dy": self.dy,
            "dr": self.dr,
            "draw": self.draw,
            "inventory_id": self.inventory_id,
            "should_update": self.should_update,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Entity instance from a dictionary."""
        # The __init__ method will handle loading the correct params from the proto
        entity = cls(id=data.get('id'), x=data.get('x'), y=data.get('y'), rot=data.get('rot'), proto=data.get('proto'))
        # Update the remaining properties from the dictionary
        entity.dx = data.get('dx', 0)
        entity.dy = data.get('dy', 0)
        entity.dr = data.get('dr', 0)
        entity.draw = data.get('draw', True)
        entity.inventory_id = data.get('inventory_id')
        entity.should_update = data.get('should_update', True)
        return entity

def get_tile_map():
    return tile_map 

def get_entities():
    return entities 

def update_entities():
    for entity in entities.values():
        entity.update()