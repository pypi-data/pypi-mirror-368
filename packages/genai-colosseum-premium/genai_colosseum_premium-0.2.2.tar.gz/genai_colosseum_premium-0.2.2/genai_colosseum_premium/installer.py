import os
import shutil
from pathlib import Path
import importlib.resources as resources


def list_templates():
    try:
        base = resources.files("genai_colosseum_premium.templates")
    except ModuleNotFoundError:
        print("❌ Templates package not found.")
        return []

    return [
        name.name
        for name in base.iterdir()
        if name.is_dir()
    ]


def install_template(name):
    try:
        base = resources.files("genai_colosseum_premium.templates")
    except ModuleNotFoundError:
        print("❌ Templates package not found.")
        return

    src = base / name
    if not src.exists():
        print("❌ Template not found.")
        return

    dst = Path.cwd() / name
    if dst.exists():
        print("⚠️ Destination already exists.")
        return

    shutil.copytree(src, dst)
    print(f"✅ Installed template '{name}' to {dst}")
