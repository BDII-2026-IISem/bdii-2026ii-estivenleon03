"""
Intérprete del proyecto.
Los paquetes se instalan dentro de .venv. El comando python3 manage.py
usa el Python del sistema y no ve esos paquetes.
use_project_python() vuelve a lanzar el mismo comando con .venv/bin/python.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def use_project_python():
    """Reejecuta el proceso con el Python de .venv si aún no es ese intérprete."""
    venv_root = PROJECT_ROOT / ".venv"
    venv_python = venv_root / "bin" / "python"

    if not venv_python.is_file():
        return

    try:
        if Path(sys.prefix).resolve() == venv_root.resolve():
            return
    except OSError:
        return

    os.execv(venv_python, [str(venv_python), *sys.argv])
