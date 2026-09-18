$ErrorActionPreference = "Stop"

# Start from the project directory regardless of the caller's current folder.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    # Create the virtual environment on the first run.
    python -m venv .venv
}

# Install dependencies and run the Python launcher.
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".venv\Scripts\python.exe" app_launcher.py
