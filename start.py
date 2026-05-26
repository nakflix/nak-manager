import os
import subprocess

TOKEN = os.environ.get("GITHUB_TOKEN")

with open("repos.txt") as f:
    repos = [r.strip() for r in f.readlines() if r.strip()]

supervisor_config = """
[supervisord]
nodaemon=true
"""

port = 8080

for repo in repos:

    repo_name = repo.split("/")[-1].replace(".git", "")

    auth_repo = repo.replace(
        "https://",
        f"https://{TOKEN}@"
    )

    # Clone repo
    if not os.path.exists(repo_name):
        subprocess.run(["git", "clone", auth_repo])

    # Install requirements
    req_path = f"{repo_name}/requirements.txt"

    if os.path.exists(req_path):
        subprocess.run([
            "pip",
            "install",
            "--no-cache-dir",
            "-r",
            req_path
        ])

    # Detect startup file
    if os.path.exists(f"{repo_name}/main.py"):
        main_file = "main.py"

    elif os.path.exists(f"{repo_name}/bot.py"):
        main_file = "bot.py"

    elif os.path.exists(f"{repo_name}/app.py"):
        main_file = "app.py"

    else:
        print(f"No startup file found for {repo_name}")
        continue

    # Generate supervisor config
    supervisor_config += f"""
[program:{repo_name}]
command=python {main_file}
directory=/app/{repo_name}
environment=PORT="{port}"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
"""

    port += 1

# Write supervisor config
with open("supervisor.conf", "w") as f:
    f.write(supervisor_config)

# Start supervisor
subprocess.run([
    "supervisord",
    "-c",
    "/app/supervisor.conf"
])
