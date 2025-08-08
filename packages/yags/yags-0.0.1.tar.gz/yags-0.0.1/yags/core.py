import subprocess
import sys
import os
import click

def run_command(command, capture=True, env=None):
    try:
        if capture:
            result = subprocess.run(
                command, check=True, text=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
            )
            return result.stdout.strip()
        else:
            subprocess.run(
                command, check=True, text=True, stderr=subprocess.PIPE, env=env
            )
            return ""
    except FileNotFoundError:
        click.secho("Error: git not found. Is Git installed?", fg='red', bold=True)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if "rebase" in command and e.returncode == 1:
            raise e
        click.secho(f"Git error: {e.stderr.strip()}", fg='red')
        sys.exit(1)

def get_main_branch_name():
    for branch in ['main', 'master']:
        try:
            run_command(['git', 'rev-parse', '--verify', branch])
            return branch
        except subprocess.CalledProcessError:
            continue
    click.secho("Error: No main/master branch found.", fg='red', bold=True)
    sys.exit(1)

def get_commits_since(base):
    try:
        log_output = run_command(['git', 'log', f'{base}..HEAD', '--pretty=format:%H|%P|%s', '--reverse'])
        if not log_output:
            return []
        commits = []
        for line in log_output.splitlines():
            parts = line.split('|', 2)
            if len(parts) == 3:
                commits.append((parts[0], parts[1], parts[2]))
        return commits
    except subprocess.CalledProcessError:
        return []

def get_user_editor():
    try:
        return run_command(['git', 'var', 'GIT_EDITOR'])
    except subprocess.CalledProcessError:
        return os.environ.get('EDITOR', 'vim')