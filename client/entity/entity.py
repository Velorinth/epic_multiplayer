from networking.main import tile_map,entities
from loader.content import get_object_properties as get_content

class Entity:
    def __init__(self,id, x=0, y=0, rot=0, params=None, proto=""):
        self.id = id
        self.x = x
        self.y = y
        self.rot = rot
        self.proto = proto
        self.params = params if params is not None else get_content(self.proto)
        self.dx = 0
        self.dy = 0
        self.dr = 0

        print(self.id)
        print(self.params)

    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def update(self):
        self.x += self.dx   
        self.y += self.dy
        self.rot += self.dr
        print()

def get_tile_map():
    return tile_map 

def get_entities():
    return entities