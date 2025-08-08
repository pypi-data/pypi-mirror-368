import sys
import os
import tempfile
import time
import click
import subprocess

from yags.core import (
    run_command,
    get_main_branch_name,
    get_commits_since,
)

def display_squash_preview(all_commits, first_idx, last_idx):
    first_0 = first_idx - 1
    last_0 = last_idx - 1
    
    context_lines = 2

    click.secho("\n--- BEFORE ---", fg='yellow', bold=True)
    
    if first_0 > 0:
        click.echo("  ...")
    start = first_0 - context_lines
    if start < 0:
        start = 0
    for i in range(start, first_0):
        commit = all_commits[i]

        click.echo(f"  * {i+1:2d}) {commit['hash']} {commit['message'][:50]}")

    click.secho("\n  // To be squashed into one:", fg='cyan')
    click.echo("  [")
    for i in range(first_0, last_0 + 1):
        commit = all_commits[i]
        click.echo(f"    * {i+1:2d}) {click.style(commit['hash'], fg='yellow')} {commit['message'][:50]}")
    click.echo("  ]")

    if last_0 < len(all_commits) - 1:
        end_idx = last_0 + 1 + context_lines
        for i in range(last_0 + 1, len(all_commits)):
            if i >= end_idx:
                break
            commit = all_commits[i]
            click.echo(f"  * {i+1:2d}) {commit['hash']} {commit['message'][:50]}")
        
        if end_idx < len(all_commits):
            click.echo("  ...")
    
    click.secho("\n--- AFTER ---", fg='green', bold=True)
    
    if first_0 > 0:
        click.echo("  ...")
    for i in range(max(0, first_0 - context_lines), first_0):
        commit = all_commits[i]
        click.echo(f"  * {i+1:2d}) {commit['hash']} {commit['message'][:50]}")
    
    click.secho("\n  + ---- NEW SQUASHED COMMIT ----", bold=True)

    if last_0 < len(all_commits) - 1:
        click.echo("")
        end_idx = last_0 + 1 + context_lines
        for i in range(last_0 + 1, len(all_commits)):
            if i >= end_idx:
                break
            commit = all_commits[i]
            click.echo(f"  * {i+1:2d}) {commit['hash']} {commit['message'][:50]}")
        
        if end_idx < len(all_commits):
            click.echo("  ...")

def create_backup_branch():
    timestamp = int(time.time())
    backup_name = f"yags-backup-{timestamp}"
    try:
        run_command(['git', 'branch', backup_name])
        click.secho(f"Created backup branch: {backup_name}")
        return backup_name
    except subprocess.CalledProcessError as e:
        click.secho(f"Failed to create backup: {e}", fg='red')
        return None

def get_latest_backup():
    try:
        result = run_command(['git', 'branch', '--list', 'yags-backup-*'])
        if not result.strip():
            return None
        
        branches = result.strip().split('\n')
        
        clean_branches = []
        for branch in branches:
            clean_name = branch.strip()
            if clean_name.startswith('* '):
                clean_name = clean_name[2:]
            clean_branches.append(clean_name)
        
        latest_branch = None
        latest_timestamp = 0
        
        for branch in clean_branches:
            parts = branch.split('-')
            timestamp = int(parts[-1])
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_branch = branch
        
        return latest_branch
        
    except (subprocess.CalledProcessError, ValueError):
        return None
    
