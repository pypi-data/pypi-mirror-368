import click
import json
import os
from typing import Optional
from datetime import datetime

from .git_diff import GitDiffAnalyzer
from .llm_client import CommitMessageGenerator
from .config import Config
from .storage import MessageStorage
from . import __version__


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, version):
    """GitMe - Git commit message generator
    
    Generate intelligent git commit messages by analyzing your code changes.
    
    Commands:
        gitme [OPTIONS]         Generate commit message
        gitme show [OPTIONS]    Show previous commit messages
        gitme -v                Show version information
    
    Generate Examples:
        gitme              # Generate message for staged changes
        gitme -a           # Generate message for all changes  
        gitme -c           # Generate message and commit all changes     
        gitme -p openai    # Use OpenAI instead of default Anthropic
        gitme -p openai -m gpt-4o-mini  # Use OpenAI's GPT-4o-mini model
        gitme -u <branch>  # Stealth mode: Generate, commit and push to upstream branch
        
    Show Examples:
        gitme show         # Show last 10 messages with provider info
        gitme show -n 5    # Show last 5 messages
        gitme show -r      # Show from all repositories  
        gitme show --clear # Clear message history
    
    Environment:
        ANTHROPIC_API_KEY must be set for Claude API access
        OPENAI_API_KEY must be set for OpenAI API access
    """
    if version:
        click.echo(f"gitme version {__version__}")
        ctx.exit()
    
    if ctx.invoked_subcommand is None:
        # If no subcommand, show help
        click.echo(ctx.get_help())
        ctx.exit()


@cli.command()
@click.option('--staged', '-s', is_flag=True, help='Analyze only staged changes')
@click.option('--all', '-a', is_flag=True, help='Analyze all changes (staged and unstaged)')
@click.option('--model', '-m', default='claude-3-5-haiku-latest', help='Model to use (Claude or OpenAI)')
@click.option('--provider', '-p', type=click.Choice(['anthropic', 'openai']), default='anthropic', help='LLM provider to use (default: anthropic)')
@click.option('--commit', '-c', is_flag=True, help='Create commit with generated message')
@click.option('--upstream', '-u', help='Create commit and push to upstream branch (specify branch name)')
def generate(staged: bool, all: bool, model: str, provider: str, commit: bool, upstream: Optional[str]):
    """Generate a commit message for current changes
    
    By default analyzes staged changes only. Use -a for all changes.
    Use -c to automatically commit after generating the message.
    Use -u <branch> to commit and push to upstream branch with confirmations.
    You can combine -c and -u flags together.
    """
    
    analyzer = GitDiffAnalyzer()
    
    if not analyzer.git_available:
        click.echo(click.style("𐩃 Error: Git is not installed on your system", fg="red", bold=True), err=True)
        click.echo(click.style("💡 Please install git to use this tool", fg="yellow"), err=True)
        return
    
    if not analyzer.in_git_repo:
        click.echo(click.style("𐩃 Error: Not in a git repository", fg="red", bold=True), err=True)
        click.echo(click.style("💡 Please run 'git init' to initialize a git repository", fg="yellow"), err=True)
        return
    
    # Determine which changes to analyze
    if staged and all:
        click.echo(click.style("𐩃 Error: Cannot use both --staged and --all options together", fg="red", bold=True), err=True)
        return
    
    # Default behavior: staged changes only
    use_staged = True
    
    if all or commit or upstream:
        # For --all, --commit, or --upstream, analyze all changes
        use_staged = False
    elif staged:
        # Explicitly requested staged only
        use_staged = True
    
    # Check for untracked files first
    untracked_files = analyzer.get_untracked_files()
    
    if untracked_files:
        click.echo(click.style("📁 Untracked files found:", fg="yellow", bold=True))
        for file in untracked_files:
            click.echo(f"    {file}")
        
        if click.confirm("Do you want to add these untracked files to the staging area?"):
            import subprocess
            try:
                subprocess.run(["git", "add"] + untracked_files, check=True)
                click.echo(click.style("✓ Untracked files added to staging area", fg="green"))
            except subprocess.CalledProcessError as e:
                click.echo(click.style(f"⚠️ Failed to add untracked files: {e}", fg="red"), err=True)
    
    # Get file changes
    file_changes = analyzer.get_file_changes(staged_only=use_staged)
    
    if not file_changes:
        click.echo(click.style("⚠️  No changes detected to analyze", fg="yellow"))
        return
    
    # Generate commit message
    try:
        if provider == 'openai':
            # Set default OpenAI model if Claude model was specified
            model = 'gpt-4o-mini'
            commit_message = CommitMessageGenerator.generate_commit_message_openai(
                file_changes=file_changes,
                model=model
            )
        else:
            # Use Anthropic (default)
            generator = CommitMessageGenerator()
            generator.model = model
            commit_message = generator.generate_commit_message(file_changes)
        
        # Save the generated message
        storage = MessageStorage()
        repo_path = os.getcwd()
        storage.save_message(commit_message, repo_path, file_changes, provider, model)
        
        click.echo()
        click.echo(click.style("🎉 Generated commit message:", fg="green", bold=True))
        click.echo(click.style(commit_message, fg="cyan"))
        
        if commit or upstream:
            # Ask for confirmation before committing
            if click.confirm("Do you want to create a commit with this message?"):
                import subprocess
                try:
                    subprocess.run(["git", "commit", "-a", "-m", commit_message], check=True)
                    click.echo(click.style("✓ Commit created successfully!", fg="green", bold=True))
                    
                    # If upstream flag is used, also ask about pushing
                    if upstream:
                        if click.confirm(f"Do you want to push to upstream branch '{upstream}'?"):
                            try:
                                subprocess.run(["git", "push", "-u", "origin", upstream], check=True)
                                click.echo(click.style(f"✓ Successfully pushed to upstream branch '{upstream}'!", fg="green", bold=True))
                            except subprocess.CalledProcessError as e:
                                click.echo(click.style(f"𐩃 Failed to push to upstream: {e}", fg="red"), err=True)
                                click.echo(click.style("💡 You may need to set up the upstream branch first", fg="yellow"), err=True)
                        
                except subprocess.CalledProcessError as e:
                    click.echo(click.style(f"𐩃 Failed to create commit: {e}", fg="red"), err=True)
    
    except ValueError as e:
        click.echo(click.style(f"𐩃 Error: {e}", fg="red", bold=True), err=True)
        if provider == 'openai':
            click.echo(click.style("💡 Please set OPENAI_API_KEY environment variable", fg="yellow"), err=True)
        else:
            click.echo(click.style("💡 Please set ANTHROPIC_API_KEY environment variable", fg="yellow"), err=True)
    except Exception as e:
        click.echo(click.style(f"𐩃 Error: {e}", fg="red", bold=True), err=True)


