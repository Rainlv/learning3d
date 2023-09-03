import os
import sys
from pathlib import Path


def fix_import_path():
    if Path(__file__).resolve().parent.name == 'examples':
        sys.path.append(Path(__file__).resolve().parent.parent.parent.as_posix())
        sys.path.append(Path(__file__).resolve().parent.parent.as_posix())
        os.chdir(Path(__file__).resolve().parent.parent.parent.as_posix())