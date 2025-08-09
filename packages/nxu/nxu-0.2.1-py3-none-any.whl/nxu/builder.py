import importlib
from pathlib import Path
from .config import get_config


def build(config_path: Path):
    config = get_config()

    module_name = "strategy_config"
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.build(config.target_path)
    print("🎉 编译完成")
