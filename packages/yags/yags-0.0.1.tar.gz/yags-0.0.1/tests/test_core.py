import pytest
import subprocess
import os
from unittest.mock import patch, MagicMock
from yags.core import run_command, get_main_branch_name, get_commits_since, get_user_editor

class TestRunCommand:
    @patch('subprocess.run')
    def test_basic_command(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "test output\n"
        mock_run.return_value = mock_result
        
        result = run_command(['git', 'status'])
        assert result == "test output"

    @patch('subprocess.run')
    def test_no_capture(self, mock_run):
        result = run_command(['git', 'status'], capture=False)
        assert result == ""

    @patch('subprocess.run') 
    def test_git_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(SystemExit):
            run_command(['git', 'status'])

    @patch('subprocess.run')
    def test_command_fails(self, mock_run):
        error = subprocess.CalledProcessError(1, 'git')
        error.stderr = "fatal: not a git repository"
        mock_run.side_effect = error
        
        with pytest.raises(SystemExit):
            run_command(['git', 'status'])

class TestGetMainBranchName:
    @patch('yags.core.run_command')
    def test_has_main(self, mock_run):
        mock_run.return_value = ""
        result = get_main_branch_name()
        assert result == "main"

    @patch('yags.core.run_command')
    def test_falls_back_to_master(self, mock_run):
        ### main fails, master works
        mock_run.side_effect = [subprocess.CalledProcessError(1, 'git'), ""]
        result = get_main_branch_name()
        assert result == "master"

    @patch('yags.core.run_command')
    def test_no_main_branch_found(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        with pytest.raises(SystemExit):
            get_main_branch_name()

class TestGetCommitsSince:
    @patch('yags.core.run_command')
    def test_normal_commits(self, mock_run):
        mock_run.return_value = "abc123 fix bug\ndef456 add feature"
        
        result = get_commits_since('HEAD~3')
        
        assert len(result) == 2
        assert result[0] == ('abc123', 'fix bug')
        assert result[1] == ('def456', 'add feature')

    @patch('yags.core.run_command')
    def test_no_commits(self, mock_run):
        mock_run.return_value = ""
        result = get_commits_since('HEAD~3')
        assert result == []

    @patch('yags.core.run_command')
    def test_git_fails(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        result = get_commits_since('HEAD~3')
        assert result == []

    @patch('yags.core.run_command')
    def test_long_commit_messages(self, mock_run):
        mock_run.return_value = "abc123 fix the really annoying login bug that was bothering everyone"
        
        result = get_commits_since('HEAD~1')
        
        assert result[0][0] == 'abc123'
        assert 'annoying login bug' in result[0][1]

    @patch('yags.core.run_command')  
    def test_weird_git_output(self, mock_run):
        mock_run.return_value = "abc123\ndef456 add feature"
        
        result = get_commits_since('HEAD~2')
        
        # skip malformed line
        assert len(result) == 1
        assert result[0] == ('def456', 'add feature')

class TestGetUserEditor:
    @patch('yags.core.run_command')
    def test_git_editor(self, mock_run):
        mock_run.return_value = "nano"
        result = get_user_editor()
        assert result == "nano"

    @patch('yags.core.run_command')
    @patch.dict(os.environ, {'EDITOR': 'emacs'})
    def test_uses_editor_env(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        result = get_user_editor()
        assert result == "emacs"

    @patch('yags.core.run_command')
    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_to_vim(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        result = get_user_editor()
        assert result == "vim"

class TestRealWorldStuff:
    @patch('yags.core.run_command')
    def test_typical_squash_setup(self, mock_run):
        mock_run.side_effect = [
            "",
            "a1b2c3 wip\nd4e5f6 fix typo\ng7h8i9 add login feature",
            "code"
        ]
        
        branch = get_main_branch_name()
        commits = get_commits_since('HEAD~3')
        editor = get_user_editor()
        
        assert branch == "main"
        assert len(commits) == 3
        assert commits[-1][1] == "add login feature"  # last commit
        assert editor == "code"

    @patch('yags.core.run_command')
    def test_old_repo_with_master(self, mock_run):
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, 'git'),
            "",
            "commit1 old commit\ncommit2 another old commit"
        ]
        
        branch = get_main_branch_name()
        commits = get_commits_since('HEAD~2')
        
        assert branch == "master"
        assert len(commits) == 2

if __name__ == "__main__":
    pytest.main([__file__])