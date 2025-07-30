"""
This script uses the Arcade library to detect and display keyboard key presses.

To run this script:
1. Make sure you have Python installed.
2. Install the Arcade library by running this command in your terminal:
   pip install arcade
3. Run this script from your terminal:
   python your_script_name.py
"""
import arcade
import inspect

# --- Screen Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Key Identifier"
LINE_HEIGHT = 30
FONT_SIZE = 20

class KeyIdentifier(arcade.Window):
    """
    Main application window.
    This class inherits from arcade.Window and handles drawing and key presses.
    """

    def __init__(self):
        # --- Initialize the Window ---
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # --- Member Variables ---
        self.key_name = "No key pressed yet"
        self.key_code = ""
        self.modifiers_text = ""

        # --- Create a reverse lookup dictionary for key constants ---
        # This allows us to get the string name (e.g., "ENTER") from the
        # integer code (e.g., 65293).
        self.key_map = {}
        # The inspect.getmembers function gets all members of the arcade.key module.
        for member_name, member_value in inspect.getmembers(arcade.key):
            # We only want the key constants, which are uppercase integers.
            if member_name.isupper() and isinstance(member_value, int):
                self.key_map[member_value] = member_name

    def on_draw(self):
        """
        This method is called whenever the screen needs to be redrawn.
        """
        # This command has to happen before we start drawing
        self.clear()

        # --- Draw the information text on the screen ---
        start_y = self.height - (FONT_SIZE + LINE_HEIGHT)

        # Instructions
        arcade.draw_text(
            "Press any key to see its identifier.",
            self.width / 2,
            start_y,
            arcade.color.WHITE,
            font_size=FONT_SIZE,
            anchor_x="center"
        )
        start_y -= LINE_HEIGHT * 2

        # Display Key Name
        arcade.draw_text(
            f"Key Name: {self.key_name}",
            self.width / 2,
            start_y,
            arcade.color.CYAN,
            font_size=FONT_SIZE,
            anchor_x="center"
        )
        start_y -= LINE_HEIGHT

        # Display Key Code (Integer)
        arcade.draw_text(
            f"Key Code: {self.key_code}",
            self.width / 2,
            start_y,
            arcade.color.LIGHT_YELLOW,
            font_size=FONT_SIZE,
            anchor_x="center"
        )
        start_y -= LINE_HEIGHT

        # Display Modifiers
        arcade.draw_text(
            f"Modifiers: {self.modifiers_text}",
            self.width / 2,
            start_y,
            arcade.color.PASTEL_ORANGE,
            font_size=FONT_SIZE,
            anchor_x="center"
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        This method is called whenever a key is pressed.
        
        :param key: The integer code of the key that was pressed.
        :param modifiers: A bitwise combination of any modifiers held down (SHIFT, CTRL, ALT).
        """
        # --- Update the text variables with the new key information ---

        # Look up the key name in our map. Default to "UNKNOWN" if not found.
        self.key_name = self.key_map.get(key, "UNKNOWN")
        
        # Store the integer code as a string
        self.key_code = str(key)

        # --- Check which modifiers are active ---
        mod_list = []
        if modifiers & arcade.key.MOD_SHIFT:
            mod_list.append("Shift")
        if modifiers & arcade.key.MOD_CTRL:
            mod_list.append("Ctrl")
        if modifiers & arcade.key.MOD_ALT:
            mod_list.append("Alt")
        
        if mod_list:
            self.modifiers_text = " + ".join(mod_list)
        else:
            self.modifiers_text = "None"
            
        print(f"Key pressed: arcade.key.{self.key_name} ({self.key_code}), Modifiers: {self.modifiers_text}")


def main():
    """ Main function """
    window = KeyIdentifier()
    arcade.run()


if __name__ == "__main__":
    main()
