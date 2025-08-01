import arcade
import arcade.gui
import io
import contextlib
import traceback

from networking.main import entities
from loader.content import get_objects_by_property
from game.player import Player
from game.inventory import Inventory

# We are keeping this custom widget from the previous attempt.
# Its job is to reliably intercept the Enter key and prevent the default buggy behavior.
class CustomUIInputText(arcade.gui.UIInputText):
    def __init__(self, console_instance, **kwargs):
        super().__init__(**kwargs)
        self.console = console_instance

class DebugConsole:
    FONT_SIZE = 12
    BG_COLOR = (20, 20, 20, 220)
    
    def __init__(self, player_ref: Player, inventory_ref: Inventory, ui_manager: arcade.gui.UIManager):
        self.player = player_ref
        self.inventory = inventory_ref
        self.ui_manager = ui_manager
        self.is_open = False
        
        self.custom_commands = {}
        command_list = get_objects_by_property("type", "cmd")
        for command_data in command_list:
            command_name = command_data.get('command')
            if command_name:
                self.custom_commands[command_name] = command_data

        # Store v_box as an instance variable so we can access it later if needed.
        self.v_box = arcade.gui.UIBoxLayout(size_hint=(1, 1))
        
        self.history_area = arcade.gui.UITextArea(
            text="", size_hint=(1, 1), text_color=arcade.color.WHITE, font_name="Consolas"
        )
        
        self.input_area = CustomUIInputText(
            console_instance=self,
            text="",
            font_size=12,
            text_color=arcade.color.LIGHT_GRAY,
            size_hint=(1, None),
            height=30
        )
        
        # Correct Layout: Add history first so it's on top, then the input area at the bottom.
        self.v_box.add(self.history_area)
        self.v_box.add(self.input_area)

        # Store the main container so we can trigger its render.
        self.container = arcade.gui.UIAnchorLayout(
            children=[self.v_box],
            anchor_x="left", anchor_y="bottom",
            size_hint=(1, 0.5)
        )

    def toggle(self):
        """Shows or hides the console."""
        self.is_open = not self.is_open
        if self.is_open:
            self.ui_manager.add(self.container)
        else:
            self.ui_manager.remove(self.container)

    def on_key_press(self, symbol):
        if symbol == arcade.key.GRAVE:
            self.toggle()
        if self.is_open:
            if symbol == arcade.key.ENTER or symbol == arcade.key.NUM_ENTER:
                self.execute_command()
                return True  # Consume the event
    def draw(self, width, height):
        """Draws the console's background manually."""
        if self.is_open:
            arcade.draw_lrbt_rectangle_filled(0, width, 0, height / 2, self.BG_COLOR)

    def write_line(self, text, color=arcade.color.YELLOW):
        lines = self.history_area.text.split('\n')
        if len(lines) > 200:
            self.history_area.text = '\n'.join(lines[-100:])
        self.history_area.text += f"{text}\n"

    def execute_command(self):
        """Executes the command and forces the UI to redraw."""
        command_text = self.input_area.text.strip()
        print(command_text)
        self.write_line(f"> {command_text}", arcade.color.WHITE)
        self.input_area.text = ""
        self.container.trigger_full_render()

        # Execute the actual command logic after handling the UI updates.
        parts = command_text.split()
        command_name = parts[0]
        if command_name in self.custom_commands:
            self.execute_custom_command(command_name, parts[1:])
        else:
            self.execute_python_command(command_text)
            
    def execute_custom_command(self, name, args):
        command_info = self.custom_commands.get(name)
        self.write_line(f"Executed custom command: '{name}' with args: {args}")
        self.write_line(f"Description: {command_info.get('description', 'N/A')}")
        
    def execute_python_command(self, command):
        console_globals = {
        "arcade": arcade,
        "entities": entities,
        "player": self.player,
        "inventory": self.inventory
        }
        output_buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(output_buffer):
                exec(command, console_globals)
            output = output_buffer.getvalue().strip()
            if output: self.write_line(output, arcade.color.YELLOW)
        except Exception:
            self.write_line(traceback.format_exc().strip(), arcade.color.RED_ORANGE)