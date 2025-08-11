import os
import shutil
from pathlib import Path
import importlib.resources as pkg_resources

def list_templates():
    with pkg_resources.path("genai_colosseum_premium.templates", "") as base:
        return [name for name in os.listdir(base) if os.path.isdir(os.path.join(base, name))]

def install_template(name):
    with pkg_resources.path("genai_colosseum_premium.templates", "") as base:
        src = os.path.join(base, name)
        if not os.path.exists(src):
            print("❌ Template not found.")
            return
        dst = Path.cwd() / name
        if dst.exists():
            print("⚠️ Destination already exists.")
            return
        shutil.copytree(src, dst)
        print(f"✅ Installed template '{name}' to {dst}")
