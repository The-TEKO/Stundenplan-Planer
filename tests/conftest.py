from pathlib import Path
import sys


def _ensure_src_on_path():
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"
    src_as_text = str(src_path)
    if src_as_text not in sys.path:
        sys.path.insert(0, src_as_text)


_ensure_src_on_path()
