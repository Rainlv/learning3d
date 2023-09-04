import os
import sys
from pathlib import Path


def fix_import_path():
    if Path(__file__).resolve().parent.name == 'examples':
        sys.path.insert(0, Path(__file__).resolve().parent.parent.as_posix())
        os.chdir(Path(__file__).resolve().parent.parent.parent.as_posix())


if __name__ == '__main__':
    fix_import_path()
