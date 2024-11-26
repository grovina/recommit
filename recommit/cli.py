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
@click.option('--count', '-n', default=10, help='Number of commits to process')
def rewrite(api_key: str, count: int):
    """Interactively rewrite recent commit messages."""
    if not api_key:
        raise click.ClickException(
            "OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key"
        )
    
    try:
        repo = GitRepo()
        generator = MessageGenerator(api_key)
        rewriter = InteractiveRewriter(repo, generator)
        rewriter.start(count)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
    except Exception as e:
        raise click.ClickException(str(e))

def main():
    cli()