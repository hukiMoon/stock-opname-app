import sys
import os

# Fungsi ini akan menambahkan folder root ke path sistem
def setup_path():
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if root_path not in sys.path:
        sys.path.append(root_path)

setup_path()
