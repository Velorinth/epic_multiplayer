import yaml
from pathlib import Path
import os
import sys

def get_object_properties(obj_name):
    """Get properties for any object by its exact name, regardless of where it's located in the content structure"""
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
                return {
                    'name': obj_name,
                    **result
                }
    return None

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
    return yml_content

def load_content():
    print(loader())
    return loader()