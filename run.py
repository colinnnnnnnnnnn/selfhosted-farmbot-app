import subprocess
import sys
import os
import atexit


PYTHON_EXECUTABLE = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')


NPM_CMD = 'npm.cmd' if sys.platform == 'win32' else 'npm'


processes = []

def run_command(command, cwd=None):
    print(f"$ {' '.join(command)}")
    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}", file=sys.stderr)
        sys.exit(1)

def cleanup():
    for p in processes:
        print(f"Stopping process {p.pid}...")
        p.terminate()

atexit.register(cleanup)

def main():
    print("Setting up backend")
    run_command([PYTHON_EXECUTABLE, "-m", "pip", "install", "-r", "requirements.txt"])
    run_command([PYTHON_EXECUTABLE, "manage.py", "migrate"])

    print("\nSetting up frontend")
    run_command([NPM_CMD, "install"], cwd=FRONTEND_DIR)

    print("\nStarting servers")
    print("Press CTRL+C to stop all servers")

    try:
        backend_process = subprocess.Popen(
            [PYTHON_EXECUTABLE, "manage.py", "runserver", "0.0.0.0:8000"],
        )
        processes.append(backend_process)
        print(f"Started backend server with PID: {backend_process.pid}")

        frontend_process = subprocess.Popen(
            [NPM_CMD, "start"],
            cwd=FRONTEND_DIR
        )
        processes.append(frontend_process)
        print(f"Started frontend server with PID: {frontend_process.pid}")
        os.waitpid(backend_process.pid, 0)

    except KeyboardInterrupt:
        print("\nCTRL+C detected. Shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()