def get_commit_range_input(recent_commits):
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            click.secho("Pick the range to squash:", fg='green', bold=True)
            click.echo("Enter TWO numbers: the FIRST and LAST commits to squash")
            click.echo("(e.g., '2 5' to squash commits 2, 3, 4, and 5 into one)")
            click.echo(f"Valid range: 1 to {len(recent_commits)}")
            
            range_input = click.prompt("Range (first last)").strip()
            
            parts = range_input.split()
            
            if len(parts) != 2:
                if len(parts) == 1:
                    click.secho("Error: Please provide TWO numbers (first and last)", fg='red')
                    click.secho("Example: '2 5' means squash commits 2 through 5", fg='yellow')
                else:
                    click.secho(f"Error: Expected 2 numbers, but got {len(parts)}: {parts}", fg='red')
                    click.secho("Please enter exactly TWO numbers separated by a space", fg='yellow')
                
                if attempt < max_attempts - 1:
                    click.echo("Please try again...\n")
                    continue
                else:
                    click.secho("Too many invalid attempts. Exiting.", fg='red')
                    sys.exit(1)
            
            try:
                first, last = map(int, parts)
            except ValueError:
                click.secho(f"Error: Both inputs must be numbers. Got: '{range_input}'", fg='red')
                if attempt < max_attempts - 1:
                    click.echo("Please try again...\n")
                    continue
                else:
                    sys.exit(1)
            
            if first < 1 or last < 1 or first > len(recent_commits) or last > len(recent_commits):
                click.secho(f"Error: Numbers must be between 1 and {len(recent_commits)}", fg='red')
                click.secho(f"You entered: first={first}, last={last}", fg='yellow')
                if attempt < max_attempts - 1:
                    click.echo("Please try again...\n")
                    continue
                else:
                    sys.exit(1)
                
            if first > last:
                first, last = last, first 
                click.secho(f"Swapped order: will squash commits {first} through {last}", fg='yellow')
            
            click.secho(f"\nWill squash commits {first} through {last}:", fg='yellow')
            for i in range(first-1, last):
                commit = recent_commits[i]
                click.echo(f"  {commit['hash']} - {commit['message']}")
                
            return first, last
            
        except (KeyboardInterrupt, EOFError):
            click.secho("\nCancelled", fg='red')
            sys.exit(1)
    
    sys.exit(1)

def undo_last_squash():
    latest_backup = get_latest_backup()
    
    if not latest_backup:
        click.secho("No yags backup found. Nothing to undo.", fg='red')
        return False
    
    try:
        current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        
        click.secho(f"Found backup: {latest_backup}", fg='cyan')
        click.echo(f"This will reset your current branch '{current_branch}'")
        click.secho("WARNING. Any changes since the last squash will be lost", fg='red', bold=True)
        
        if not click.confirm("Continue with undo?", default=False):
            click.secho("Undo cancelled", fg='yellow')
            return False
        
        run_command(['git', 'reset', '--hard', latest_backup])
        
        click.secho(f"Successfully restored to backup: {latest_backup}", fg='green', bold=True)
        
        if click.confirm("Delete the backup branch?", default=True):
            run_command(['git', 'branch', '-D', latest_backup])
            click.secho("Backup branch deleted", fg='cyan')
            click.secho('Please remember to git add and push your changes after this to properly revert your changes')
        
        return True
        
    except subprocess.CalledProcessError as e:
        click.secho(f"Failed to undo: {e}", fg='red')
        return False

def cleanup_old_backups(keep_count=5):
    try:
        result = run_command(['git', 'branch', '--list', 'yags-backup-*'])
        if not result.strip():
            return
        
        branches = result.strip().split('\n')
        
        clean_branches = []
        for branch in branches:
            clean_name = branch.strip()
            if clean_name.startswith('* '):
                clean_name = clean_name[2:]
            clean_branches.append(clean_name)
        
        if len(clean_branches) <= keep_count:
            return
        
        branch_timestamps = []
        for branch in clean_branches:
            parts = branch.split('-')
            timestamp = int(parts[-1])
            branch_timestamps.append((timestamp, branch))
        
        branch_timestamps.sort(reverse=True)
        
        to_delete = []
        for i in range(keep_count, len(branch_timestamps)):
            to_delete.append(branch_timestamps[i][1])
        
        for branch in to_delete:
            run_command(['git', 'branch', '-D', branch])
            click.secho(f"Cleaned up old backup: {branch}")
            
    except:
        pass

def get_recent_commits(limit=100):
    result = run_command([
        'git', 'log', 
        f'--max-count={limit}',
        '--pretty=format:%h|%s|%an|%ar|%H',
        '--no-merges'
    ])
    
    commits = []
    for line in result.strip().split('\n'):
        if line:
            parts = line.split('|', 4)
            if len(parts) == 5:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author': parts[2],
                    'age': parts[3],
                    'full_hash': parts[4]
                })
    return commits

