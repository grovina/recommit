import os
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
    
    def update_commit_message(self, commit: Commit, new_message: str):
        """Update the message of a specific commit using git rebase."""
        # Get the commit hash for the parent of our target commit
        target = commit.hexsha
        
        # Create a git rebase todo script
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # For the first commit, we need to handle it differently
            if not commit.parents:
                # Just write the reword command for the first commit
                f.write(f'reword {target} {commit.message.splitlines()[0]}\n')
            else:
                # Write rebase commands: reword the target commit, pick all others
                parent = commit.parents[0].hexsha
                for c in self.repo.iter_commits(f'{parent}..HEAD', reverse=True):
                    action = 'reword' if c.hexsha == target else 'pick'
                    f.write(f'{action} {c.hexsha} {c.message.splitlines()[0]}\n')
            todo_file = f.name
            
        # Create a message file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(new_message)
            msg_file = f.name
            
        try:
            # Set up the environment to automate the rebase
            env = os.environ.copy()
            env['GIT_SEQUENCE_EDITOR'] = f'cat {todo_file} >'
            env['EDITOR'] = f'cat {msg_file} >'
            
            # Start the rebase
            base = '--root' if not commit.parents else f'{commit.parents[0].hexsha}^'
            self.repo.git.rebase(
                '-i', base,
                env=env
            )
            
        finally:
            # Clean up temporary files
            os.unlink(todo_file)
            os.unlink(msg_file)
    
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