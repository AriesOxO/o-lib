import os
import sys
from pathlib import Path

# offscreen mode for headless testing
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# 确保项目根在 sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
