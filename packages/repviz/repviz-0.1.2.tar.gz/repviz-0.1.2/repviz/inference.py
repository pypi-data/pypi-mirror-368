from typing import Optional, Union, Dict, Any

import torch
import numpy as np

from .registry import Registry
from .hooks import HookManager
from .utils import get_model_info


def run_inference(
    registry: Registry,
    data: Union[np.ndarray, torch.Tensor],
    label: Optional[np.ndarray] = None,
    device: Union[torch.device, str] = "cpu",
    get_gradients: bool = False,
) -> Dict[str, Any]:
    device = torch.device(device)
    models = registry.get_model()

    results = {}

    for model_name, model in models.items():
        model.eval()
        model_info = get_model_info(model)
        model_hook_mgr = HookManager(track_all=True)
        model_hook_mgr.register_hooks(model, partial_matches=["ALL"])

        if get_gradients and label is not None:
            if isinstance(data, np.ndarray):
                ts_x = torch.tensor(data, dtype=torch.float32).to(device)
                ts_y = torch.tensor(label, dtype=torch.long).to(device)
            else:
                ts_x = data.to(device)
                ts_y = label.to(device)

            output = model(ts_x)
            loss = torch.nn.CrossEntropyLoss()(output, ts_y)
            loss.backward()
            activations = {k: v for k, v in model_hook_mgr.get_activations().items()}
            weights = {k: v for k, v in model_hook_mgr.get_weights().items()}
            gradients = {k: v for k, v in model_hook_mgr.get_gradients().items()}
            preds = output.detach().cpu().numpy()

        else:
            with torch.no_grad():
                if isinstance(data, np.ndarray):
                    ts_x = torch.tensor(data, dtype=torch.float32).to(device)
                else:
                    ts_x = data.to(device)

                output = model(ts_x)
                activations = {
                    k: v for k, v in model_hook_mgr.get_activations().items()
                }
                weights = {k: v for k, v in model_hook_mgr.get_weights().items()}
                gradients = {k: v for k, v in model_hook_mgr.get_gradients().items()}
                preds = output.detach().cpu().numpy()

        model_hook_mgr.clear_hooks()

        results[model_name] = {
            "model_info": model_info,
            "activations": activations,
            "weights": weights,
            "gradients": gradients,
            "predictions": preds,
        }

    return results

    # with open(os.path.join(output_path, "model_structure.json"), "w") as f:
    #     json.dump(model_info, f)

    # with open(os.path.join(output_path, "activations.json"), "w") as f:
    #     json.dump(activations, f)

    # with open(os.path.join(output_path, "weights.json"), "w") as f:
    #     json.dump(weights, f)

    # with open(os.path.join(output_path, "gradients.json"), "w") as f:
    #     json.dump(gradients, f)

    # with open(os.path.join(output_path, "predictions.json"), "w") as f:
    #     json.dump(preds, f)
