import os
import time

from git import Commit, Repo
from git.exc import InvalidGitRepositoryError


class GitRepo:
    def __init__(self):
        try:
            self.repo = Repo(os.getcwd(), search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise ValueError("Not a git repository")
            
    def create_backup_branch(self) -> str:
        """Creates a backup branch with current state."""
        backup_name = f"recommit-backup-{int(time.time())}"
        new_branch = self.repo.create_head(backup_name)
        new_branch.checkout()
        return backup_name
        
    def get_commits(self, count: int = 10):
        """Returns recent commits for processing."""
        return list(self.repo.iter_commits('HEAD', max_count=count))
        
    def get_commit_diff(self, commit: Commit) -> str:
        """Get the diff for a specific commit."""
        return self.repo.git.show(
            commit.hexsha,
            format='',  # Don't show commit message
            no_prefix=True
        )
    
    def update_commit_message(self, commit: Commit, new_message: str):
        """Update the message of a specific commit."""
        # Using git filter-branch to rewrite the commit message
        self.repo.git.filter_branch(
            f'--msg-filter \'if [ "$GIT_COMMIT" = "{commit.hexsha}" ]; then echo "{new_message}"; else cat; fi\'',
            commit.hexsha + '^..HEAD',
            force=True
        )