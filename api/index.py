import sys
import os

# Ensure project root is in path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app import create_app

app = create_app()
