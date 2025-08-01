import arcade
import collections
import math
from typing import Optional, List, Dict, Any
from entity.entity import Entity

from render.renderer import loaded_textures
from networking.main import entities

class Inventory:
    # --- UI Constants ---
    SLOT_SIZE = 52
    SLOT_MARGIN = 8
    SPRITE_SCALE_FACTOR = 0.6
    HOTBAR_SLOT_COUNT = 5
    SLOT_BG_COLOR = (50, 50, 50, 180)
    SLOT_HIGHLIGHT_COLOR = arcade.color.WHITE
    
    INV_WINDOW_COLOR = (30, 30, 30, 220)
    INV_WINDOW_PADDING = 15
    INV_COLS = 5
    INV_MIN_ROWS = 3
    
    TEXT_COLOR = arcade.color.WHITE
    FONT_SIZE = 12
    
    TOOLTIP_COLOR = (0, 0, 0, 230)
    TOOLTIP_WIDTH = 200

    def __init__(self):
        # The inventory's own master list of entity objects it contains.
        self._master_item_list: list[Entity] = []

        self.cursor_stack: list[Entity] = []
        self.hotbar_slots: list[list[Entity]] = [[] for _ in range(self.HOTBAR_SLOT_COUNT)]
        
        self.selected_hotbar_slot = 0
        self.is_open = False

        self.cursor_sprite = arcade.Sprite()
        self.cursor_sprite_list = arcade.SpriteList()
        self.cursor_sprite_list.append(self.cursor_sprite)

        self.hovered_item_stack: Optional[list[Entity]] = None
        self.mouse_x, self.mouse_y = 0, 0
        self._shape_list = arcade.shape_list.ShapeElementList()
        self._sprite_list = arcade.SpriteList()
        self._text_list = []
        self._clickable_areas = {}
        self._needs_rebuild = True
        
    def _get_entity_hash(self, entity: Entity) -> str:
        param_string = str(sorted(entity.params.items()))
        return f"{entity.proto}:{param_string}"

    def _update_cursor_sprite(self):
        texture_to_use = loaded_textures.get("ui/trans1.png")
        if self.cursor_stack:
            texture_name = self.cursor_stack[0].params.get("texture")
            if texture_name and texture_name in loaded_textures:
                texture_to_use = loaded_textures[texture_name]
        
        if texture_to_use:
            self.cursor_sprite.texture = texture_to_use
            self.cursor_sprite.width = self.SLOT_SIZE * self.SPRITE_SCALE_FACTOR * 1.5
            self.cursor_sprite.height = self.SLOT_SIZE * self.SPRITE_SCALE_FACTOR * 1.5
        else:
            self.cursor_sprite.texture = None

    def add_item(self, entity: Entity):
        """Claims an entity by flagging it and adding it to the internal list."""
        if not entity: return
        entity.inventory_id = 1
        entity.draw = False
        self._master_item_list.append(entity)
        self._needs_rebuild = True

    def drop_stack(self, stack: list, player_entity: Entity):
        """Drops a stack of items, removing them from inventory control."""
        if not stack: return
        
        stack_ids = {id(item) for item in stack}
        self._master_item_list = [item for item in self._master_item_list if id(item) not in stack_ids]

        for item in stack:
            item.inventory_id = None
            item.draw = True
            item.x = player_entity.x
            item.y = player_entity.y
        
        stack.clear()
        self._needs_rebuild = True

    def on_key_press_inventory(self, symbol, modifiers):
        if symbol == arcade.key.TAB:
            self.is_open = not self.is_open
            self._needs_rebuild = True
        if arcade.key.KEY_1 <= symbol <= arcade.key.KEY_5:
            self.selected_hotbar_slot = symbol - arcade.key.KEY_1
            self._needs_rebuild = True

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_x, self.mouse_y = x, y
        self.hovered_item_stack = None
        
        current_areas = self._clickable_areas if self.is_open else {k: v for k, v in self._clickable_areas.items() if k[0] == 'hotbar'}
        for area_id, area_rect in current_areas.items():
            left, bottom, width, height = area_rect
            if left < x < left + width and bottom < y < bottom + height:
                area_type, data = area_id
                if area_type == "hotbar" and self.hotbar_slots[data]:
                    self.hovered_item_stack = self.hotbar_slots[data]
                elif area_type == "inventory":
                    grouped_items = self._get_grouped_items()
                    if data < len(grouped_items):
                        self.hovered_item_stack = grouped_items[list(grouped_items.keys())[data]]
                break

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        clicked_area = None
        for area_id, area_rect in self._clickable_areas.items():
            left, bottom, width, height = area_rect
            if left < x < left + width and bottom < y < bottom + height:
                clicked_area = area_id; break
        if not clicked_area: return

        area_type, data = clicked_area
        
        if area_type == "hotbar":
            self._handle_hotbar_click(data, button)
        elif area_type == "inventory" and self.is_open:
            self._handle_inventory_click(data, button)

        self._update_cursor_sprite()
        self._needs_rebuild = True
    
    def _handle_hotbar_click(self, slot_index: int, button: int):
        target_stack = self.hotbar_slots[slot_index]
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.cursor_stack and target_stack and self._get_entity_hash(self.cursor_stack[0]) == self._get_entity_hash(target_stack[0]):
                target_stack.extend(self.cursor_stack)
                self.cursor_stack.clear()
            else:
                self.cursor_stack, self.hotbar_slots[slot_index] = target_stack, self.cursor_stack
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.cursor_stack and (not target_stack or self._get_entity_hash(target_stack[0]) == self._get_entity_hash(self.cursor_stack[0])):
                target_stack.append(self.cursor_stack.pop())
            elif not self.cursor_stack and target_stack:
                split_amount = math.ceil(len(target_stack) / 2)
                self.cursor_stack.extend(target_stack[split_amount:])
                del target_stack[split_amount:]

    def _handle_inventory_click(self, slot_index: int, button: int):
        grouped_items = self._get_grouped_items()
        item_stacks = list(grouped_items.values())
        if slot_index < len(item_stacks):
            source_stack = item_stacks[slot_index]
            if button == arcade.MOUSE_BUTTON_LEFT:
                if self.cursor_stack and source_stack and self._get_entity_hash(self.cursor_stack[0]) == self._get_entity_hash(source_stack[0]):
                    self._master_item_list.extend(self.cursor_stack)
                    self.cursor_stack.clear()
                else:
                    source_ids = {id(item) for item in source_stack}
                    self._master_item_list = [item for item in self._master_item_list if id(item) not in source_ids]
                    self._master_item_list.extend(self.cursor_stack)
                    self.cursor_stack = source_stack
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if not self.cursor_stack and source_stack:
                    split_amount = math.ceil(len(source_stack) / 2)
                    items_to_move = source_stack[:split_amount]
                    self.cursor_stack.extend(items_to_move)
                    for item in items_to_move:
                        self._master_item_list.remove(item)
        elif self.cursor_stack:
            if button == arcade.MOUSE_BUTTON_LEFT:
                self._master_item_list.extend(self.cursor_stack)
                self.cursor_stack.clear()
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if self.cursor_stack: self._master_item_list.append(self.cursor_stack.pop())
                
    def _get_grouped_items(self) -> dict:
        grouped = collections.defaultdict(list)
        checked_out_ids = {id(item) for stack in self.hotbar_slots for item in stack}
        if self.cursor_stack:
            checked_out_ids.update(id(item) for item in self.cursor_stack)
        for item in self._master_item_list:
            if id(item) not in checked_out_ids:
                grouped[self._get_entity_hash(item)].append(item)
        return grouped

    def _rebuild_visuals(self, screen_width: int, screen_height: int):
        """
        Clears and rebuilds all visual elements for the inventory and hotbar UI.
        """
        self._shape_list = arcade.shape_list.ShapeElementList()
        self._sprite_list = arcade.SpriteList()
        self._text_list = []
        self._clickable_areas = {}
        
        # --- Rebuild Hotbar ---
        hotbar_width = (self.SLOT_SIZE * self.HOTBAR_SLOT_COUNT) + (self.SLOT_MARGIN * (self.HOTBAR_SLOT_COUNT - 1))
        hotbar_start_x = (screen_width / 2) - (hotbar_width / 2)
        hotbar_center_y = self.SLOT_SIZE / 2 + self.SLOT_MARGIN
        
        for i in range(self.HOTBAR_SLOT_COUNT):
            center_x = hotbar_start_x + (self.SLOT_SIZE / 2) + i * (self.SLOT_SIZE + self.SLOT_MARGIN)
            
            slot_bg = arcade.shape_list.create_rectangle_filled(center_x, hotbar_center_y, self.SLOT_SIZE, self.SLOT_SIZE, self.SLOT_BG_COLOR)
            self._shape_list.append(slot_bg)
            
            if i == self.selected_hotbar_slot:
                highlight_border = arcade.shape_list.create_rectangle_outline(center_x, hotbar_center_y, self.SLOT_SIZE, self.SLOT_SIZE, self.SLOT_HIGHLIGHT_COLOR, 2)
                self._shape_list.append(highlight_border)
                
            left = center_x - self.SLOT_SIZE / 2
            bottom = hotbar_center_y - self.SLOT_SIZE / 2
            self._clickable_areas[("hotbar", i)] = (left, bottom, self.SLOT_SIZE, self.SLOT_SIZE)
            
            stack = self.hotbar_slots[i]
            if stack:
                item, count = stack[0], len(stack)
                texture_name = item.params.get("texture")
                if texture_name and texture_name in loaded_textures:
                    sprite = arcade.Sprite(loaded_textures[texture_name])
                    sprite.scale = (self.SLOT_SIZE * self.SPRITE_SCALE_FACTOR) / sprite.width
                    sprite.position = (center_x, hotbar_center_y)
                    self._sprite_list.append(sprite)
                    
                if count > 1:
                    text_x = center_x + self.SLOT_SIZE / 2 - 8
                    text_y = hotbar_center_y - self.SLOT_SIZE / 2 + 5
                    count_text = arcade.Text(str(count), text_x, text_y, self.TEXT_COLOR, self.FONT_SIZE, anchor_x="center")
                    self._text_list.append(count_text)

        # --- Rebuild Inventory Window (if open) ---
        if self.is_open:
            item_stacks = list(self._get_grouped_items().values())
            
            num_rows = self.INV_MIN_ROWS
            if item_stacks:
                num_rows = max(self.INV_MIN_ROWS, math.ceil(len(item_stacks) / self.INV_COLS))

            window_width = (self.SLOT_SIZE * self.INV_COLS) + (self.SLOT_MARGIN * (self.INV_COLS + 1))
            window_height = (self.SLOT_SIZE * num_rows) + (self.SLOT_MARGIN * (num_rows + 1))
            win_center_x, win_center_y = screen_width / 2, screen_height / 2
            
            panel = arcade.shape_list.create_rectangle_filled(win_center_x, win_center_y, window_width, window_height, self.INV_WINDOW_COLOR)
            self._shape_list.append(panel)
            
            inv_start_x = win_center_x - (window_width / 2) + self.SLOT_MARGIN + (self.SLOT_SIZE / 2)
            inv_start_y = win_center_y + (window_height / 2) - self.SLOT_MARGIN - (self.SLOT_SIZE / 2)
            
            for i in range(num_rows * self.INV_COLS):
                row, col = divmod(i, self.INV_COLS)
                
                center_x = inv_start_x + col * (self.SLOT_SIZE + self.SLOT_MARGIN)
                center_y = inv_start_y - row * (self.SLOT_SIZE + self.SLOT_MARGIN)
                
                slot_bg = arcade.shape_list.create_rectangle_filled(center_x, center_y, self.SLOT_SIZE, self.SLOT_SIZE, self.SLOT_BG_COLOR)
                self._shape_list.append(slot_bg)
                
                left = center_x - self.SLOT_SIZE / 2
                bottom = center_y - self.SLOT_SIZE / 2
                self._clickable_areas[("inventory", i)] = (left, bottom, self.SLOT_SIZE, self.SLOT_SIZE)
                
                if i < len(item_stacks):
                    item, count = item_stacks[i][0], len(item_stacks[i])
                    texture_name = item.params.get("texture")
                    if texture_name and texture_name in loaded_textures:
                        sprite = arcade.Sprite(loaded_textures[texture_name])
                        sprite.scale = (self.SLOT_SIZE * self.SPRITE_SCALE_FACTOR) / sprite.width
                        sprite.position = (center_x, center_y)
                        self._sprite_list.append(sprite)
                        
                    if count > 1:
                        text_x = center_x + self.SLOT_SIZE / 2 - 8
                        text_y = center_y - self.SLOT_SIZE / 2 + 5
                        count_text = arcade.Text(str(count), text_x, text_y, self.TEXT_COLOR, self.FONT_SIZE, anchor_x="center")
                        self._text_list.append(count_text)

        self._needs_rebuild = False
        
    def draw(self, screen_width, screen_height, mouse_x, mouse_y):
        if self._needs_rebuild: self._rebuild_visuals(screen_width, screen_height)
        self._shape_list.draw(); self._sprite_list.draw()
        for text_object in self._text_list: text_object.draw()
        
        if self.cursor_stack and self.cursor_sprite.texture:
            self.cursor_sprite.position = (mouse_x, mouse_y)
            self.cursor_sprite_list.draw()
            if len(self.cursor_stack) > 1:
                cursor_count_text = arcade.Text(
                    str(len(self.cursor_stack)),
                    mouse_x + 15,
                    mouse_y - 15,
                    color=self.TEXT_COLOR,
                    font_size=self.FONT_SIZE,
                    anchor_x="center"
                )
                cursor_count_text.draw()

        if self.hovered_item_stack:
            item, name, desc = self.hovered_item_stack[0], self.hovered_item_stack[0].params.get("name", "Unknown"), self.hovered_item_stack[0].params.get("description", "")
            text_obj = arcade.Text(f"{name}\n{desc}", 0, 0, self.TEXT_COLOR, self.FONT_SIZE, multiline=True, width=self.TOOLTIP_WIDTH)
            box_width, box_height = text_obj.content_width + 20, text_obj.content_height + 20
            box_x, box_y = mouse_x + box_width/2 + 10, mouse_y - box_height/2 - 10
            tooltip_shapes = arcade.shape_list.ShapeElementList(); tooltip_bg = arcade.shape_list.create_rectangle_filled(box_x, box_y, box_width, box_height, self.TOOLTIP_COLOR); tooltip_shapes.append(tooltip_bg); tooltip_shapes.draw()
            text_obj.position = (box_x - box_width/2 + 10, box_y + box_height/2 - text_obj.content_height/2 + self.FONT_SIZE/2); text_obj.draw()