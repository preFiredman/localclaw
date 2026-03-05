"""Main entry point for LocalClaw"""
import sys
import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from localclaw.config import Config
from localclaw.agent import Agent


def print_banner(console: Console):
    """Print welcome banner"""
    banner = """
🦞 LocalClaw - Your local AI assistant
   100% private. 100% local.
    """
    console.print(Panel(banner, title="Welcome", border_style="blue"))


def run_cli():
    """Run CLI mode"""
    parser = argparse.ArgumentParser(description="LocalClaw - Local AI Assistant")
    parser.add_argument("--config", "-c", help="Path to config file")
    parser.add_argument("--message", "-m", help="Single message mode")
    parser.add_argument("--tui", "-t", action="store_true", help="Launch TUI mode")
    args = parser.parse_args()
    
    # Launch TUI if requested
    if args.tui:
        from localclaw.tui import run_tui
        run_tui()
        return
    
    console = Console()
    
    # Load configuration
    try:
        config = Config(args.config)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)
    
    # Create workspace if needed
    workspace = Path(config.workspace_path)
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Initialize agent
    try:
        agent = Agent(config)
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
        sys.exit(1)
    
    print_banner(console)
    
    # Single message mode
    if args.message:
        console.print(f"[green]You:[/green] {args.message}")
        console.print("[blue]LocalClaw:[/blue] ", end="")
        for chunk in agent.chat(args.message):
            console.print(chunk, end="")
        console.print()
        return
    
    # Interactive mode
    console.print("[dim]Type 'exit' to quit, 'clear' to clear history[/dim]")
    console.print()
    
    while True:
        try:
            user_input = Prompt.ask("[green]You[/green]")
            
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye! 👋[/dim]")
                break
            
            if user_input.lower() == "clear":
                agent.clear_history()
                console.print("[dim]Conversation history cleared.[/dim]")
                continue
            
            if not user_input.strip():
                continue
            
            # Chat with agent
            console.print("[blue]LocalClaw:[/blue] ", end="")
            response_text = ""
            for chunk in agent.chat(user_input):
                console.print(chunk, end="")
                response_text += chunk
            console.print()
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'exit' to quit.[/dim]")
        except EOFError:
            break


def main():
    """Main entry point"""
    run_cli()


if __name__ == "__main__":
    main()
