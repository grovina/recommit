import click
from dotenv import load_dotenv

from . import __version__
from .git_utils import GitRepo
from .interactive import InteractiveRewriter
from .message_generator import MessageGenerator


@click.group()
@click.version_option(__version__)
def cli():
    """🤖 AI-powered Git commit message regenerator."""
    load_dotenv()

@cli.command()
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
def commit(api_key: str):
    """Generate and commit a message for staged changes."""
    if not api_key:
        raise click.ClickException(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key"
        )
    
    try:
        repo = GitRepo()
        generator = MessageGenerator(api_key)
        
        # Get staged changes diff
        diff = repo.get_staged_diff()
        if not diff:
            raise click.ClickException("No staged changes found")
            
        # Generate message
        click.echo("Generating commit message...")
        message = generator.generate_message(diff, "")
        
        # Show and confirm
        click.echo(f"\nProposed message:\n{message}")
        if click.confirm("Create commit with this message?", default=True):
            repo.create_commit(message)
            click.echo("Commit created!")
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--recent', type=int, help='Limit to N most recent commits')
def rewrite(api_key: str, recent: int):
    """Interactively rewrite commit messages.
    
    If --recent N is specified, only process the N most recent commits.
    Otherwise, process all commits in the current branch.
    """
    if not api_key:
        raise click.ClickException(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key"
        )
    
    try:
        repo = GitRepo()
        generator = MessageGenerator(api_key)
        rewriter = InteractiveRewriter(repo, generator)
        rewriter.start(recent)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
    except Exception as e:
        raise click.ClickException(str(e))

def main():
    cli()