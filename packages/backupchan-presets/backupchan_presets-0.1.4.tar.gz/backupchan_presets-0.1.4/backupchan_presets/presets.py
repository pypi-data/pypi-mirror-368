from backupchan import API
from dataclasses import dataclass, asdict
from pathlib import Path
import os
import json
import platformdirs

CONFIG_FILE_DIR = platformdirs.user_config_dir("backupchan")
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/presets.json"

class PresetError(Exception):
    pass

@dataclass
class Preset:
    location: str
    target_id: str

    def upload(self, api: API, manual: bool) -> str:
        if not os.path.exists(self.location):
            raise PresetError(f"No such file or directory: {self.location}")

        if os.path.isdir(self.location):
            return api.upload_backup_folder(self.target_id, self.location, manual)
        else:
            with open(self.location, "rb") as file:
                return api.upload_backup(self.target_id, file, os.path.basename(self.location), manual)

    @staticmethod
    def from_dict(d: dict) -> "Preset":
        return Preset(d["location"], d["target_id"])

class Presets:
    def __init__(self, config_path: str | None = None):
        self.presets: dict[str, Preset] = {}
        self.config_path = CONFIG_FILE_PATH if config_path is None else config_path

    def load(self):
        if not os.path.exists(self.config_path):
            return

        self.presets = {}
        with open(self.config_path, "r") as config_file:
            config = json.load(config_file)
            for json_preset in config["presets"]:
                self.presets[json_preset["name"]] = Preset.from_dict(json_preset)

    def save(self):
        Path(os.path.dirname(self.config_path)).mkdir(exist_ok=True, parents=True)

        presets_list = []

        for name, preset in self.presets.items():
            presets_list.append({
                "name": name,
                "location": preset.location,
                "target_id": preset.target_id
            })

        presets_dict = {
            "presets": presets_list
        }

        with open(self.config_path, "w") as config_file:
            json.dump(presets_dict, config_file)

    def add(self, name: str, location: str, target_id: str):
        if name in self.presets:
            raise PresetError(f"Preset '{name}' already exists")

        self.presets[name] = Preset(location, target_id)

    def remove(self, name: str):
        del self.presets[name]

    def __getitem__(self, name: str) -> Preset:
        return self.presets[name]

    def __iter__(self):
        return iter(self.presets.keys())

    def __len__(self):
        return len(self.presets)
