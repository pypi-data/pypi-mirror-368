from pathlib import Path
from typing import Any

import yaml

from tesorotools.utils.template import TemplateLoader


def clean_config_dicts(config_dicts: dict[str, Any]):
    if config_dicts is None:
        return None
    return {k: v for k, v in config_dicts.items() if not k.startswith(".")}


# maybe a dedicated function for templates would be nice
def read_config(
    config_file: Path, loader: yaml.FullLoader = None, clean: bool = True
) -> Any | dict:
    loader = yaml.FullLoader if loader is None else TemplateLoader
    with open(config_file, encoding="utf8") as file:
        config_dict = yaml.load(file, Loader=loader)
        if clean and isinstance(config_dict, dict):
            config_dict = clean_config_dicts(config_dict)
    return config_dict


def merge(a: dict, b: dict):
    # a overrides
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key])
        else:
            a[key] = b[key]
    return a
