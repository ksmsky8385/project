# Tuner_RFR/tunerengine.py

import json
import random
from pathlib import Path
from typing import Dict, Any

class RandomTuner:
    def __init__(self, searchspace_path: Path):
        self.searchspace_path = searchspace_path
        self.search_space = self._load_searchspace()

    def _load_searchspace(self) -> Dict[str, Any]:
        with open(self.searchspace_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def sample_param(self, spec: dict):
        if spec["type"] == "fixed":
            return spec["fixed"]

        if spec["type"] == "categorical" and "choices" in spec:
            return random.choice(spec["choices"])

        if spec["type"] == "int" and "range" in spec:
            low, high = spec["range"]
            return random.randint(low, high)
        
        if spec["type"] == "categorical" and "choices" in spec:
            choice = random.choice(spec["choices"])
            return None if choice in [None, "None", "null"] else choice

        # 향후 float 확장 가능
        return None

    def sample_params(self) -> Dict[str, Any]:
        sampled = {}
        for key, spec in self.search_space.items():
            value = self.sample_param(spec)
            if value is not None:
                sampled[key] = value
        return sampled
