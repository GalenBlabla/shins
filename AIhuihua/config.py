# config.py
import json
from pathlib import Path

config_path = Path('config.json')
with config_path.open() as config_file:
    config = json.load(config_file)
