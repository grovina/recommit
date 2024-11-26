import os
import subprocess
import tempfile
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
        
    def get_commits(self, count: int = None):
        """Returns commits for processing.
        
        Args:
            count: If specified, limit to this many recent commits
        """
        if count is not None:
            return list(self.repo.iter_commits('HEAD', max_count=count))
        return list(self.repo.iter_commits('HEAD'))
        
    def get_commit_diff(self, commit: Commit) -> str:
        """Get the diff for a specific commit."""
        return self.repo.git.show(
            commit.hexsha,
            format='',  # Don't show commit message
            no_prefix=True
        )
    
    def update_commit_messages(self, commit_message_map: dict):
        """Update multiple commit messages using git-filter-repo."""
        # Ensure there are no unstaged changes
        if self.repo.is_dirty(untracked_files=True):
            raise ValueError("Cannot rewrite history with unstaged changes. Please commit or stash them first.")
        
        # Create a Python-compatible mapping string with proper escaping
        mapping_items = []
        for sha, message in commit_message_map.items():
            # Escape any quotes in the message
            escaped_message = message.replace('"', '\\"')
            mapping_items.append(f'    "{sha}": "{escaped_message}"')
        
        mapping_str = ',\n'.join(mapping_items)
        
        commit_callback = f"""
commit_mapping = {{
{mapping_str}
}}

try:
    commit_id = commit.original_id.decode('utf-8')
except AttributeError:
    commit_id = commit.original_id

if commit_id in commit_mapping:
    commit.message = commit_mapping[commit_id].encode('utf-8')
"""
        
        try:
            subprocess.run(
                [
                    'git', 'filter-repo',
                    '--force',
                    '--commit-callback', commit_callback
                ],
                check=True,
                cwd=self.repo.working_tree_dir
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"git-filter-repo failed: {e}")
        
    def get_staged_diff(self) -> str:
        """Get the diff of staged changes."""
        return self.repo.git.diff('--cached')
    
    def create_commit(self, message: str):
        """Create a new commit with the staged changes."""
        self.repo.index.commit(message)
    
    def get_current_branch(self) -> str:
        """Returns the name of the current branch."""
        return self.repo.active_branch.name
    
    def checkout_branch(self, branch_name: str):
        """Checkout the specified branch."""
        self.repo.git.checkout(branch_name)
    
    def update_branch(self, branch_name: str, commit_sha: str):
        """Update a branch to point to a specific commit."""
        self.repo.git.branch('-f', branch_name, commit_sha)
    
    def force_update_branch(self, branch_name: str):
        """Force update a branch to point to the current HEAD."""
        current_sha = self.repo.head.commit.hexsha
        self.repo.git.branch('-f', branch_name, current_sha)