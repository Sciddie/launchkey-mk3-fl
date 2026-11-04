import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(ROOT, "src", "LaunchkeyMK3Full")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
