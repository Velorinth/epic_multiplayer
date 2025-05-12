class Camera:
    def __init__(self, x=0, y=0, zoom=1.0):
        self.x = x
        self.y = y
        self.zoom = zoom
    def set_position(self, x, y):
        self.x = x
        self.y = y
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    def get_position(self):
        return self.x, self.y