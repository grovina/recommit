from typing import List

import click
from git import Commit


class InteractiveRewriter:
    def __init__(self, repo, generator):
        self.repo = repo
        self.generator = generator
        self.original_branch = None
        
    def start(self, recent: int = None):
        """Start the interactive rewriting process.
        
        Args:
            recent: If specified, limit to this many recent commits
        """
        # Store current branch and create backup
        self.original_branch = self.repo.get_current_branch()
        backup_branch = self.repo.create_backup_branch()
        click.echo(f"Created backup branch: {backup_branch}")
        
        try:
            # Get commits
            commits = self.repo.get_commits(count=recent)  # Pass None to get all commits
            self._process_commits(commits)
        finally:
            # Always return to original branch
            self.repo.checkout_branch(self.original_branch)
            click.echo(f"\nReturned to branch: {self.original_branch}")
        
    def _process_commits(self, commits: List[Commit]):
        """Process each commit interactively."""
        for commit in reversed(commits):  # Start with oldest commit
            click.echo("\n" + "="*50)
            click.echo(f"Commit: {click.style(commit.hexsha[:8], fg='yellow')}")
            click.echo(click.style("Original message:", fg='blue', bold=True))
            click.echo(click.style(commit.message.strip(), fg='blue'))
            click.echo(f"Date: {click.style(str(commit.authored_datetime), fg='cyan')}")
            
            # Get the diff for this commit
            diff = self.repo.get_commit_diff(commit)
            
            # Generate new message
            click.echo("\nGenerating improved message...")
            new_message = self.generator.generate_message(diff, commit.message)
            
            click.echo(click.style("\nProposed message:", fg='green', bold=True))
            click.echo(click.style(new_message, fg='green'))
            
            # Ask user what to do
            choice = click.prompt(
                "\nWhat would you like to do?",
                type=click.Choice(['accept', 'edit', 'skip', 'quit']),
                default='accept'
            )
            
            if choice == 'quit':
                break
            elif choice == 'skip':
                continue
            elif choice == 'edit':
                new_message = click.edit(new_message)
                if not new_message:
                    click.echo("No changes made, skipping...")
                    continue
            
            if choice in ['accept', 'edit']:
                self.repo.update_commit_message(commit, new_message)
                click.echo("Message updated!")