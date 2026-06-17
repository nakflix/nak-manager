from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
raise Exception("GITHUB_TOKEN not found in .env")

with open("repos.txt") as f:
repos = [r.strip() for r in f.readlines() if r.strip()]

SUPERVISOR_DIR = "/etc/supervisor/conf.d"
LOG_DIR = "/var/log"

os.makedirs(LOG_DIR, exist_ok=True)

for repo in repos:

```
repo_name = repo.split("/")[-1].replace(".git", "")
repo_path = f"/root/{repo_name}"

print(f"\n=== Processing {repo_name} ===")

auth_repo = repo.replace(
    "https://",
    f"https://{TOKEN}@"
)

# Clone repo if missing
if not os.path.exists(repo_path):
    subprocess.run(
        ["git", "clone", auth_repo, repo_path],
        check=False
    )

# Create virtual environment
venv_path = f"{repo_path}/venv"

if not os.path.exists(venv_path):
    subprocess.run(
        ["python3", "-m", "venv", venv_path],
        check=False
    )

pip_path = f"{venv_path}/bin/pip"
python_path = f"{venv_path}/bin/python"

# Upgrade pip
subprocess.run(
    [pip_path, "install", "--upgrade", "pip"],
    check=False
)

# Install requirements
req_path = f"{repo_path}/requirements.txt"

if os.path.exists(req_path):
    subprocess.run(
        [pip_path, "install", "-r", req_path],
        check=False
    )

# Detect startup file
startup_files = [
    "main.py",
    "bot.py",
    "app.py",
    "run.py",
    "start.py"
]

main_file = None

for file in startup_files:
    if os.path.exists(f"{repo_path}/{file}"):
        main_file = file
        break

if not main_file:
    print(f"Skipping {repo_name}: no startup file found")
    continue

out_log = f"{LOG_DIR}/{repo_name}.out.log"
err_log = f"{LOG_DIR}/{repo_name}.err.log"

supervisor_conf = f"""
```

[program:{repo_name}]
directory={repo_path}
command={python_path} {main_file}
autostart=true
autorestart=true
startsecs=10
stdout_logfile={out_log}
stderr_logfile={err_log}
redirect_stderr=false
"""

```
conf_path = f"{SUPERVISOR_DIR}/{repo_name}.conf"

with open(conf_path, "w") as conf_file:
    conf_file.write(supervisor_conf)

print(f"Created supervisor config for {repo_name}")
```

print("\nReloading supervisor...")

subprocess.run(["supervisorctl", "reread"], check=False)
subprocess.run(["supervisorctl", "update"], check=False)

print("\nDone.")
