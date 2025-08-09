import os
import importlib
from pathlib import Path


def get_config():
    if not Path(".nxu.py").exists():
        print("🔍 .nxu.py文件不存在, 请先初始化项目")
        os.exit(1)
    module_name = ".nxu"
    spec = importlib.util.spec_from_file_location(module_name, Path(".nxu.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
