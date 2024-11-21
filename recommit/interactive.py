from typing import List

import click
from git import Commit


class InteractiveRewriter:
    def __init__(self, repo, generator):
        self.repo = repo
        self.generator = generator
        
    def start(self):
        """Start the interactive rewriting process."""
        # Create backup first
        backup_branch = self.repo.create_backup_branch()
        click.echo(f"Created backup branch: {backup_branch}")
        
        # Get recent commits
        commits = self.repo.get_commits(count=10)
        self._process_commits(commits)
        
    def _process_commits(self, commits: List[Commit]):
        """Process each commit interactively."""
        for commit in reversed(commits):  # Start with oldest commit
            click.echo("\n" + "="*50)
            click.echo(f"Commit: {commit.hexsha[:8]}")
            click.echo(f"Original message:\n{commit.message.strip()}")
            click.echo(f"Date: {commit.authored_datetime}")
            
            # Get the diff for this commit
            diff = self.repo.get_commit_diff(commit)
            
            # Generate new message
            click.echo("\nGenerating improved message...")
            new_message = self.generator.generate_message(diff, commit.message)
            
            click.echo(f"\nProposed message:\n{new_message}")
            
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