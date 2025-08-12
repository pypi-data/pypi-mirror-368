"""
Enhanced CLI for Metis Agent with Claude Code/Gemini CLI styling.

This module provides a modern command-line interface focused on:
1. Interactive natural language interface with streaming
2. Configuration management  
3. Authentication management
4. Visual enhancements and real-time feedback
"""
import os
import time
import threading
import click
from pathlib import Path
from ..core.agent_config import AgentConfig
from ..auth.api_key_manager import APIKeyManager
from ..core import SingleAgent
from .code_commands import code as code_command
from .knowledge_commands import knowledge_cli
from .todo_commands import todo_group

# Try to import Rich for enhanced visuals, fallback to basic if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.status import Status
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


@click.group()
def cli():
    """Metis Agent - Intelligent AI Assistant"""
    pass


# Add the code command to the CLI
cli.add_command(code_command)

# Add the todo command to the CLI
cli.add_command(todo_group)


@cli.command()
@click.argument("query", required=False)
@click.option("--session", "-s", help="Session ID for context")
def chat(query, session):
    """Start interactive chat or process a single query."""
    config = AgentConfig()
    
    # Initialize agent with config settings
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=True,
        config=config
    )
    
    if query:
        # Single query mode
        try:
            response = agent.process_query(query, session_id=session)
            if isinstance(response, dict):
                click.echo(response.get("response", str(response)))
            else:
                click.echo(response)
        except Exception as e:
            click.echo(f"Error: {e}")
        return
    
    # Interactive mode
    _start_interactive_mode(agent, config, session)


def _show_welcome_logo(config=None):
    """Display enhanced Metis Agent welcome with system status."""
    if RICH_AVAILABLE:
        console = Console()
        
        # Create enhanced logo with Rich
        logo_text = Text()
        logo_text.append("    ###   ### ", style="bold blue")
        logo_text.append("####### ", style="bold magenta")
        logo_text.append("######## ", style="bold cyan")
        logo_text.append("## ", style="bold white")
        logo_text.append("#######", style="bold magenta")
        logo_text.append("\n")
        logo_text.append("    #### #### ", style="bold blue")
        logo_text.append("##      ", style="bold magenta")
        logo_text.append("   ##    ", style="bold cyan")
        logo_text.append("## ", style="bold white")
        logo_text.append("##     ", style="bold magenta")
        logo_text.append("\n")
        logo_text.append("    ## ### ## ", style="bold blue")
        logo_text.append("#####   ", style="bold magenta")
        logo_text.append("   ##    ", style="bold cyan")
        logo_text.append("## ", style="bold white")
        logo_text.append("#######", style="bold magenta")
        logo_text.append("\n")
        logo_text.append("    ##  #  ## ", style="bold blue")
        logo_text.append("##      ", style="bold magenta")
        logo_text.append("   ##    ", style="bold cyan")
        logo_text.append("## ", style="bold white")
        logo_text.append("     ##", style="bold magenta")
        logo_text.append("\n")
        logo_text.append("    ##     ## ", style="bold blue")
        logo_text.append("####### ", style="bold magenta")
        logo_text.append("   ##    ", style="bold cyan")
        logo_text.append("## ", style="bold white")
        logo_text.append("#######", style="bold magenta")
        
        # Add version and description
        version_text = Text("\n                    AGENTS v0.6.0\n", style="bold cyan")
        desc_text = Text("              General Purpose AI Agent", style="white")
        
        # System status
        status_table = Table.grid()
        if config:
            provider = config.get_llm_provider()
            model = config.get_llm_model()
            status_table.add_row(f"[dim]Provider:[/dim] [green]{provider}[/green]")
            status_table.add_row(f"[dim]Model:[/dim] [green]{model}[/green]")
            
            # Check API key status
            from ..auth.api_key_manager import APIKeyManager
            key_manager = APIKeyManager()
            services = key_manager.list_services()
            if services:
                status_table.add_row(f"[dim]API Keys:[/dim] [green]{len(services)} configured[/green]")
            else:
                status_table.add_row(f"[dim]API Keys:[/dim] [yellow]None configured[/yellow]")
        
        # Create main panel
        main_content = Text()
        main_content.append(logo_text)
        main_content.append(version_text)
        main_content.append(desc_text)
        
        panel = Panel(main_content, border_style="bright_blue", padding=(0, 1))
        console.print(panel)
        
        if config:
            console.print(Panel(status_table, title="[bold]System Status[/bold]", border_style="dim", padding=(0, 1)))
        
    else:
        # Fallback to original ANSI colors
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        
        logo = f"""
{BLUE}{BOLD}    ###   ### {MAGENTA}####### {CYAN}######## {WHITE}## {MAGENTA}#######{RESET}
{BLUE}{BOLD}    #### #### {MAGENTA}##      {CYAN}   ##    {WHITE}## {MAGENTA}##     {RESET}
{BLUE}{BOLD}    ## ### ## {MAGENTA}#####   {CYAN}   ##    {WHITE}## {MAGENTA}#######{RESET}
{BLUE}{BOLD}    ##  #  ## {MAGENTA}##      {CYAN}   ##    {WHITE}## {MAGENTA}     ##{RESET}
{BLUE}{BOLD}    ##     ## {MAGENTA}####### {CYAN}   ##    {WHITE}## {MAGENTA}#######{RESET}

{CYAN}{BOLD}                    AGENTS v0.6.0{RESET}
{WHITE}              General Purpose AI Agent{RESET}
"""
        click.echo(logo)