@cli.command()
@click.option('--limit', '-n', default=10, help='Number of messages to show (default: 10)')
@click.option('--all-repos', '-r', is_flag=True, help='Show messages from all repositories')
@click.option('--clear', is_flag=True, help='Clear message history')
def show(limit: int, all_repos: bool, clear: bool):
    """Show previously generated commit messages
    
    Displays message history for the current repository by default.
    Use -r to show messages from all repositories.
    Use --clear to remove message history.
    """
    storage = MessageStorage()
    repo_path = os.getcwd() if not all_repos else None
    
    if clear:
        if click.confirm(f"Are you sure you want to clear {'all' if all_repos else 'this repository'} message history?"):
            storage.clear_messages(repo_path)
            click.echo(click.style("🗑️  Message history cleared.", fg="green"))
        return
    
    messages = storage.get_messages(repo_path, limit)
    
    if not messages:
        click.echo(click.style("📭 No previously generated messages found.", fg="yellow"))
        return
    
    for i, entry in enumerate(reversed(messages), 1):
        timestamp = datetime.fromisoformat(entry['timestamp'])
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        click.echo(f"\n{click.style(f'[{i}]', fg='cyan', bold=True)} {click.style(formatted_time, fg='green')}")
        if all_repos:
            click.echo(f"    {click.style('📁 Repository:', fg='magenta')} {entry['repo_path']}")
        click.echo(f"    {click.style('💬 Message:', fg='blue', bold=True)}")
        # Display multi-line messages with proper indentation
        for line in entry['message'].split('\n'):
            click.echo(f"    {line}")
        
        # Show provider and model information
        provider = entry.get('provider', 'unknown')
        model = entry.get('model', 'unknown')
        if provider or model:
            provider_display = provider.title() if provider != 'unknown' else 'Unknown'
            model_display = model if model and model != 'unknown' else 'Unknown'
            click.echo(f"    {click.style('🤖 AI Provider:', fg='magenta')} {provider_display} ({model_display})")
        
        # Show file changes summary
        file_changes = entry.get('file_changes', {})
        if file_changes:
            files_count = len(file_changes)
            click.echo(f"    {click.style('📝 Files changed:', fg='yellow')} {files_count}")


def main():
    """Entry point that provides backward compatibility"""
    import sys
    
    # If help flag or version flag, show the main help/version
    if '--help' in sys.argv or '-h' in sys.argv or '--version' in sys.argv or '-v' in sys.argv:
        # Remove the argument so Click handles it properly
        cli()
    # If no arguments, default to generate command 
    elif len(sys.argv) == 1:
        sys.argv.append('generate')
        cli()
    # If the first argument is a known subcommand, use the group
    elif len(sys.argv) > 1 and sys.argv[1] in ['generate', 'show']:
        cli()
    # Otherwise, assume it's the old-style command and prepend 'generate'
    else:
        sys.argv.insert(1, 'generate')
        cli()


if __name__ == "__main__":
    main()