from collections import defaultdict
from typing import Callable, Dict, List

import torch
from torch import nn


class HookManager:
    def __init__(self, track_all: bool = False) -> None:
        self.track_all = track_all
        self.hooks = []
        self.activations = defaultdict(list) if track_all else {}
        self.inputs = defaultdict(list) if track_all else {}
        self.gradients = defaultdict(list) if track_all else {}
        self.weights = defaultdict(list[str]) if track_all else {}

    def _hook_fn(self, name: str) -> Callable:
        def hook(module: nn.Module, input, output):
            out = output.detach().cpu()
            inp = input[0].detach().cpu()

            if self.track_all:
                self.activations[name].append(out)
                self.inputs[name].append(inp)
            else:
                self.activations[name] = out
                self.inputs[name] = inp

        return hook

    def _grad_hook_fn(self, name: str) -> Callable:
        def hook(module: nn.Module, grad_input, grad_output):
            grad = grad_output[0].detach().cpu()

            if self.track_all:
                self.gradients[name].append(grad)
            else:
                self.gradients[name] = grad

        return hook

    def count_module_type(self, model: nn.Module) -> Dict[str, int]:
        type_counter = defaultdict(int)

        for _, module in model.named_modules():
            module_type = str(module).split("(")[0].strip()
            type_counter[module_type] += 1

        return type_counter

    def register_hooks(
        self,
        model: nn.Module,
        partial_matches: List[str] = ["ALL"],
    ) -> None:
        """
        Module:

        Model class, Sequential, and every single component
        Single component will have no children.
        """
        type_counter = defaultdict(int)

        for _, module in model.named_modules():
            if len(list(module.children())) == 0:
                module_type = str(module).split("(")[0].strip()
                idx = type_counter[module_type]
                module_name = f"{module_type}:{idx}"
                type_counter[module_type] += 1

                if partial_matches != ["ALL"]:
                    for partial_match in partial_matches:
                        if partial_match and partial_match in str(module):
                            self.hooks.append(
                                module.register_forward_hook(self._hook_fn(module_name))
                            )
                            self.hooks.append(
                                module.register_full_backward_hook(
                                    self._grad_hook_fn(module_name)
                                )
                            )
                            if hasattr(module, "weight"):
                                self.weights[module_name] = (
                                    torch.tensor(module.weight).detach().cpu()
                                )
                else:
                    self.hooks.append(
                        module.register_forward_hook(self._hook_fn(module_name))
                    )
                    self.hooks.append(
                        module.register_full_backward_hook(
                            self._grad_hook_fn(module_name)
                        )
                    )
                    if hasattr(module, "weight"):
                        self.weights[module_name] = (
                            torch.tensor(module.weight).detach().cpu()
                        )

    def clear_hooks(self) -> None:
        for hook in self.hooks:
            hook.remove()

        self.hooks = []

    def get_activations(self) -> Dict:
        if self.track_all:
            return {k: torch.stack(v) for k, v in self.activations.items()}

        return self.activations

    def get_inputs(self) -> Dict:
        if self.track_all:
            return {k: torch.stack(v) for k, v in self.inputs.items()}

        return self.inputs

    def get_gradients(self) -> Dict:
        if self.track_all:
            return {k: torch.stack(v) for k, v in self.gradients.items()}

        return self.gradients

    def get_weights(self) -> Dict:
        return self.weights
