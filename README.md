# Recommit

Recommit is a command-line tool that leverages Language Models to automatically regenerate clear, descriptive commit messages for your Git repositories. Say goodbye to writing commit messages manually!

## How does it work?

1. Navigate to your Git repository in the terminal
2. Run the `recommit` command
3. The tool will analyze your commit history and generate improved commit messages based on the actual code changes

## Iterative mode

Recommit includes an interactive mode that ensures safe Git history modifications:

1. Before making any changes, Recommit creates a temporary backup branch of your current state
2. Changes are previewed one commit at a time, allowing you to:
   - Accept the suggested message
   - Edit the suggestion
   - Skip the current commit
   - Keep the original message
3. You can abort the process at any time, which will restore your repository to its original state
4. The backup branch is maintained until you explicitly confirm the changes

This approach guarantees that your Git history remains intact and recoverable, even if:

- The process is interrupted (power failure, nuclear apocalypse, etc.)
- You change your mind about the modifications

> 💡 **Tip**: Use `recommit --interactive` or `recommit -i` to enable interactive mode
