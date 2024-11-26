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
        # Ensure working directory is clean
        if self.repo.repo.is_dirty(untracked_files=True):
            raise click.ClickException("Cannot rewrite history with unstaged changes. Please commit or stash them first.")
        
        # Store current branch and create backup
        self.original_branch = self.repo.get_current_branch()
        backup_branch = self.repo.create_backup_branch()
        click.echo(f"Created backup branch: {backup_branch}")
        
        commit_message_map = {}
        try:
            # Get commits
            commits = self.repo.get_commits(count=recent)
            click.echo(f"\nProcessing {len(commits)} commits...")
            self._process_commits(commits, commit_message_map)
            
            if commit_message_map:
                # Perform the rewrite with all collected commit message changes
                self.repo.update_commit_messages(commit_message_map)
                click.echo("All selected commit messages have been updated.")
            
            # After successful processing, force update the original branch to our new history
            self.repo.force_update_branch(self.original_branch)
            success = True
            
        except Exception as e:
            click.echo(f"An error occurred: {e}")
            success = False
        finally:
            # Always return to original branch
            self.repo.checkout_branch(self.original_branch)
            
            # Only offer to delete backup if successful
            if success and commit_message_map and click.confirm("Delete backup branch?", default=True):
                self.repo.repo.delete_head(backup_branch, force=True)
            elif not success:
                click.echo(f"Changes were not applied. Your original state is preserved in '{self.original_branch}'")
                click.echo(f"The backup branch '{backup_branch}' contains the attempted changes")
        
    def _process_commits(self, commits: List[Commit], commit_message_map: dict):
        """Process each commit interactively and collect new messages."""
        total_commits = len(commits)
        
        for idx, commit in enumerate(reversed(commits)):  # Start with oldest commit
            current_num = idx + 1
            click.echo("\n" + "="*80)  # Wider separator for better visibility
            
            # Header section with progress
            click.echo(f"Processing commit {click.style(f'{current_num}/{total_commits}', fg='bright_blue')}: {click.style(commit.hexsha[:8], fg='yellow')}")
            click.echo(f"Date: {click.style(str(commit.authored_datetime), fg='cyan')}")
            
            # Original message section
            click.echo("\n" + click.style("📝 ORIGINAL COMMIT MESSAGE:", fg='blue', bold=True))
            click.echo("─" * 40)  # Subsection separator
            click.echo(click.style(commit.message.strip(), fg='blue'))
            
            # Get the diff and generate new message
            diff = self.repo.get_commit_diff(commit)
            click.echo("\nGenerating improved message...")
            new_message = self.generator.generate_message(diff, commit.message)
            
            # Proposed message section
            click.echo("\n" + click.style("✨ PROPOSED NEW MESSAGE:", fg='green', bold=True))
            click.echo("─" * 40)  # Subsection separator
            click.echo(click.style(new_message, fg='green'))
            
            # Action prompt
            click.echo("\n" + click.style("📋 ACTION REQUIRED:", fg='yellow', bold=True))
            choice = click.prompt(
                "Choose what to do",
                type=click.Choice(['accept', 'edit', 'skip', 'quit']),
                default='accept'
            )
            
            if choice == 'quit':
                break
            elif choice == 'skip':
                continue
            elif choice == 'edit':
                edited_message = click.edit(new_message)
                if edited_message:
                    new_message = edited_message.strip()
                else:
                    click.echo("No changes made, skipping...")
                    continue
            
            if choice in ['accept', 'edit']:
                commit_message_map[commit.hexsha] = new_message
                click.echo("Message queued for update!")