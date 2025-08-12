import importlib.metadata
from typing import Tuple

def get_module_info(module_name) -> Tuple[str, str]:
    try:
        version = importlib.metadata.version(module_name)
        return version
    except importlib.metadata.PackageNotFoundError:
        raise ValueError(f"Module '{module_name}' not found")
