import os

REPO_DIR = '/home/ambi_dex/projects/replog/mirror/'

def list_repo_files():
    entries = []
    for name in os.listdir(REPO_DIR):
        if name.startswith('.'):
            continue
        if name in ('venv', '__pycache__', '.mypy_cache'):
            continue
        full = os.path.join(REPO_DIR, name)
        entries.append({
            "name" : name,
            'is_dir' : os.path.isdir(full),
            })
    return entries
