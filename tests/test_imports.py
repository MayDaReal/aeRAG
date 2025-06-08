"""
Smoke test: ensure all modules are importable without error.
Useful to catch syntax or path issues early.
"""
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def iter_python_files():
    excluded = {"tests", "venv", ".venv", "env", "site-packages", "__pypackages__"}
    for path in ROOT.rglob("*.py"):
        if any(part in excluded for part in path.parts):
            continue
        yield path

def module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

def test_all_modules_importable():
    errors = []
    for path in iter_python_files():
        name = module_name(path)
        try:
            importlib.import_module(name)
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    assert not errors, "Import errors:\n" + "\n".join(errors)