from typing import Dict, List

import torch


class Registry:
    def __init__(self) -> None:
        self._models = {}
        self._data = None

    def register_model(self, models: List[torch.nn.Module]) -> None:
        for model in models:
            self._models[model.__class__.__name__] = model

    def get_model(self) -> Dict[str, torch.nn.Module]:
        return self._models
