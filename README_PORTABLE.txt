COLLECTION TRACKER - PORTABLE PACKAGE

1. Extract the complete folder.
2. Run install_and_run.ps1 with PowerShell.
3. The script installs Python if winget is available, creates .venv, installs dependencies, and opens the app.

The application opens at http://127.0.0.1:8503.
The backend uses http://127.0.0.1:8001.

Do not delete the backend, frontend, data, or dist folders.
The real .env file is intentionally not included. Copy values from .env.example if an OpenAI key is needed.