def _start_interactive_mode(agent: SingleAgent, config: AgentConfig, session_id: str = None):
    """Start enhanced interactive chat mode with streaming."""
    current_dir = Path.cwd()
    current_session = session_id or "default_session"
    
    # Show enhanced welcome logo with config
    _show_welcome_logo(config)
    
    if RICH_AVAILABLE:
        console = Console()
        
        # Enhanced context panel
        context_table = Table.grid()
        context_table.add_row(f"[dim]Directory:[/dim] [cyan]{current_dir}[/cyan]")
        context_table.add_row(f"[dim]Session:[/dim] [cyan]{current_session}[/cyan]")
        
        # Show project context if available
        try:
            from ..tools.project_context import ProjectContextTool
            project_tool = ProjectContextTool()
            project_summary = project_tool.get_project_summary(".")
            
            if project_summary.get("success"):
                summary = project_summary["summary"]
                if summary.get("primary_language"):
                    project_info = f"{summary['project_name']} ({summary['primary_language']}"
                    if summary.get('framework'):
                        project_info += f", {summary['framework']}"
                    project_info += f", {summary['file_count']} files)"
                    context_table.add_row(f"[dim]Project:[/dim] [green]{project_info}[/green]")
        except Exception:
            pass  # Project context not available
        
        console.print(Panel(context_table, title="[bold]Context[/bold]", border_style="dim"))
        
        # Enhanced help panel
        help_table = Table.grid()
        help_table.add_row("[dim]Natural Language Examples:[/dim]")
        help_table.add_row("  [cyan]> Research recent developments in renewable energy[/cyan]")
        help_table.add_row("  [cyan]> Analyze this data and find trends[/cyan]")
        help_table.add_row("  [cyan]> Write a business plan for a coffee shop[/cyan]")
        help_table.add_row("  [cyan]> Help me understand quantum physics concepts[/cyan]")
        help_table.add_row("")
        help_table.add_row("[dim]Special Commands:[/dim]")
        help_table.add_row("  [yellow]exit[/yellow] or [yellow]quit[/yellow] - Exit chat")
        help_table.add_row("  [yellow]session <name>[/yellow] - Switch session")
        help_table.add_row("  [yellow]clear[/yellow] - Clear screen")
        help_table.add_row("  [yellow]help[/yellow] - Show this help")
        
        console.print(Panel(help_table, title="[bold]Getting Started[/bold]", border_style="green"))
        
    else:
        # Fallback for non-Rich environments
        click.echo(f"\nDirectory: {current_dir}")
        click.echo(f"Session: {current_session}")
        
        # Show project context if available
        try:
            from ..tools.project_context import ProjectContextTool
            project_tool = ProjectContextTool()
            project_summary = project_tool.get_project_summary(".")
            
            if project_summary.get("success"):
                summary = project_summary["summary"]
                if summary.get("primary_language"):
                    context_info = f"Project: {summary['project_name']} ({summary['primary_language']}"
                    if summary.get('framework'):
                        context_info += f", {summary['framework']}"
                    context_info += f", {summary['file_count']} files)"
                    click.echo(context_info)
        except Exception:
            pass  # Project context not available
        
        click.echo("\nJust type your request in natural language!")
        click.echo("Examples:")
        click.echo("  - 'Create a Python web app with FastAPI'")
        click.echo("  - 'Analyze the code in this project'")
        click.echo("  - 'Search for information about quantum computing'")
        click.echo("  - 'Help me debug this error'")
        click.echo("\nSpecial commands:")
        click.echo("  - 'exit' or 'quit' - Exit chat")
        click.echo("  - 'session <name>' - Switch session")
        click.echo("  - 'clear' - Clear screen")
        click.echo("  - 'help' - Show this help")
        click.echo("=" * 60)
    
    while True:
        try:
            user_input = input(f"\n[{current_session}] > ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                if RICH_AVAILABLE:
                    console = Console()
                    console.print("[dim]Goodbye![/dim]")
                else:
                    click.echo("Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            elif user_input.lower() == 'help':
                _show_help_panel()
                continue
            
            elif user_input.lower().startswith('session '):
                new_session = user_input[8:].strip()
                if new_session:
                    current_session = new_session
                    if RICH_AVAILABLE:
                        console = Console()
                        console.print(f"[green]Switched to session:[/green] [cyan]{current_session}[/cyan]")
                    else:
                        click.echo(f"Switched to session: {current_session}")
                continue
            
            # Process query with enhanced streaming
            try:
                _process_query_with_streaming(user_input, agent, current_session, config)
                    
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console = Console()
                    console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
                else:
                    click.echo("\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                if RICH_AVAILABLE:
                    console = Console()
                    console.print(f"\n[red]Error:[/red] {e}")
                    console.print("[dim]Try rephrasing your request or check your configuration.[/dim]")
                else:
                    click.echo(f"\nError: {e}")
                    click.echo("Try rephrasing your request or check your configuration.")
                
        except KeyboardInterrupt:
            click.echo("\nGoodbye!")
            break
        except EOFError:
            if RICH_AVAILABLE:
                console = Console()
                console.print("\n[dim]Goodbye![/dim]")
            else:
                click.echo("\nGoodbye!")
            break


def _process_query_with_streaming(user_input: str, agent, session_id: str, config: AgentConfig):
    """Process query with Claude Code-style streaming interface."""
    if RICH_AVAILABLE:
        console = Console()
        
        # Show thinking indicator with spinner
        with console.status("[bold cyan]Thinking...", spinner="dots") as status:
            response = agent.process_query(user_input, session_id=session_id)
        
        # Display agent name header
        agent_name = config.get_agent_name()
        console.print(f"\n[bold cyan]{agent_name}:[/bold cyan]")
        
        # Stream the response word by word
        if isinstance(response, dict):
            response_text = response.get("response", str(response))
        else:
            response_text = str(response)
        
        _stream_text_response(response_text, console)
        
    else:
        # Fallback for non-Rich environments
        click.echo("Thinking...")
        response = agent.process_query(user_input, session_id=session_id)
        
        agent_name = config.get_agent_name()
        click.echo(f"\n{agent_name}:")
        if isinstance(response, dict):
            click.echo(response.get("response", str(response)))
        else:
            click.echo(response)


def _stream_text_response(text: str, console):
    """Stream text response with enhanced formatting like Claude Code."""
    import re
    
    # Handle different content types in the response
    if not text.strip():
        return
    
    # Check for code blocks and format accordingly
    code_block_pattern = r'```(\w+)?\n?(.*?)```'
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)
    
    if code_blocks:
        # Split text around code blocks while preserving the delimiters
        parts = re.split(code_block_pattern, text)
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Regular text part
            if i % 3 == 0:
                if part.strip():
                    _stream_plain_text(part, console)
            # Language identifier (skip)
            elif i % 3 == 1:
                pass
            # Code content
            elif i % 3 == 2:
                language = parts[i-1] if parts[i-1] else "text"
                _display_code_block(part, language, console)
            
            i += 1
    else:
        # Handle plain text with potential lists, bullets, etc.
        _stream_plain_text(text, console)


def _stream_plain_text(text: str, console):
    """Stream plain text with proper paragraph formatting."""
    import re
    import time
    
    # Normalize line breaks and split into paragraphs
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split by double newlines for paragraphs, preserve single newlines within paragraphs
    paragraphs = re.split(r'\n\s*\n', text.strip())
    
    for para_idx, paragraph in enumerate(paragraphs):
        if not paragraph.strip():
            continue
            
        # Handle single line breaks within paragraphs
        lines = paragraph.split('\n')
        
        for line_idx, line in enumerate(lines):
            if not line.strip():
                console.print()  # Empty line
                continue
                
            # Stream words in this line
            words = line.strip().split()
            current_line = ""
            
            for word in words:
                console.print(word + " ", end="")
                current_line += word + " "
                time.sleep(0.03)  # Small delay for streaming effect
                
                # Handle line wrapping at reasonable points
                if len(current_line) > 90:
                    console.print()
                    current_line = ""
            
            # End the line if there's content
            if current_line.strip():
                console.print()
            
            # Add extra line break if this was a line break in original text
            if line_idx < len(lines) - 1:
                console.print()
        
        # Add paragraph break (except after the last paragraph)
        if para_idx < len(paragraphs) - 1:
            console.print()


def _display_code_block(code: str, language: str, console):
    """Display code block with enhanced syntax highlighting."""
    from rich.syntax import Syntax
    from rich.panel import Panel
    
    try:
        # Use improved theme and formatting like Metis Code
        syntax = Syntax(
            code.strip(), 
            language, 
            theme="github-dark", 
            line_numbers=True,
            background_color="default"
        )
        
        # Display in a panel for better visual separation
        code_panel = Panel(
            syntax, 
            title=f"[bold white]{language.title() if language else 'Code'}[/bold white]",
            border_style="bright_black",
            padding=(0, 1)
        )
        console.print()  # Add spacing before code block
        console.print(code_panel)
        console.print()  # Add spacing after code block
        
    except Exception:
        # Fallback if syntax highlighting fails
        console.print(f"\n[dim]```{language}[/dim]")
        console.print(code.strip())
        console.print("[dim]```[/dim]\n")


def _show_help_panel():
    """Display enhanced help panel."""
    if RICH_AVAILABLE:
        console = Console()
        
        # Capabilities table
        capabilities_table = Table.grid()
        capabilities_table.add_row("[bold]Metis Agent Capabilities:[/bold]")
        capabilities_table.add_row("")
        capabilities_table.add_row("[green]Code & Development:[/green]")
        capabilities_table.add_row("  • Code generation and analysis")
        capabilities_table.add_row("  • Project scaffolding and management") 
        capabilities_table.add_row("  • File operations and project exploration")
        capabilities_table.add_row("  • Git operations and version control")
        capabilities_table.add_row("")
        capabilities_table.add_row("[cyan]Research & Content:[/cyan]")
        capabilities_table.add_row("  • Web search and research")
        capabilities_table.add_row("  • Content creation and writing")
        capabilities_table.add_row("  • Data analysis and processing")
        capabilities_table.add_row("")
        capabilities_table.add_row("[yellow]Special Commands:[/yellow]")
        capabilities_table.add_row("  • [bold]exit/quit/bye[/bold] - Exit chat")
        capabilities_table.add_row("  • [bold]session <name>[/bold] - Switch session")
        capabilities_table.add_row("  • [bold]clear[/bold] - Clear screen")
        capabilities_table.add_row("  • [bold]help[/bold] - Show this help")
        
        console.print(Panel(capabilities_table, title="[bold]Help[/bold]", border_style="blue"))
        
    else:
        # Fallback for non-Rich environments
        click.echo("\nJust type your request in natural language!")
        click.echo("The agent will understand and help you with:")
        click.echo("  - Code generation and analysis")
        click.echo("  - Project scaffolding and management")
        click.echo("  - Web search and research")
        click.echo("  - Content creation and writing")
        click.echo("  - Git operations and version control")
        click.echo("  - File operations and project exploration")


@cli.group()
def config():
    """Manage agent configuration and settings."""
    pass


# Add knowledge commands to config group
config.add_command(knowledge_cli)


@config.command("show")
def show_config():
    """Show current configuration."""
    config = AgentConfig()
    config.show_config()
    
    # Show provider-specific status
    provider = config.get_llm_provider()
    
    if provider == "ollama":
        click.echo("\nOllama Status:")
        base_url = config.get_ollama_base_url()
        click.echo(f"  Base URL: {base_url}")
        
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=3)
            response.raise_for_status()
            models = response.json().get("models", [])
            click.echo(f"  Status: [OK] Connected ({len(models)} models available)")
        except Exception as e:
            click.echo(f"  Status: [NO] Not connected - {e}")
            click.echo("  Make sure Ollama is installed and running.")
    
    elif provider == "huggingface":
        click.echo("\nHuggingFace Configuration:")
        click.echo(f"  Device: {config.get_huggingface_device()}")
        click.echo(f"  Quantization: {config.get_huggingface_quantization()}")
        click.echo(f"  Max Length: {config.get_huggingface_max_length()}")
        
        # Check if transformers is installed
        try:
            import transformers
            import torch
            click.echo(f"  Transformers: [OK] Installed (v{transformers.__version__})")
            click.echo(f"  PyTorch: [OK] Installed (v{torch.__version__})")
            
            # Check device availability
            device = config.get_huggingface_device()
            if device == "auto" or device == "cuda":
                if torch.cuda.is_available():
                    click.echo(f"  CUDA: [OK] Available ({torch.cuda.device_count()} devices)")
                else:
                    click.echo(f"  CUDA: [NO] Not available")
            
            if device == "auto" or device == "mps":
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    click.echo(f"  MPS: [OK] Available")
                else:
                    click.echo(f"  MPS: [NO] Not available")
                    
        except ImportError:
            click.echo(f"  Status: [NO] Missing dependencies")
            click.echo("  Install with: pip install transformers torch")


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Set a configuration value."""
    config = AgentConfig()
    
    # Handle boolean values
    if value.lower() in ['true', 'false']:
        value = value.lower() == 'true'
    
    # Handle numeric values
    elif value.isdigit():
        value = int(value)
    
    # Handle null values
    elif value.lower() in ['null', 'none']:
        value = None
    
    config.set(key, value)
    click.echo(f"Set {key} = {value}")


@config.command("system-message")
@click.option("--file", "-f", help="Load system message from file")
@click.option("--interactive", "-i", is_flag=True, help="Enter system message interactively")
@click.option("--layer", "-l", type=click.Choice(['base', 'custom']), default='custom', help="Which system message layer to modify")
def set_system_message(file, interactive, layer):
    """Set system message for the agent (base or custom layer)."""
    config = AgentConfig()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                message = f.read().strip()
            if layer == 'base':
                config.agent_identity.update_base_system_message(message)
            else:
                config.agent_identity.update_custom_system_message(message)
            click.echo(f"System message ({layer} layer) loaded from {file}")
        except Exception as e:
            click.echo(f"Error loading file: {e}")
            return
    
    elif interactive:
        current_msg = config.agent_identity.base_system_message if layer == 'base' else config.agent_identity.custom_system_message
        click.echo(f"Enter your {layer} system message (press Ctrl+D when done):")
        click.echo("Current message:")
        click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        click.echo("\nNew message:")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            message = '\n'.join(lines).strip()
            if message:
                if layer == 'base':
                    config.agent_identity.update_base_system_message(message)
                else:
                    config.agent_identity.update_custom_system_message(message)
                click.echo(f"System message ({layer} layer) updated")
            else:
                click.echo("No message entered")
                
        except KeyboardInterrupt:
            click.echo("\nCancelled")
    
    else:
        click.echo("Current system message layers:")
        click.echo("\nBase layer:")
        base_msg = config.agent_identity.base_system_message
        click.echo(f"  {base_msg[:200]}..." if len(base_msg) > 200 else f"  {base_msg}")
        
        if config.agent_identity.custom_system_message:
            click.echo("\nCustom layer:")
            custom_msg = config.agent_identity.custom_system_message
            click.echo(f"  {custom_msg[:200]}..." if len(custom_msg) > 200 else f"  {custom_msg}")
        else:
            click.echo("\nCustom layer: (not set)")
        
        click.echo("\nUse --interactive or --file to change it")
        click.echo("Use --layer base to modify the base system message")


@config.command("reset")
def reset_config():
    """Reset configuration to defaults."""
    if click.confirm("Are you sure you want to reset all configuration to defaults?"):
        config = AgentConfig()
        config.config = config._get_default_config()
        config.save_config()
        click.echo("Configuration reset to defaults")


@config.command("identity")
def show_identity():
    """Show agent identity information."""
    config = AgentConfig()
    identity_info = config.agent_identity.get_identity_info()
    
    click.echo("Agent Identity:")
    click.echo("=" * 30)
    click.echo(f"Agent ID: {identity_info['agent_id']}")
    click.echo(f"Agent Name: {identity_info['agent_name']}")
    click.echo(f"Created: {identity_info['creation_timestamp']}")
    
    click.echo("\nSystem Message Preview:")
    full_msg = identity_info['full_system_message']
    preview = full_msg[:300] + "..." if len(full_msg) > 300 else full_msg
    click.echo(f"{preview}")


@config.command("set-name")
@click.argument("name")
def set_agent_name(name):
    """Set the agent's name."""
    config = AgentConfig()
    old_name = config.agent_identity.agent_name
    config.agent_identity.update_name(name)
    click.echo(f"Agent name changed from '{old_name}' to '{name}'")


@config.command("set-personality")
@click.option("--file", "-f", help="Load personality from file")
@click.option("--interactive", "-i", is_flag=True, help="Enter personality interactively")
def set_personality(file, interactive):
    """Set the agent's personality (custom system message)."""
    config = AgentConfig()
    
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                message = f.read().strip()
            config.agent_identity.update_custom_system_message(message)
            click.echo(f"Agent personality loaded from {file}")
        except Exception as e:
            click.echo(f"Error loading file: {e}")
            return
    
    elif interactive:
        current_msg = config.agent_identity.custom_system_message
        click.echo("Enter your agent's personality/role (press Ctrl+D when done):")
        click.echo("Current personality:")
        if current_msg:
            click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        else:
            click.echo("  (not set)")
        click.echo("\nNew personality:")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            message = '\n'.join(lines).strip()
            if message:
                config.agent_identity.update_custom_system_message(message)
                click.echo("Agent personality updated")
            else:
                click.echo("No personality entered")
                
        except KeyboardInterrupt:
            click.echo("\nCancelled")
    
    else:
        click.echo("Current agent personality:")
        current_msg = config.agent_identity.custom_system_message
        if current_msg:
            click.echo(f"  {current_msg[:200]}..." if len(current_msg) > 200 else f"  {current_msg}")
        else:
            click.echo("  (not set)")
        click.echo("\nUse --interactive or --file to change it")


@config.command("regenerate-identity")
def regenerate_identity():
    """Generate a new agent identity (ID and name)."""
    config = AgentConfig()
    old_id = config.agent_identity.agent_id
    old_name = config.agent_identity.agent_name
    
    if click.confirm(f"Are you sure you want to regenerate identity for {old_name} ({old_id})?"):
        config.agent_identity.regenerate_identity()
        click.echo(f"Identity regenerated:")
        click.echo(f"  Old: {old_name} ({old_id})")
        click.echo(f"  New: {config.agent_identity.agent_name} ({config.agent_identity.agent_id})")
        click.echo("Custom personality preserved.")
    else:
        click.echo("Identity regeneration cancelled.")


@cli.group()
def auth():
    """Manage API keys and authentication."""
    pass


@auth.command("set")
@click.argument("service")
@click.argument("key", required=False)
def set_key(service, key):
    """Set an API key for a service."""
    if not key:
        key = click.prompt(f"Enter API key for {service}", hide_input=True)
    
    key_manager = APIKeyManager()
    key_manager.set_key(service, key)
    click.echo(f"API key for {service} set successfully")


@auth.command("list")
def list_keys():
    """List configured API keys."""
    key_manager = APIKeyManager()
    services = key_manager.list_services()
    
    if not services:
        click.echo("No API keys configured")
        click.echo("\nSet API keys with: metis auth set <service> <key>")
        click.echo("Supported services: openai, groq, anthropic, huggingface, google")
        return
    
    click.echo("Configured API keys:")
    for service in services:
        click.echo(f"  {service}")


@auth.command("remove")
@click.argument("service")
def remove_key(service):
    """Remove an API key."""
    if click.confirm(f"Remove API key for {service}?"):
        key_manager = APIKeyManager()
        key_manager.remove_key(service)
        click.echo(f"API key for {service} removed")


@auth.command("test")
@click.argument("service", required=False)
def test_key(service):
    """Test API key connectivity."""
    key_manager = APIKeyManager()
    
    if service:
        services = [service]
    else:
        services = key_manager.list_services()
    
    if not services:
        click.echo("No API keys to test")
        return
    
    for svc in services:
        key = key_manager.get_key(svc)
        if key:
            click.echo(f"Testing {svc}...", nl=False)
            # TODO: Add actual API connectivity tests
            click.echo(" Key present")
        else:
            click.echo(f"{svc}: No key configured")





@config.command("ollama-url")
@click.argument("url")
def set_ollama_url(url):
    """Set Ollama server URL."""
    config = AgentConfig()
    config.set_ollama_base_url(url)
    click.echo(f"Ollama base URL set to: {url}")


@config.command("hf-device")
@click.argument("device")
def set_hf_device(device):
    """Set HuggingFace model device (auto, cpu, cuda, mps)."""
    config = AgentConfig()
    try:
        config.set_huggingface_device(device)
        click.echo(f"HuggingFace device set to: {device}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("hf-quantization")
@click.argument("quantization")
def set_hf_quantization(quantization):
    """Set HuggingFace model quantization (none, 8bit, 4bit)."""
    config = AgentConfig()
    try:
        config.set_huggingface_quantization(quantization)
        click.echo(f"HuggingFace quantization set to: {quantization}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("hf-max-length")
@click.argument("max_length", type=int)
def set_hf_max_length(max_length):
    """Set HuggingFace model max sequence length."""
    config = AgentConfig()
    try:
        config.set_huggingface_max_length(max_length)
        click.echo(f"HuggingFace max length set to: {max_length}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@config.command("list-models")
def list_models():
    """List available models for the current provider."""
    config = AgentConfig()
    provider = config.get_llm_provider()
    
    if provider == "ollama":
        _list_ollama_models(config)
    elif provider == "huggingface":
        _list_huggingface_models(config)
    else:
        click.echo(f"Model listing not supported for provider: {provider}")
        click.echo("Supported providers for model listing: ollama, huggingface")


def _list_ollama_models(config):
    """List available Ollama models."""
    base_url = config.get_ollama_base_url()
    
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        
        if models:
            click.echo("Available Ollama models:")
            for model in models:
                name = model.get("name", "Unknown")
                size = model.get("size", 0)
                size_gb = size / (1024**3) if size > 0 else 0
                click.echo(f"  - {name} ({size_gb:.1f}GB)")
        else:
            click.echo("No models found.")
            click.echo("Pull a model with: ollama pull <model-name>")
            
    except Exception as e:
        click.echo(f"Error connecting to Ollama: {e}")
        click.echo("Make sure Ollama is running and accessible.")


def _list_huggingface_models(config):
    """List information about HuggingFace model setup."""
    click.echo("Local HuggingFace Models:")
    click.echo("")
    click.echo("Popular models you can download:")
    click.echo("  Small models (< 1GB):")
    click.echo("    - microsoft/DialoGPT-small")
    click.echo("    - distilgpt2")
    click.echo("    - gpt2")
    click.echo("")
    click.echo("  Medium models (1-5GB):")
    click.echo("    - microsoft/DialoGPT-medium")
    click.echo("    - QuixiAI/TinyDolphin-2.8-1.1b")
    click.echo("    - TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    click.echo("")
    click.echo("  Large models (5GB+):")
    click.echo("    - microsoft/DialoGPT-large")
    click.echo("    - EleutherAI/gpt-neo-2.7B")
    click.echo("")
    click.echo("To use a model:")
    click.echo("  1. Set provider: metis config set llm_provider huggingface")
    click.echo("  2. Set model: metis config set llm_model <model-name>")
    click.echo("  3. The model will be downloaded automatically on first use")


if __name__ == "__main__":
    cli()
