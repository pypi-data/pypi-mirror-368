#!/usr/bin/env python3
"""
This module contains Git functions.

The functions are ordered as followed:
- Git functions in Nornir stdout style
"""

import sys
import git
from nornir_collection.utils import print_task_title, print_task_name, task_info, task_error


#### Git Functions ###########################################################################################


def git_init(repo_path: str) -> tuple:
    """
    Initialize a git repo by its path specified with the repo_path argument. Returns a tuple with a GitPython
    repo object and a GitPython repo_cmd object.
    """
    print_task_name(text="Initialize Git repo")

    try:
        # Initialize the GitPython repo object
        repo = git.Repo(repo_path, search_parent_directories=True)

        # git.cmd.Git() raise no exception if no Git repo is found. If git_Repo() before was successful, also
        # git.cmd.Git() will be successful. Initialize the GitPython CMD object
        repo_cmd = git.cmd.Git(repo_path)

        print(task_info(text="Initialize local Git repo", changed=False))
        print(f"Local Git repo: {repo.working_tree_dir}")
        print(f"GitHub origin: {repo.remotes.origin.url}")

        return (repo, repo_cmd)

    except git.exc.NoSuchPathError as error:
        # If no Git repo exists terminate the script
        print(task_error(text="Initialize local Git repo", changed=False))
        print(f"Git repo not found: {error}")
        print("\n")
        sys.exit(1)


def git_is_dirty(repo: git.Repo) -> None:
    """
    Takes a GitPython repo object as argument and check if the git repo has any untracked or modified files.
    Prints the results in Nornir style and returns nothing (default None).
    """
    print_task_name(text="Check for local Git repo changes")

    # Query the active branch whether the repository data has been modified.
    if repo.is_dirty():
        print(task_info(text="Check for local Git repo changes", changed=True))
        print("Local Git repo is dirty")

        # Query the active branch and create a list of untracked files
        task_text = "Check for untracked files in local Git repo"
        untracked_files = repo.untracked_files

        if untracked_files:
            print(task_info(text=task_text, changed=True))
            print("Untracked files in local Git repo:")
            for file in untracked_files:
                print(f"-> {file}")
        else:
            print(task_info(text=task_text, changed=False))
            print("No untracked files in local Git repo")

        # Check differences between current files and last commit
        task_text = "Check for modified files in local Git repo"
        diff_to_last_commit = repo.git.diff(repo.head.commit.tree)

        if diff_to_last_commit:
            print(task_info(text=task_text, changed=True))
            print("Modified files in local Git repo:")

            # Print only the modified files from the output of git status
            for line in repo.git.status().splitlines():
                line = line.lstrip()
                if line.startswith("modified:"):
                    line = line.replace("modified:", "").lstrip()
                    print(f"-> {line}")
        else:
            print(task_info(text=task_text, changed=False))
            print("No modified files in local Git repo")

    else:
        print(task_info(text="Check for local Git repo changes", changed=False))
        print("Local Git repo is clean")


def git_cmd_pull(repo_cmd) -> None:
    """
    Takes a GitPython repo_cmd object as argument and executes a git pull to merge the local git repo with the
    origin repo. Prints the results in Nornir style and returns nothing (default None).
    """
    task_text = "Git pull from GitHub origin/main"
    print_task_name(text=task_text)

    try:
        # Execute a git pull to merge the GitHub origin/main into local main
        git_pull_result = repo_cmd.pull()

        # If the local repo is already up do date -> changed=False
        if git_pull_result.startswith("Already"):
            print(task_info(text=task_text, changed=False))
        else:
            print(task_info(text=task_text, changed=True))

        # Print the git pull result
        print(git_pull_result)

    except git.exc.GitCommandError as error:
        print(task_error(text=task_text, changed=False))
        print(f"Command '{error._cmdline}' failed\n")
        print(error.stdout.lstrip())
        print(error.stderr.lstrip())
        print("\n")
        sys.exit(1)


def git_cmd_add_commit(repo_cmd, commit_msg: str) -> None:
    """
    Takes a GitPython repo_cmd object and a commit_msg string as argument and executed a git add followed by a
    git commit to update the changes made in the local repo. Prints the results in Nornir style and returns
    nothing (default None).
    """
    print_task_name(text="Git commit changed to local repo")

    # Execute git add to stage all changes files
    repo_cmd.execute(["git", "add", "."])
    task_text = "Add Git working directory to staging area"
    print(task_info(text=task_text, changed=False))
    print("Git add working directory to staging area")

    task_text = "Git commit staging area to local repo"
    try:
        # Execute a git commit to commit the staging area to the local repo
        commit_cmd = repo_cmd.execute(["git", "commit", f"-m '{commit_msg}'", "--no-verify"])
        print(task_info(text=task_text, changed=False))
        print(commit_cmd)

    except git.exc.GitCommandError as error:
        print(task_info(text=task_text, changed=False))
        message = error.stdout.replace("stdout:", "").lstrip()
        message = message.replace("'", "").lstrip()
        print(message)

        # If the exception is another error than "Your branch is up to date ..." -> Terminate the script
        if "up to date" not in message:
            print("\n")
            sys.exit(1)


def git_push(repo) -> None:
    """
    Takes a GitPython repo object as argument and executed a git push to update the origin repo with the
    changes made in the local repo. Prints the results in Nornir style and returns nothing (default None).
    """
    print_task_name(text="Git push local repo to origin GitHub")

    task_text = "Git push local repo to origin GitHub"
    print(task_info(text=task_text, changed=False))

    push = repo.remote("origin").push()

    # push is a git.remote.PushInfo object with type git.util.InterableList
    for info in push:
        if "[up to date]" in info.summary:
            print("Everything up-to-date")

        else:
            new_commit = str(info.summary)[9:].rstrip()
            print(f"[main {new_commit}] To {repo.remotes.origin.url}")
            print(f" {info.summary.rstrip()} main -> main")


def git_pull_from_origin(repo_path: str) -> None:
    """
    Takes a string with a git directory path as argument and initializes two GitPython objects. Then checks
    for any changes in the local repo and executes a git pull to merge the local repo with the origin repo.
    Prints the results in Nornir style and returns nothing (default None).
    """
    print_task_title("Update local Git repo")

    # Initialize the GitPython repo and repo_cmd object. The repo_path is a string specifing the git directory
    repo_init = git_init(repo_path=repo_path)

    # git_init returns a tuple with a repo object [0] and a repo_cmd object [1]
    repo, repo_cmd = repo_init

    # Check for local git changes and print info to stdout
    git_is_dirty(repo=repo)

    # Execute a git pull to merge the GitHub origin/main into local main
    git_cmd_pull(repo_cmd=repo_cmd)


def git_commit_push_to_origin(repo_path: str, commit_msg: str) -> None:
    """
    Takes a string with a git directory path and a string with a commit message as argument and initializes
    two GitPython objects. Then checks for any changes in the local repo and executes a git add and a git
    commit followed by a git push to commit the local repo changes and update the origin repo with the changes
    made in the local repo. Prints the results in Nornir style and returns nothing (default None).
    """
    print_task_title("Update remote GitHub repo")

    # Initialize the GitPython repo and repo_cmd object
    repo_init = git_init(repo_path=repo_path)

    # git_init returns a tuple with a repo object [0] and a repo_cmd object [1]
    repo, repo_cmd = repo_init

    # Check for local git changes and print info to stdout
    git_is_dirty(repo=repo)

    # Execute git add to stage all changes files and commit them
    git_cmd_add_commit(repo_cmd=repo_cmd, commit_msg=commit_msg)

    # Execute git push to update the origin
    git_push(repo=repo)
