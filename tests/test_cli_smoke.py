"""
CLI smoke test: launch main.py and verify that menu text appears.
Compatible with Windows via subprocess.
"""
import subprocess
import sys
from pathlib import Path

def test_cli_smoke():
    script = str(Path(__file__).resolve().parents[1] / "main.py")

    process = subprocess.Popen(
        [sys.executable, script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Send "0" and read output
    stdout, _ = process.communicate(input="0\n", timeout=10)

    print("STDOUT:\n", stdout)  # Debug help

    assert "Welcome to the Archethic RAG Interactive System" in stdout
    assert "Goodbye!" in stdout
