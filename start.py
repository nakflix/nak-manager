from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

TOKEN = os.environ.get("GITHUB_TOKEN")

with open("repos.txt") as f:
    repos = [r.strip() for r in f.readlines() if r.strip()]

SUPERVISOR_DIR = "/etc/supervisor/conf.d"
LOG_DIR = "/var/log"

os.makedirs(LOG_DIR, exist_ok=True)

for repo in repos:

    repo_name = repo.split("/")[-1].replace(".git", "")
    repo_path = f"/root/{repo_name}"

    auth_repo = repo.replace("https://", f"https://{TOKEN}@")

    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", auth_repo, repo_path])

    if os.path.exists(f"{repo_path}/main.py"):
        main_file = "main.py"
    elif os.path.exists(f"{repo_path}/bot.py"):
        main_file = "bot.py"
    else:
        main_file = "start.py"

    conf = f"""
[program:{repo_name}]
directory={repo_path}
command=python3 {main_file}
autostart=true
autorestart=true
stderr_logfile={LOG_DIR}/{repo_name}.err.log
stdout_logfile={LOG_DIR}/{repo_name}.out.log
"""

    with open(f"{SUPERVISOR_DIR}/{repo_name}.conf", "w") as f:
        f.write(conf)

subprocess.run(["supervisorctl", "reread"])
subprocess.run(["supervisorctl", "update"])
