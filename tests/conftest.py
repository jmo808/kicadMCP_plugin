import os
import sys

# Ensure tests/ directory is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Inject mock_pcbnew as sys.modules['pcbnew'] so imports of pcbnew work
import mock_pcbnew

sys.modules["pcbnew"] = mock_pcbnew