def show_commit_details(commit_hash):
    try:
        commit_info = run_command([
            'git', 'show', '--no-patch', '--pretty=format:%H%n%an <%ae>%n%ad%n%s%n%n%b', 
            commit_hash
        ])
        
        files_changed = run_command([
            'git', 'show', '--name-status', '--pretty=format:', commit_hash
        ]).strip()
        
        stats = run_command([
            'git', 'show', '--stat', '--pretty=format:', commit_hash
        ]).strip()
        
        click.secho(f"\n--- Commit Details: {commit_hash[:8]} ---", fg='cyan', bold=True)
        
        lines = commit_info.split('\n')
        if len(lines) >= 4:
            click.echo(f"Author: {lines[1]}")
            click.echo(f"Date: {lines[2]}")
            print(f"Subject: {lines[3]}")
            
            has_body = False
            if len(lines) > 5:
                for line in lines[5:]:
                    if line.strip():
                        has_body = True
                        break

            if has_body:
                click.echo(f"\nFull message:")
                for line in lines[5:]:
                    if line.strip():
                        click.echo(f" {line}")
        
        if files_changed:
            click.secho(f"\nFiles changed:", fg='yellow')
            for line in files_changed.split('\n'):
                if line.strip():
                    click.echo(f" {line}")
        
        if stats:
            click.secho(f"\nStats:", fg='green')
            for line in stats.split('\n'):
                if not line.strip():
                    continue
                if 'file' in line:
                    click.echo(f" {line}")
        
        click.echo("\nOptions:")
        click.echo("1) Show code changes (full diff)")
        click.echo("2) Show code changes (summary only)")
        click.echo("3) Skip diff")
        
        diff_choice = click.prompt("Choice", type=click.Choice(['1', '2', '3']), default='1', show_choices=False)
        
        if diff_choice == '1':
            click.secho(f"\n--- Code Changes (Full Diff) ---", fg='magenta', bold=True)
            try:
                run_command([
                    'git', 'show', '--color=always', '--pretty=format:', commit_hash
                ], capture=False)
            except subprocess.CalledProcessError:
                click.secho("Could not show diff", fg='red')
        elif diff_choice == '2':
            click.secho(f"\n--- Code Changes ---", fg='magenta', bold=True)
            try:
                run_command([
                    'git', 'show', '--stat', '--color=always', '--pretty=format:', commit_hash
                ], capture=False)
                click.echo()
                run_command([
                    'git', 'show', '--name-only', '--pretty=format:', commit_hash
                ], capture=False)
            except subprocess.CalledProcessError:
                click.secho("Could not show summary", fg='red')
                    
    except subprocess.CalledProcessError as e:
        click.secho(f"Could not get commit details: {e}", fg='red')

def show_commits(commits, start_idx=0, page_size=20):
    end_idx = min(start_idx + page_size, len(commits))
    
    click.secho(f"\nCommits {start_idx + 1}-{end_idx} of {len(commits)}:", fg='cyan', bold=True)
    click.echo()
    
    for i in range(start_idx, end_idx):
        commit = commits[i]
        msg = commit['message']
        if len(msg) > 50:
            msg = msg[:47] + "..."
            
        click.echo(f"{i+1:3d}) {commit['hash']} - {msg:<50} ({commit['age']})")
    
    click.echo()
    
    options = []
    if end_idx < len(commits):
        options.append("'n' for next page")
    if start_idx > 0:
        options.append("'p' for previous page")
    options.append("'i <num>' to inspect commit (see code diff)")
    options.append("'q' to continue")
    
    if options:
        click.secho("Options: " + ", ".join(options), fg='yellow')
    
    return end_idx < len(commits), start_idx > 0

def interactive_commit_browser(commits):
    start_idx = 0
    page_size = 20
    
    while True:
        has_next, has_prev = show_commits(commits, start_idx, page_size)
        
        try:
            cmd = click.prompt("Command", default="q").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'n' and has_next:
                start_idx += page_size
            elif cmd == 'p' and has_prev:
                start_idx = max(0, start_idx - page_size)
            elif cmd.startswith('i '):
                try:
                    commit_num = int(cmd.split()[1])
                    if 1 <= commit_num <= len(commits):
                        commit = commits[commit_num - 1]
                        show_commit_details(commit['full_hash'])
                        click.prompt("\nPress Enter to continue browsing", default="")
                    else:
                        click.secho(f"Invalid commit number! Use 1-{len(commits)}", fg='red')
                except (ValueError, IndexError):
                    click.secho("Usage: i <number> (e.g., 'i 5' to see commit #5 details + diff)", fg='red')
            else:
                click.secho("Unknown command. Use 'n', 'p', 'i <num>', or 'q'", fg='yellow')
                
        except (KeyboardInterrupt, EOFError):
            break

