import arcade

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 30000  # pixels per second
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
        # Handle movement keys if not handled by inventory
        print(f"Key pressed: {symbol}")
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
        print(f"Key released: {symbol}")
        if symbol == arcade.key.W:
            self.keys['W'] = False
        if symbol == arcade.key.A:
            self.keys['A'] = False
        if symbol == arcade.key.S:
            self.keys['S'] = False
        if symbol == arcade.key.D:
            self.keys['D'] = False

    def key_movement(self, dt):
        """Handle key press events"""
        vx = 0
        vy = 0
        
        if not any(self.keys.values()):
            #print(f"No keys pressed: {self.keys},vel {vx},{vy},pos {self.x},{self.y}")
            vx = 0
            vy = 0
            return
        else:
            if self.keys['W']:
                vy += self.speed * dt
            if self.keys['A']:
                vx -= self.speed * dt
            if self.keys['S']:
                vy -= self.speed * dt
            if self.keys['D']:
                vx += self.speed * dt

        #print(f"vel {vx},{vy},pos {self.x},{self.y}")
        self.x += vx * dt
        self.y += vy * dt

        vx = 0
        vy = 0

    def get_position(self):
        return self.x, self.y