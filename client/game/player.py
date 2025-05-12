import pyglet

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 300  # pixels per second
        self.keys = {
            'W': False,
            'A': False,
            'S': False,
            'D': False
        }
        
    def on_key_press(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == pyglet.window.key.W:
            self.keys['W'] = True
        elif symbol == pyglet.window.key.A:
            self.keys['A'] = True
        elif symbol == pyglet.window.key.S:
            self.keys['S'] = True
        elif symbol == pyglet.window.key.D:
            self.keys['D'] = True
            
    def on_key_release(self, symbol, modifiers):
        """Handle key release events"""
        if symbol == pyglet.window.key.W:
            self.keys['W'] = False
        elif symbol == pyglet.window.key.A:
            self.keys['A'] = False
        elif symbol == pyglet.window.key.S:
            self.keys['S'] = False
        elif symbol == pyglet.window.key.D:
            self.keys['D'] = False
            
    def update(self, dt):
        """Update player position"""
        dx = 0
        dy = 0
        
        if self.keys['W']:
            dy += self.speed * dt
        if self.keys['S']:
            dy -= self.speed * dt
        if self.keys['A']:
            dx -= self.speed * dt
        if self.keys['D']:
            dx += self.speed * dt
            
        self.x += dx
        self.y += dy
    def get_position(self):
        return self.x, self.y