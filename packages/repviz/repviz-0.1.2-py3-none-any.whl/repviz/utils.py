import re
import ast
from typing import Any, Dict

from torch import nn


def tolist_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v.tolist() if hasattr(v, "tolist") else v for k, v in d.items()}


def parse_args_kwargs_from_repr(repr_str: str):
    """
    Parse the positional args and keyword args from a nn.Module repr string.

    Example:
        "LayerNorm((54,), eps=1e-05, elementwise_affine=True)"
        --> args: ((54,),), kwargs: {'eps': 1e-05, 'elementwise_affine': True}
    """
    # Match the first '(' to the last ')' to get argument section
    match = re.search(r"\((.*)\)", repr_str)
    if not match:
        return (), {}

    content = match.group(1).strip()
    args = []
    kwargs = {}

    # This regex splits by commas not inside parentheses
    tokens = re.findall(r"(?:[^,(]|\([^)]*\))+", content)

    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            key, val = token.split("=", 1)
            try:
                kwargs[key.strip()] = ast.literal_eval(val.strip())
            except Exception:
                kwargs[key.strip()] = val.strip()  # fallback: string
        else:
            try:
                args.append(ast.literal_eval(token))
            except Exception:
                args.append(token.strip())  # fallback: string

    return tuple(args), kwargs


def get_model_info(model: nn.Module) -> Dict[str, Any]:
    infos = {}

    for name, module in model.named_modules():
        if len(list(module.children())) == 0:
            args, kwargs = parse_args_kwargs_from_repr(str(module))
            module_type = str(module).split("(")[0].strip()
            infos[name] = {
                "module_type": module_type,
                "args": args,
                "kwargs": kwargs,
            }

    return infos