@click.command()
@click.option('-c', '--commits', type=int, help="Number of commits to squash")
@click.option('--dry-run', is_flag=True, help="Show what would happen")
@click.option('--limit', type=int, default=100, help="Max number of commits to show (default: 100)")
@click.option('--undo', is_flag=True, help="Undo last squash (restores from backup branch)")
def main(commits, dry_run, limit, undo):
    if undo:
        click.secho("--- Git Squash Undo ---", fg='magenta', bold=True)
        success = undo_last_squash()
        sys.exit(0 if success else 1)
    
    if dry_run:
        click.secho("--- Git Squash (Dry Run) ---", fg='yellow', bold=True)
    else:
        click.secho("--- Git Squash ---", fg='blue', bold=True)
    
    try:
        run_command(['git', 'rev-parse', '--is-inside-work-tree'], capture=False)
    except subprocess.CalledProcessError:
        click.secho("Not in a git repo!", fg='red', bold=True)
        sys.exit(1)

    base = ""
    rebase_todo = []
    commits_for_message = []
    
    choice = ""

    if commits:
        base = f'HEAD~{commits}'
        choice = '2'
    else:
        click.echo("\n1) Squash since main branch")
        click.echo("2) Squash the last N commits")
        click.echo("3) Browse and pick commits visually")
        choice = click.prompt("Pick", type=click.Choice(['1', '2', '3']), show_choices=False)

    if choice == '1':
        main_branch = get_main_branch_name()
        try:
            base = run_command(['git', 'merge-base', 'HEAD', main_branch])
            click.echo(f"Squashing since common ancestor with '{main_branch}' ({base[:7]})")
            commit_list = get_commits_since(base)
            if not commit_list:
                click.secho("Nothing to squash!", fg='yellow')
                sys.exit(0)
            
            for i, (sha, _, msg) in enumerate(commit_list):
                action = "pick" if i == 0 else "squash"
                rebase_todo.append(f"{action} {sha} {msg}")
            commits_for_message = [msg for sha, _, msg in commit_list]
        except subprocess.CalledProcessError as e:
            click.secho(f"Git error: {e.stderr.strip()}", fg='red')
            sys.exit(1)
            
    elif choice == '2':
        n = click.prompt("How many commits?", type=int)
        base = f'HEAD~{n}'
        commit_list = get_commits_since(base)
        if not commit_list:
            click.secho("Nothing to squash!", fg='yellow')
            sys.exit(0)

        for i, (sha, _, msg) in enumerate(commit_list):
            action = "pick" if i == 0 else "squash"
            rebase_todo.append(f"{action} {sha} {msg}")
        commits_for_message = [msg for sha, _, msg in commit_list]
        
    elif choice == '3':
        recent_commits = get_recent_commits(limit)
        if not recent_commits:
            click.secho("No commits found!", fg='red')
            sys.exit(1)
        
        click.secho(f"Found {len(recent_commits)} commits. Browse and inspect:", fg='green')
        interactive_commit_browser(recent_commits)
        
        first, last = get_commit_range_input(recent_commits)
        
        display_squash_preview(recent_commits, first, last)
        
        if not click.confirm(f"\nConfirm: Squash commits {first} through {last}?", default=True):
            click.secho("Cancelled", fg='yellow')
            sys.exit(0)

        if last < len(recent_commits):
            base = recent_commits[last]['full_hash']
        else:
            base = f"{recent_commits[last - 1]['full_hash']}^"

        commits_to_rebase = recent_commits[0:last]
        commits_to_rebase.reverse()
        
        for i, commit in enumerate(commits_to_rebase):
            original_index = last - i
            
            if first <= original_index <= last:
                if original_index == last:
                    action = "pick"
                else:
                    action = "squash"
            else:
                action = "pick"
            
            rebase_todo.append(f"{action} {commit['full_hash']} {commit['message']}")

        commits_for_message = [c['message'] for c in recent_commits[first - 1 : last]]

    click.secho(f"\nRebase Plan:" )
    for line in rebase_todo:
        if line.startswith('squash'):
            click.secho(f" {line}", fg='yellow')
        else:
            click.echo(f" {line}")

    if dry_run:
        click.secho("\n[DRY RUN] This will show the rebase actions that will be taken.", fg='yellow')
        click.secho("[DRY RUN] No changes will be made.", fg='yellow')
        sys.exit(0)

    if not click.confirm("\nContinue?", default=False):
        click.secho("Cancelled", fg='red')
        sys.exit(0)
    
    backup_branch = None
    if not dry_run:
        click.secho("Creating safety backup..." )
        backup_branch = create_backup_branch()
        if not backup_branch:
            click.secho("Failed to create backup. Aborting.", fg='red', bold=True)
            sys.exit(1)
        
        cleanup_old_backups()
    
        click.echo()
    click.secho("----------------------------------------", fg='cyan')
    click.secho("Create your squash commit message", fg='cyan', bold=True)
    click.secho("----------------------------------------", fg='cyan')
    
    click.echo("\nCombining these commits:")
    for i, msg in enumerate(commits_for_message, 1):
        click.echo(f"  * {msg}")
    
    if len(commits_for_message) == 1:
        default_message = commits_for_message[0]
    elif len(commits_for_message) <= 3:
        default_message = " + ".join(commits_for_message)
    else:
        common_words = []
        first_msg_words = set(commits_for_message[0].lower().split())
        for word in first_msg_words:
            if all(word in msg.lower() for msg in commits_for_message):
                common_words.append(word)
        
        if common_words:
            default_message = f"Multiple {' '.join(common_words)} updates"
        else:
            default_message = f"Squashed {len(commits_for_message)} commits"
    
    click.echo(f"\nDefault: {click.style(default_message, fg='yellow')}")
    click.echo("Type your message (or press Enter to use default):")
    
    commit_message = click.prompt("", default=default_message, show_default=False)
    
    click.echo()
    click.secho("Your commit message will be:", fg='green')
    click.secho(f"  {commit_message}", fg='green', bold=True)
    click.secho("----------------------------------------", fg='cyan')
    
    todo_script = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh')
    editor_script = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh')

    todo_script.write("#!/bin/sh\n")
    todo_script.write("cat > \"$1\" << 'EOF'\n")
    for line in rebase_todo:
        todo_script.write(f"{line}\n")
    todo_script.write("EOF\n")
    todo_script.close()
    os.chmod(todo_script.name, 0o755)

    editor_script.write("#!/bin/sh\n")
    editor_script.write("cat > \"$1\" << 'COMMITMSG_END'\n")
    editor_script.write(f"{commit_message}\n")
    editor_script.write("\n")
    editor_script.write("# Squashed commits:\n")
    for msg in commits_for_message:
        editor_script.write(f"# - {msg}\n")
    editor_script.write("COMMITMSG_END\n")
    editor_script.write("exit 0\n")
    editor_script.close()
    os.chmod(editor_script.name, 0o755)

    click.secho("Starting rebase..." )
    
    try:
        env = os.environ.copy()
        env['GIT_SEQUENCE_EDITOR'] = todo_script.name
        env['GIT_EDITOR'] = editor_script.name
        
        run_command(['git', 'rebase', '-i', base], env=env, capture=False)
        
        click.secho("Rebase successful", fg='green', bold=True)
        click.secho("If you need to undo this, run: yags --undo", fg='cyan')
        
        current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        push_command = f"git push --force-with-lease origin {current_branch}"
        click.secho(f"\nTo finish, run: {push_command}", fg='cyan')
        click.secho('If you run into ')

        if click.confirm("Push to remote now?", default=False):
            run_command(['git', 'push', '--force-with-lease', 'origin', current_branch], capture=False)
            click.secho("Done!", fg='green', bold=True)
            if backup_branch:
                click.secho("Backup kept in case you need to undo later", fg='cyan')
        
    except subprocess.CalledProcessError:
        click.secho(f"Rebase failed or was cancelled.", fg='yellow')
        click.echo("Run 'git rebase --abort' if needed.")
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg='red')
    finally:
        os.remove(todo_script.name)
        os.remove(editor_script.name)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        click.secho("\nCancelled by user.", fg='red')
        sys.exit(1)