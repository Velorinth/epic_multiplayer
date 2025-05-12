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
        print(f"Key pressed: {symbol}")
        if symbol == arcade.key.W:
            self.keys['W'] = True
        if symbol == arcade.key.A:
            self.keys['A'] = True
        if symbol == arcade.key.S:
            self.keys['S'] = True
        if symbol == arcade.key.D:
            self.keys['D'] = True
        print(f"Current keys: {self.keys}")
            
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
        print(f"Current keys: {self.keys}")
            
    def update(self, dt):
        """Update player position"""
        # Reset velocity to small values when no keys are pressed
        if not any(self.keys.values()):
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            # Calculate velocity based on keys
            if self.keys['W'] and self.velocity_y < self.speed:
                self.velocity_y += self.speed * dt
            if self.keys['S'] and self.velocity_y > -self.speed:
                self.velocity_y -= self.speed * dt
            if self.keys['A'] and self.velocity_x > -self.speed:
                self.velocity_x -= self.speed * dt
            if self.keys['D'] and self.velocity_x < self.speed:
                self.velocity_x += self.speed * dt

            # Clamp velocity to max speed
            self.velocity_x = max(-self.speed, min(self.velocity_x, self.speed))
            self.velocity_y = max(-self.speed, min(self.velocity_y, self.speed))

            # Handle diagonal movement - reduce speed when moving diagonally
            if abs(self.velocity_x) > 0 and abs(self.velocity_y) > 0:
                self.velocity_x *= 0.707  # ~1/sqrt(2)
                self.velocity_y *= 0.707

        # Apply velocity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def get_position(self):
        return self.x, self.y