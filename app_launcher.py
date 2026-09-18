import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BACKEND_PORT = 8001
FRONTEND_PORT = 8503


def project_root():
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        return executable_dir.parent if executable_dir.name.lower() == "dist" else executable_dir
    return Path(__file__).resolve().parent


def python_command(root):
    if not getattr(sys, "frozen", False):
        return [sys.executable]

    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return [str(venv_python)]

    for command in ("py", "python"):
        if shutil.which(command):
            return [command]

    raise RuntimeError("Python was not found. Install Python 3.11 or newer first.")


def ensure_environment(root):
    if not getattr(sys, "frozen", False):
        return

    venv_dir = root / ".venv"
    ready_file = venv_dir / ".collection_tracker_ready"
    if ready_file.exists():
        return

    base_python = None
    for command in ("py", "python"):
        if shutil.which(command):
            base_python = command
            break

    if base_python is None and shutil.which("winget"):
        subprocess.run(
            [
                "winget", "install", "--id", "Python.Python.3.12", "--exact",
                "--scope", "user", "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            check=True,
        )
        base_python = next((command for command in ("py", "python") if shutil.which(command)), None)

    if base_python is None:
        raise RuntimeError("Python was not found and could not be installed automatically.")

    if not (venv_dir / "Scripts" / "python.exe").exists():
        subprocess.run([base_python, "-m", "venv", str(venv_dir)], cwd=root, check=True)

    venv_python = venv_dir / "Scripts" / "python.exe"
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--disable-pip-version-check", "-r", "requirements.txt"],
        cwd=root,
        check=True,
    )
    ready_file.write_text("ready\n", encoding="ascii")


def wait_for_url(url, process, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"The process for {url} stopped unexpectedly.")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}.")


def stop_process(process):
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    root = project_root()
    os.chdir(root)
    ensure_environment(root)
    python = python_command(root)
    processes = []

    try:
        backend = subprocess.Popen(
            python + [
                "-m", "uvicorn", "backend.main:app",
                "--host", "127.0.0.1", "--port", str(BACKEND_PORT),
            ],
            cwd=root,
        )
        processes.append(backend)
        wait_for_url(f"http://127.0.0.1:{BACKEND_PORT}/api/health", backend)

        frontend = subprocess.Popen(
            python + [
                "-m", "streamlit", "run", "frontend/front_main.py",
                "--server.port", str(FRONTEND_PORT),
                "--server.headless", "true",
            ],
            cwd=root,
            env={**os.environ, "API_BASE_URL": f"http://127.0.0.1:{BACKEND_PORT}"},
        )
        processes.append(frontend)
        wait_for_url(f"http://127.0.0.1:{FRONTEND_PORT}", frontend)

        url = f"http://127.0.0.1:{FRONTEND_PORT}"
        print(f"Collection Tracker is running at {url}")
        os.startfile(url)

        while all(process.poll() is None for process in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        print(f"Could not start Collection Tracker: {error}")
        input("Press Enter to close...")
    finally:
        for process in reversed(processes):
            stop_process(process)


if __name__ == "__main__":
    main()
