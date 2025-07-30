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

def get_objects_by_property(prop_key: str, prop_value) -> list:
    found_objects = []
    
    def search_recursive(d):
        for key, value in d.items():
            if isinstance(value, dict):
                # Check if the dictionary itself is the object we want
                if value.get(prop_key) == prop_value:
                    found_objects.append(value)
                # Continue searching deeper
                search_recursive(value)

    for category in yml_content.values():
        if isinstance(category, dict):
            search_recursive(category)
            
    return found_objects