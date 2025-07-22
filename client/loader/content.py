import yaml
from pathlib import Path
import os
import sys

# Cache for storing previously queried objects
_content_cache = {}

def get_object_properties(obj_name):
    """Get properties for any object by its exact name, regardless of where it's located in the content structure"""
    # Check cache first
    if obj_name in _content_cache:
        return _content_cache[obj_name]

    def search_dict(d, obj_name):
        """Recursively search through a dictionary for the object name"""
        if not isinstance(d, dict):
            return None
            
        # Check if the object is directly in this dictionary
        if obj_name in d:
            return d[obj_name]
            
        # Recursively search through all values
        for value in d.values():
            if isinstance(value, dict):
                result = search_dict(value, obj_name)
                if result is not None:
                    return result
        return None
    
    # Search through all loaded content
    for data in yml_content.values():
        if isinstance(data, dict):
            result = search_dict(data, obj_name)
            if result is not None:
                # Store in cache before returning
                cached_result = {
                    'name': obj_name,
                    **result
                }
                _content_cache[obj_name] = cached_result
                return cached_result
    return None

# Clear cache when content is reloaded
def clear_content_cache():
    """Clear the content cache when content is reloaded"""
    _content_cache.clear()

def get_content_dir():
    # Get the base directory (works for both development and executable)
    if getattr(sys, 'frozen', False):
        # Running as executable
        base_path = sys._MEIPASS
    else:
        # Running in development mode
        base_path = Path(__file__).parent.parent.parent
    
    return Path(base_path) / "assets" / "content"

yml_content = {}

def loader():
    content_dir = get_content_dir()
    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory {content_dir} not found")
    yml_content.clear()
    for file in content_dir.glob("*.yml"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is not None:
                    yml_content[file.stem] = data
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

    # Immediately remove the local map content after loading.
    # The client will wait for the map from the server instead.
    if "map" in yml_content:
        del yml_content["map"]

    return yml_content

def load_content():
    #print(loader())
    return loader()

def update_prototype(prototype_name, updates):
    """
    Update a prototype in memory without modifying the original file.
    
    Args:
        prototype_name (str): The exact name of the prototype to update
        updates (dict): Dictionary of key-value pairs to update in the prototype
        
    Returns:
        bool: True if the prototype was found and updated, False otherwise
    """
    # Clear the cache for this prototype if it exists
    _content_cache.pop(prototype_name, None)
    
    # Search through all loaded content to find the prototype
    for content in yml_content.values():
        if not isinstance(content, dict):
            continue
            
        # Check if this is the prototype we're looking for
        if prototype_name in content:
            # Update the prototype with new values
            content[prototype_name].update(updates)
            return True
            
        # Recursively search through nested dictionaries
        for value in content.values():
            if isinstance(value, dict) and prototype_name in value:
                value[prototype_name].update(updates)
                return True
                
    return False