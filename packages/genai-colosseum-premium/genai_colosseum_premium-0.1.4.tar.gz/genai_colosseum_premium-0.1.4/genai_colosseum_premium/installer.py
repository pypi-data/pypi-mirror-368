# installer.py
import os
import shutil
from pkg_resources import resource_filename
from pathlib import Path

def list_templates():
    base = resource_filename("genai_colosseum_premium", "templates")
    return [name for name in os.listdir(base) if os.path.isdir(os.path.join(base, name))]

def install_template(name):
    base = resource_filename("genai_colosseum_premium", "templates")
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
