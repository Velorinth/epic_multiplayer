import arcade

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 3  # pixels per second
        self.velocity_x = 0
        self.velocity_y = 0
        self.keys = {
            'W': False,
            'A': False,
            'S': False,
            'D': False
        }
        
    def on_key_press(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == arcade.key.W:
            self.keys['W'] = True
        if symbol == arcade.key.A:
            self.keys['A'] = True
        if symbol == arcade.key.S:
            self.keys['S'] = True
        if symbol == arcade.key.D:
            self.keys['D'] = True
            
    def on_key_release(self, symbol, modifiers):
        """Handle key release events"""
        if symbol == arcade.key.W:
            self.keys['W'] = False
        if symbol == arcade.key.A:
            self.keys['A'] = False
        if symbol == arcade.key.S:
            self.keys['S'] = False
        if symbol == arcade.key.D:
            self.keys['D'] = False
            
    def update(self, dt):
        """Update player position"""
        # Reset velocity
        self.velocity_x = 0
        self.velocity_y = 0

        # Calculate velocity based on keys
        if self.keys['W']:
            self.velocity_y += self.speed
        if self.keys['S']:
            self.velocity_y -= self.speed
        if self.keys['A']:
            self.velocity_x -= self.speed
        if self.keys['D']:
            self.velocity_x += self.speed
            
        # Apply velocity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_x = 0
        self.velocity_y = 0

    def get_position(self):
        return self.x, self.y