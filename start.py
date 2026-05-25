import os
import subprocess

TOKEN = os.environ.get("GITHUB_TOKEN")

with open("repos.txt") as f:
    repos = [r.strip() for r in f.readlines() if r.strip()]

supervisor_config = """
[supervisord]
nodaemon=true
"""

for i, repo in enumerate(repos, start=1):

    repo_name = repo.split("/")[-1].replace(".git", "")

    auth_repo = repo.replace(
        "https://",
        f"https://{TOKEN}@"
    )

    if not os.path.exists(repo_name):
        subprocess.run(["git", "clone", auth_repo])

    req_path = f"{repo_name}/requirements.txt"

    if os.path.exists(req_path):
        subprocess.run([
            "pip",
            "install",
            "--no-cache-dir",
            "-r",
            req_path
        ])

    supervisor_config += f"""
[program:{repo_name}]
command=python bot.py
directory=/app/{repo_name}
autostart=true
autorestart=true
stderr_logfile=/dev/stderr
stdout_logfile=/dev/stdout
"""

with open("supervisor.conf", "w") as f:
    f.write(supervisor_config)

subprocess.run([
    "supervisord",
    "-c",
    "/app/supervisor.conf"
])
