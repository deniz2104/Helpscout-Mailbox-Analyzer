import os
import subprocess
import venv

def create_and_setup_venv(venv_dir="venv", requirements_file="requirements.txt"):
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in '{venv_dir}'...")
        venv.EnvBuilder(with_pip=True).create(venv_dir)
    else:
        print(f"Virtual environment '{venv_dir}' already exists.")

    python_exe = os.path.join(venv_dir, "bin", "python3")
    pip_exe = os.path.join(venv_dir, "bin", "pip3")

    print("Upgrading pip...")
    subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])

    if os.path.exists(requirements_file):
        print(f"Installing dependencies from '{requirements_file}'...")
        subprocess.check_call([pip_exe, "install", "-r", requirements_file])
    else:
        print(f"No '{requirements_file}' file found. Skipping package installation.")

if __name__ == "__main__":
    venv_dir = "venv"
    requirements_file = "requirements.txt"

    create_and_setup_venv(venv_dir, requirements_file)
