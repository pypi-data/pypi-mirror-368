import os
import sys
from pathlib import Path


def listdir(file: __file__):
	return os.listdir(os.path.dirname(file))

def package(file: __file__):
	project_root = Path(sys.modules['__main__'].file).resolve().parent
	current_path = Path(file).resolve()
	relative_path = current_path.relative_to(project_root)
	return ".".join(relative_path.with_suffix('').parts)

def basename(file: __file__):
	return file.split(os.sep)[-2]
