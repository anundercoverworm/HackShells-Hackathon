$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Find-Python {
    $localPython = Join-Path $root ".venv\Scripts\python.exe"
    if (Test-Path $localPython) {
        return $localPython
    }

    foreach ($command in @("py", "python")) {
        $candidate = Get-Command $command -ErrorAction SilentlyContinue
        if ($candidate) {
            return $candidate.Source
        }
    }

    return $null
}

$python = Find-Python

if (-not $python) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "Python was not found. Install Python 3.11 or newer and run this file again."
        Read-Host "Press Enter to close"
        exit 1
    }

    Write-Host "Python was not found. Installing Python 3.12 with winget..."
    winget install --id Python.Python.3.12 --exact --scope user --accept-package-agreements --accept-source-agreements
    $python = Find-Python
}

if (-not (Test-Path (Join-Path $root ".venv\Scripts\python.exe"))) {
    Write-Host "Creating the local environment..."
    & $python -m venv .venv
}

$python = Join-Path $root ".venv\Scripts\python.exe"
Write-Host "Installing application dependencies..."
& $python -m pip install --disable-pip-version-check -r requirements.txt

$launcher = Join-Path $root "dist\CollectionTrackerLauncher.exe"
if (Test-Path $launcher) {
    Start-Process -FilePath $launcher -WorkingDirectory $root
} else {
    & $python app_launcher.py
}
