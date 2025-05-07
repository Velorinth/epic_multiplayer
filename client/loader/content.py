import yaml
from pathlib import Path
import os

def get_content_dir():
    return Path(__file__).parent.parent / "assets" / "content"

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
    return loader()