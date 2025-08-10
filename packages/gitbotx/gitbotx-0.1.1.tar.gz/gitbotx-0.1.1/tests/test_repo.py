import pytest
from unittest.mock import patch
from gitbot.repo import parse_git_status, generate_commit_message, is_working_directory_clean

@patch('git_helper.repo.run_git_command')
def test_parse_git_status(mock_run_git):
    mock_run_git.return_value = " M file1.py\nM  file2.py\n?? newfile.txt\n"
    status = parse_git_status()
    assert status['staged'] == 1
    assert status['unstaged'] == 1
    assert status['untracked'] == 1

@patch('git_helper.repo.run_git_command')
def test_generate_commit_message(mock_run_git):
    mock_run_git.return_value = "file1.py\nREADME.md\n"
    msg = generate_commit_message()
    assert "Python" in msg and "documentation" in msg

@patch('git_helper.repo.run_git_command')
def test_is_working_directory_clean(mock_run_git):
    mock_run_git.return_value = ""
    assert is_working_directory_clean() is True
    mock_run_git.return_value = " M file1.py"
    assert is_working_directory_clean() is False
