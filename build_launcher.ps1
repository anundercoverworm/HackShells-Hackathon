$ErrorActionPreference = "Stop"

# Build the executable from the project root.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    # PyInstaller must run inside the project's virtual environment.
    Write-Host "Virtual environment not found. Run: python -m venv .venv"
    exit 1
}

# Install the packaging tool and create a single-file Windows executable.
& ".venv\Scripts\python.exe" -m pip install pyinstaller
& ".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --name CollectionTrackerLauncher app_launcher.py

Write-Host "Launcher created at dist\CollectionTrackerLauncher.exe"
