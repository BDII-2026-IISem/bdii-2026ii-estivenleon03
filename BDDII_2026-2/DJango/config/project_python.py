import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def use_project_python():
    venv_root = PROJECT_ROOT / ".venv"
    venv_python = venv_root / "bin" / "python"
    if not venv_python.is_file():
        return
    if Path(sys.prefix).resolve() == venv_root.resolve():
        return
    os.execv(venv_python, [str(venv_python), *sys.argv])
