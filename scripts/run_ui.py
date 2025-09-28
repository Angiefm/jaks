import subprocess
import sys
from pathlib import Path

def main():
    ui_path = Path(__file__).parent.parent / "ui" / "main.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(ui_path)])

if __name__ == "__main__":
    main()