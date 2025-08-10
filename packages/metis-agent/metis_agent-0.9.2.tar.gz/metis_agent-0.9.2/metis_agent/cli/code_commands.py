"""
Natural Language CLI commands for code intelligence features.

This module provides a unified natural language interface that routes all coding tasks
through the SingleAgent instead of using multiple subcommands.
"""
import click
import glob
import os
import re
import subprocess
import random
import string
from pathlib import Path
from datetime import datetime

# Try to import Rich for enhanced visuals, fallback to basic if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
from ..core.agent import SingleAgent
from ..core.smart_orchestrator import SmartOrchestrator
from ..core.agent_config import AgentConfig
from ..tools.core_tools.write_tool import WriteTool
from ..tools.core_tools.project_management_tool import ProjectManagementTool
from ..tools.core_tools.read_tool import ReadTool
from ..tools.core_tools.grep_tool import GrepTool
from ..tools.core_tools.filemanagertool import FileManagerTool
from ..tools.core_tools.bash_tool import BashTool
from ..tools.advanced_tools.e2b_code_sandbox import E2BCodeSandboxTool
from .streaming_interface import GeminiStreamingInterface


def generate_project_name(user_request):
    """
    Generate a simple, unique project name in format: metis-project-XXXXX
    
    Args:
        user_request (str): The user's project request (not used in simple format)
        
    Returns:
        str: A unique project name in format: metis-project-XXXXX
    """
    # Generate unique 5-digit ID using timestamp + random
    timestamp_part = datetime.now().strftime('%m%d')  # MMDD format
    random_part = ''.join(random.choices(string.digits, k=1))  # 1 random digit
    unique_id = f"{timestamp_part}{random_part}"
    
    # Simple consistent naming format
    project_name = f"metis-project-{unique_id}"
    
    return project_name

def _detect_existing_project(current_dir: str) -> dict:
    """
    Detect if current directory is already a Metis project or contains project files.
    
    Args:
        current_dir (str): Current working directory
        
    Returns:
        dict: Project detection info with keys: is_project, project_type, should_continue
    """
    # Debug info for troubleshooting
    debug_info = []
    
    try:
        # Check for common project indicators
        project_indicators = {
            'package.json': 'npm/node project',
            'requirements.txt': 'python project', 
            'pyproject.toml': 'python project',
            'Cargo.toml': 'rust project',
            'pom.xml': 'java project',
            'go.mod': 'go project',
            'composer.json': 'php project',
            'Gemfile': 'ruby project',
            'yarn.lock': 'yarn project',
            'poetry.lock': 'poetry project',
            'pipfile': 'pipenv project',
            'dockerfile': 'docker project',
            'makefile': 'makefile project'
        }
        
        # Check for git repository
        is_git_repo = False
        try:
            is_git_repo = os.path.isdir(os.path.join(current_dir, '.git'))
            if is_git_repo:
                debug_info.append("Found .git directory")
        except (OSError, PermissionError):
            debug_info.append("Cannot check for .git directory (permission issue)")
        
        # Check for existing project files
        existing_files = []
        detected_type = None
        
        try:
            for indicator_file, proj_type in project_indicators.items():
                file_path = os.path.join(current_dir, indicator_file)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    existing_files.append(indicator_file)
                    if not detected_type:
                        detected_type = proj_type
                    debug_info.append(f"Found project file: {indicator_file}")
        except (OSError, PermissionError):
            debug_info.append("Cannot check project files (permission issue)")
        
        # Check for common source directories
        common_dirs = ['src', 'lib', 'app', 'components', 'pages', 'views', 'controllers', 'tests', 'test']
        has_src_structure = False
        try:
            for d in common_dirs:
                if os.path.isdir(os.path.join(current_dir, d)):
                    has_src_structure = True
                    debug_info.append(f"Found source directory: {d}")
                    break
        except (OSError, PermissionError):
            debug_info.append("Cannot check source directories (permission issue)")
        
        # Check for code files in the directory (Python, JavaScript, etc.)
        code_files = []
        has_code_files = False
        try:
            files_in_dir = os.listdir(current_dir)
            code_extensions = ('.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt')
            
            for file in files_in_dir:
                file_path = os.path.join(current_dir, file)
                if os.path.isfile(file_path) and file.lower().endswith(code_extensions):
                    code_files.append(file)
            
            has_code_files = len(code_files) > 0
            if has_code_files:
                debug_info.append(f"Found {len(code_files)} code files: {', '.join(code_files[:3])}{'...' if len(code_files) > 3 else ''}")
                
        except (OSError, PermissionError) as e:
            debug_info.append(f"Cannot list files in directory: {str(e)}")
        
        # Check for metis project naming pattern in current directory name
        dir_name = os.path.basename(current_dir)
        is_metis_project = dir_name.startswith('metis-') or 'metis' in dir_name.lower()
        if is_metis_project:
            debug_info.append(f"Directory name suggests Metis project: {dir_name}")
        
        # Determine project status
        is_project = bool(existing_files) or has_src_structure or is_git_repo or has_code_files
        should_continue = is_project  # Continue in any existing project
        
        # Log debug info for troubleshooting (only if environment variable is set)
        if os.environ.get('METIS_DEBUG_PROJECT_DETECTION'):
            print(f"[DEBUG] Project detection for {current_dir}:")
            for info in debug_info:
                print(f"[DEBUG]   - {info}")
            print(f"[DEBUG] Result: is_project={is_project}, should_continue={should_continue}")
        
        return {
            'is_project': is_project,
            'is_metis_project': is_metis_project,
            'project_type': detected_type or ('code project' if has_code_files else None),
            'existing_files': existing_files,
            'code_files': code_files,
            'has_git': is_git_repo,
            'has_src_structure': has_src_structure,
            'has_code_files': has_code_files,
            'should_continue': should_continue,
            'directory_name': dir_name,
            'debug_info': debug_info
        }
        
    except Exception as e:
        # Fallback: if detection fails completely, don't assume it's a project
        debug_info.append(f"Project detection failed: {str(e)}")
        return {
            'is_project': False,
            'is_metis_project': False,
            'project_type': None,
            'existing_files': [],
            'code_files': [],
            'has_git': False,
            'has_src_structure': False,
            'has_code_files': False,
            'should_continue': False,
            'directory_name': os.path.basename(current_dir),
            'debug_info': debug_info,
            'error': str(e)
        }


def _get_project_location(project_name: str, auto: bool = False) -> str:
    """Get project location with user confirmation and project detection."""
    current_dir = os.getcwd()
    
    try:
        project_info = _detect_existing_project(current_dir)
    except Exception as e:
        # If project detection completely fails, create a fallback response
        click.echo(click.style(f"[WARNING] Project detection failed: {str(e)}", fg="red"))
        project_info = {
            'should_continue': False,
            'is_project': False,
            'project_type': None,
            'error': str(e)
        }
    
    # Debug output for troubleshooting
    if os.environ.get('METIS_DEBUG_PROJECT_DETECTION'):
        click.echo(click.style(f"[DEBUG] should_continue = {project_info.get('should_continue', False)}", fg="blue"))
    
    # If we're in an existing project, work in current directory
    if project_info.get('should_continue', False):
        if auto:
            return current_dir
        
        # Show project continuation info
        try:
            if RICH_AVAILABLE:
                console = Console()
                project_table = Table.grid(padding=1)
                project_table.add_column(style="dim", min_width=15)
                project_table.add_column()
                
                project_table.add_row("Current Dir:", Text(current_dir, style="bold cyan"))
                project_table.add_row("Project Type:", Text(project_info['project_type'] or 'detected project', style="green"))
                
                if project_info['existing_files']:
                    project_table.add_row("Project Files:", Text(', '.join(project_info['existing_files']), style="dim"))
                
                if project_info['code_files']:
                    code_files_display = ', '.join(project_info['code_files'][:5])  # Show first 5 code files
                    if len(project_info['code_files']) > 5:
                        code_files_display += f" (+{len(project_info['code_files']) - 5} more)"
                    project_table.add_row("Code Files:", Text(code_files_display, style="dim"))
                
                if project_info['has_git']:
                    project_table.add_row("Git Repo:", Text("Yes", style="green"))
                
                panel = Panel(
                    project_table,
                    title="[bold yellow]Existing Project Detected[/bold yellow]",
                    title_align="left",
                    border_style="yellow",
                    padding=(0, 1)
                )
                console.print(panel)
            else:
                # Fallback display without Rich
                click.echo(click.style(f"\n[EXISTING PROJECT DETECTED]", fg="yellow", bold=True))
                click.echo(click.style(f"Current Directory: {current_dir}", fg="white"))
                click.echo(click.style(f"Project Type: {project_info['project_type'] or 'detected project'}", fg="green"))
                
                if project_info['existing_files']:
                    click.echo(click.style(f"Project Files: {', '.join(project_info['existing_files'])}", fg="white", dim=True))
                
                if project_info['code_files']:
                    code_files_display = ', '.join(project_info['code_files'][:5])
                    if len(project_info['code_files']) > 5:
                        code_files_display += f" (+{len(project_info['code_files']) - 5} more)"
                    click.echo(click.style(f"Code Files: {code_files_display}", fg="white", dim=True))
                
                if project_info['has_git']:
                    click.echo(click.style(f"Git Repository: Yes", fg="green"))
                
                # Add debug info if available
                if os.environ.get('METIS_DEBUG_PROJECT_DETECTION') and project_info.get('debug_info'):
                    click.echo(click.style("\nDebug Info:", fg="blue"))
                    for info in project_info['debug_info']:
                        click.echo(click.style(f"  - {info}", fg="blue", dim=True))
                
        except Exception as e:
            # Ultimate fallback - just show basic info
            click.echo(click.style(f"\n[PROJECT DETECTED] Working in: {current_dir}", fg="yellow"))
            click.echo(click.style(f"Note: Display error occurred: {str(e)}", fg="red", dim=True))
        
        while True:
            choice = click.prompt(
                click.style("Continue working in this existing project?", fg="yellow") + " " +
                click.style("(y)es", fg="green") + " / " +
                click.style("(n)ew project in subdirectory", fg="blue"),
                type=str,
                default="y"
            ).lower().strip()
            
            if choice in ['y', 'yes', '']:
                return current_dir
            elif choice in ['n', 'new', 'no']:
                break
            else:
                click.echo(click.style("Please enter 'y' to continue or 'n' for new project", fg="red"))
    
    # Create new project in subdirectory
    default_location = os.path.join(current_dir, project_name)
    
    if auto:
        # In auto mode, create new project directory
        return default_location
    
    # Show proposed location with Rich panel
    if RICH_AVAILABLE:
        console = Console()
        
        # Create project info table
        project_table = Table.grid(padding=1)
        project_table.add_column(style="dim", min_width=15)
        project_table.add_column()
        
        rel_path = os.path.relpath(default_location, current_dir) if default_location != current_dir else f"./{project_name}"
        project_table.add_row("Project Name:", Text(project_name, style="bold cyan"))
        project_table.add_row("Relative Path:", Text(rel_path, style="green"))
        project_table.add_row("Full Path:", Text(default_location, style="dim"))
        project_table.add_row("Current Dir:", Text(current_dir, style="dim"))
        
        panel = Panel(
            project_table,
            title="[bold]Project Setup[/bold]",
            title_align="left",
            border_style="bright_blue",
            padding=(0, 1)
        )
        
        console.print(panel)
    else:
        # Fallback for non-Rich environments
        click.echo(click.style(f"\n[PROJECT SETUP] {project_name}", fg="cyan", bold=True))
        click.echo(click.style("─" * 50, fg="cyan", dim=True))
        
        rel_path = os.path.relpath(default_location, current_dir) if default_location != current_dir else f"./{project_name}"
        click.echo(click.style(f"Proposed location: {rel_path}", fg="white"))
        click.echo(click.style(f"Full path: {default_location}", fg="white", dim=True))
    
    while True:
        try:
            choice = click.prompt(
                click.style("Create project here?", fg="yellow") + " " +
                click.style("(y)es", fg="green") + " / " +
                click.style("(n)o, choose location", fg="blue") + " / " +
                click.style("(c)ancel", fg="red"),
                type=str,
                show_default=False
            ).lower().strip()
            
            if choice in ['y', 'yes']:
                return default_location
            elif choice in ['n', 'no']:
                # Let user choose custom location
                custom_path = click.prompt(
                    click.style("Enter project directory", fg="blue"),
                    type=str,
                    default=current_dir
                )
                if not os.path.isabs(custom_path):
                    custom_path = os.path.join(current_dir, custom_path)
                
                full_project_path = os.path.join(custom_path, project_name)
                click.echo(click.style(f"Project will be created at: {full_project_path}", fg="cyan"))
                return full_project_path
            elif choice in ['c', 'cancel']:
                click.echo(click.style("Project creation cancelled.", fg="red"))
                raise click.Abort()
            else:
                click.echo(click.style("Please choose: y/n/c", fg="red", dim=True))
                
        except (KeyboardInterrupt, EOFError):
            click.echo(click.style("\nProject creation cancelled.", fg="red"))
            raise click.Abort()


@click.command()
@click.argument('request', nargs=-1, required=False)
@click.option('--session', '-s', help='Session ID for context')
@click.option('--branch', '-b', type=str, help='Create specific named feature branch')
@click.option('--no-branch', is_flag=True, help='Skip automatic branch creation')
@click.option('--auto', '-a', is_flag=True, help='Auto mode - skip prompts and execute directly')
def code(request, session, branch, no_branch, auto):
    """Natural language coding assistant - handles all coding tasks through conversation.
    
    Examples:
      metis code "analyze this project and tell me about its structure"
      metis code "create a calculator class with add and subtract methods"
      metis code "fix the syntax errors in main.py"
      metis code "generate tests for the User class"
      metis code "refactor this function to be more readable"
      metis code "show me the dependencies in this project"
      metis code "create documentation for the API endpoints"
      
    Auto Mode Examples:
      metis code --auto "edit main.py and add a circle area function"
      metis code -a "create a new file utils.py with helper functions"
      metis code --auto "refactor the calculate method in calculator.py"
    """
    # Initialize streaming interface with tools first
    tools_registry = {
        'WriteTool': WriteTool(),
        'ProjectManagementTool': ProjectManagementTool(),
        'ReadTool': ReadTool(),
        'GrepTool': GrepTool(),
        'FileManagerTool': FileManagerTool(),
        'BashTool': BashTool(),
        'E2BCodeSandboxTool': E2BCodeSandboxTool()
    }
    
    # Convert tools registry to list for agent
    tools_list = list(tools_registry.values())
    
    # Initialize agent with config settings and tools for streaming
    config = AgentConfig()
    agent = SingleAgent(
        use_titans_memory=config.is_titans_memory_enabled(),
        llm_provider=config.get_llm_provider(),
        llm_model=config.get_llm_model(),
        enhanced_processing=False,  # Use direct processing for streaming
        config=config,
        tools=tools_list  # Pass tools to agent
    )
    
    # Handle natural language request with streaming
    if request:
        request_text = ' '.join(request)
        return _handle_natural_language_request(agent, request_text, session, branch, no_branch, auto)
    else:
        # No request provided - start interactive streaming session
        return _start_interactive_streaming_session(agent, session, branch, no_branch, auto)


def _handle_natural_language_request(agent, request_text, session=None, branch=None, no_branch=False, auto=False):
    """Process a single natural language coding request."""
    if auto:
        click.echo(click.style(f"[AUTO MODE] {request_text}", fg="yellow", bold=True))
        click.echo(click.style("[AUTO] Executing directly without prompts...", fg="yellow"))
    else:
        click.echo(click.style(f"[PROCESSING] {request_text}", fg="cyan", bold=True))
    click.echo("=" * 50)
    
    try:
        # Handle branch creation if this looks like a code generation task
        if _should_create_branch(request_text) and not no_branch:
            branch_created = _create_feature_branch(branch, auto_branch=(branch is None), description=request_text)
            if not branch_created:
                if auto or click.confirm("Continue without creating a branch?"):
                    pass  # Continue in auto mode or if user confirms
                else:
                    return
        
        # Get project context for the agent
        project_context = _get_project_context()
        
        # All requests now use streaming interface - no separate workflow
        
        # Create enhanced prompt with context for regular requests
        if auto:
            enhanced_prompt = f"""EXECUTE THIS TASK IMMEDIATELY IN AUTO MODE:

USER REQUEST: "{request_text}"

PROJECT CONTEXT:
{project_context}

CRITICAL: You MUST actually execute the tools to complete this task. Do not just analyze or plan - EXECUTE NOW.

For file operations:
1. Identify the correct tool (EditTool for editing existing files, WriteTool for creating new files)
2. Extract the file path from the user request
3. Determine the operation type (create, edit, append, etc.)
4. Execute the tool with proper structured parameters
5. Show the results of the actual file modification

Do NOT just describe what should be done - DO IT NOW.

EXECUTE THE TOOLS NOW - DO NOT JUST ANALYZE."""
        else:
            enhanced_prompt = f"""I'm working on a coding task. Here's my request:

USER REQUEST: "{request_text}"

PROJECT CONTEXT:
{project_context}

Please help me with this request. You have access to various tools including:
- ReadTool: for reading and analyzing existing files in the project
- GrepTool: for searching through files and finding specific patterns or code
- FileManagerTool: for listing directories, managing file operations, and project structure analysis
- WriteTool: for creating new files and writing code
- ProjectManagementTool: for creating projects, managing sessions, project lifecycle
- BashTool: for executing shell commands and system operations (with user confirmation)
- E2BCodeSandboxTool: for secure Python code execution in isolated cloud sandboxes (with user confirmation)
- And many other specialized tools for different tasks

IMPORTANT: When asked about existing code or files, ALWAYS use the file analysis tools first:
1. Use ReadTool to examine specific files: ReadTool.execute(task="read file", file_path="/path/to/file")
2. Use GrepTool to search for patterns: GrepTool.execute(task="search files", pattern="function_name", file_types=[".py"])
3. Use FileManagerTool to explore project structure: FileManagerTool.execute(task="list directory", path="/project/path")

Analyze my request and determine what needs to be done. Use the appropriate tools based on the task:
- To understand existing code: FIRST use ReadTool, GrepTool, or FileManagerTool to examine the files
- To analyze project structure: use FileManagerTool to list directories and ReadTool for key files
- Create/manage projects: use ProjectManagementTool
- Write new files: use WriteTool
- Search for specific code patterns: use GrepTool
- Execute shell commands: use BashTool (will ask user for confirmation)
- Run Python code securely: use E2BCodeSandboxTool (will ask user for confirmation)
- Multiple operations: break it down step by step

Be conversational and explain what you're doing. Show me the results and ask if you need clarification."""

        # Generate unique project directory in current directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = ''.join(c for c in request_text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_').lower()
        project_name = f"{safe_name}_{timestamp}"
        
        # Get project location with user confirmation
        project_location = _get_project_location(project_name, auto)
        
        # Create streaming interface
        streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry)
        
        # Enable auto-write mode if --auto flag is used
        if auto:
            streaming_interface.session_write_preference = 'all'
        
        # Stream response and write code blocks in real-time (like Gemini Code)
        streaming_interface.start_session()
        list(streaming_interface.stream_response(enhanced_prompt, session_id=session))
        
        click.echo(click.style("\n[COMPLETE] Task completed!", fg="green", bold=True))
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] {str(e)}", fg="red"))


def _start_interactive_streaming_session(agent, session=None, branch=None, no_branch=False, auto=False):
    """Start an interactive streaming session like Gemini."""
    
    # Generate session project location
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"interactive_session_{timestamp}"
    project_location = _get_project_location(project_name, auto)
    
    # Initialize streaming interface with tools - use same registry as main function
    tools_registry = {
        'WriteTool': WriteTool(),
        'ProjectManagementTool': ProjectManagementTool(),
        'ReadTool': ReadTool(),
        'GrepTool': GrepTool(),
        'FileManagerTool': FileManagerTool(),
        'BashTool': BashTool(),
        'E2BCodeSandboxTool': E2BCodeSandboxTool()
    }
    
    streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry)
    
    # Enable auto-write mode if --auto flag is used
    if auto:
        streaming_interface.session_write_preference = 'all'
    
    # Start interactive session
    streaming_interface.interactive_session()


def _start_interactive_coding_session(agent, session=None, branch=None, no_branch=False, auto=False):
    """Start an interactive coding session with the agent."""
    click.echo(click.style("[INTERACTIVE CODING SESSION]", fg="magenta", bold=True))
    click.echo("=" * 50)
    
    # Show project status
    _show_project_status()
    
    click.echo("\nI'm your coding assistant. You can ask me to:")
    click.echo("• Analyze code or project structure")  
    click.echo("• Generate new code or modify existing code")
    click.echo("• Debug issues or explain code")
    click.echo("• Create documentation or tests")
    click.echo("• Refactor or optimize code")
    click.echo("• Manage files and directories")
    click.echo("• And much more...")
    click.echo("\nType 'help' for more examples, 'quit' to exit")
    click.echo("=" * 50)
    
    current_session = session or f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            user_input = click.prompt(
                click.style("\n[You]", fg="green", bold=True),
                type=str, 
                show_default=False
            ).strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                click.echo(click.style("[GOODBYE] Happy coding!", fg="cyan"))
                break
                
            elif user_input.lower() == 'help':
                _show_help_examples()
                continue
                
            elif user_input.lower() in ['status', 'project']:
                _show_project_status()
                continue
            
            # Process the request through streaming interface
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = ''.join(c for c in user_input[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            project_name = f"{safe_name}_{timestamp}"
            
            project_location = _get_project_location(project_name, auto)
            
            # Initialize streaming interface with tools - use same registry as main function
            tools_registry = {
                'WriteTool': WriteTool(),
                'ProjectManagementTool': ProjectManagementTool(),
                'ReadTool': ReadTool(),
                'GrepTool': GrepTool(),
                'FileManagerTool': FileManagerTool(),
                'BashTool': BashTool(),
                'E2BCodeSandboxTool': E2BCodeSandboxTool()
            }
            
            streaming_interface = GeminiStreamingInterface(agent, project_location, tools_registry)
            
            # Stream the response
            list(streaming_interface.stream_response(user_input, session_id=current_session))
            
        except KeyboardInterrupt:
            click.echo(click.style("\n[GOODBYE] Session interrupted. Happy coding!", fg="cyan"))
            break
        except EOFError:
            click.echo(click.style("\n[GOODBYE] Session ended. Happy coding!", fg="cyan"))
            break


def _get_project_context():
    """Get current project context for the agent."""
    current_dir = Path.cwd()
    
    context_parts = [f"Working Directory: {current_dir}"]
    
    # Get file listing using standard Python
    try:
        files = [f.name for f in current_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
        dirs = [d.name for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if files:
            context_parts.append(f"Files in current directory: {', '.join(files[:10])}")
            if len(files) > 10:
                context_parts.append(f"... and {len(files) - 10} more files")
                
        if dirs:
            context_parts.append(f"Subdirectories: {', '.join(dirs[:5])}")
    except:
        context_parts.append("Unable to read directory contents")
    
    # Check for common project files
    project_indicators = []
    common_files = ["requirements.txt", "package.json", "setup.py", "pyproject.toml", "Dockerfile", "README.md"]
    for file in common_files:
        if Path(file).exists():
            project_indicators.append(file)
    
    if project_indicators:
        context_parts.append(f"Project files detected: {', '.join(project_indicators)}")
    
    # Check git status
    try:
        result = subprocess.run(["git", "branch", "--show-current"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            context_parts.append(f"Git branch: {result.stdout.strip()}")
    except:
        pass
    
    return "\n".join(context_parts)


def _show_project_status():
    """Show current project context."""
    click.echo(click.style("[PROJECT CONTEXT]", fg="blue", bold=True))
    click.echo(_get_project_context())
    click.echo("\n" + click.style("Available Workflows:", fg="green", bold=True))
    click.echo("• Complete Project Development - Creates full applications from requirements to completion")
    click.echo("• Code Analysis & Quality Check - Analyzes existing codebases for quality and structure")
    click.echo("• Documentation Generation - Creates comprehensive project documentation")
    click.echo("\nTry: metis code 'create a todo app with Python' or metis code 'analyze this codebase'")


def _show_help_examples():
    """Show help with natural language examples."""
    click.echo(click.style("\n[HELP] Natural Language Examples", fg="yellow", bold=True))
    click.echo("=" * 40)
    
    examples = [
        "Code Analysis:",
        "  • 'analyze this project structure'",
        "  • 'show me the dependencies in requirements.txt'", 
        "  • 'what functions are in main.py?'",
        "  • 'check for syntax errors in my Python files'",
        "",
        "Code Generation:",
        "  • 'create a calculator class with basic operations'",
        "  • 'generate unit tests for the User class'",
        "  • 'write a function that validates email addresses'", 
        "  • 'create a simple REST API with FastAPI'",
        "",
        "File Operations:",
        "  • 'create a new file called config.py'",
        "  • 'read the contents of setup.py'",
        "  • 'search for all TODO comments in .py files'",
        "  • 'show me the directory tree'",
        "",
        "Code Improvement:",
        "  • 'refactor this function to be more readable'",
        "  • 'optimize the performance of data_processor.py'",
        "  • 'add proper error handling to my API endpoints'",
        "  • 'generate docstrings for all functions in utils.py'",
        "",
        "Documentation:",
        "  • 'create README documentation for this project'",
        "  • 'generate API documentation from my FastAPI code'",
        "  • 'explain what this code does in simple terms'",
    ]
    
    for example in examples:
        click.echo(example)


def _should_create_branch(request_text):
    """Determine if the request should create a new git branch."""
    request_lower = request_text.lower()
    
    # Keywords that suggest code changes
    change_keywords = [
        'create', 'generate', 'add', 'build', 'make', 'write', 'implement',
        'modify', 'update', 'change', 'fix', 'refactor', 'optimize'
    ]
    
    # Keywords that suggest read-only operations
    readonly_keywords = [
        'analyze', 'show', 'list', 'read', 'display', 'explain', 'describe',
        'check', 'review', 'examine', 'tell me about'
    ]
    
    # Check if it's clearly a read-only request
    if any(keyword in request_lower for keyword in readonly_keywords):
        return False
    
    # Check if it's clearly a change request
    if any(keyword in request_lower for keyword in change_keywords):
        return True
    
    # Default to creating branch for ambiguous cases
    return False


def _create_feature_branch(branch_name, auto_branch, description):
    """Create a feature branch for code changes."""
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return True  # Not a git repo, continue without branch
            
    except:
        return True  # Git not available, continue without branch
    
    # Generate branch name
    if branch_name:
        new_branch = branch_name
    elif auto_branch:
        safe_desc = re.sub(r'[^\w\s-]', '', description.lower())
        safe_desc = re.sub(r'\s+', '-', safe_desc.strip())[:30]
        timestamp = datetime.now().strftime("%m%d-%H%M")
        new_branch = f"feature/{safe_desc}-{timestamp}"
    else:
        return True
    
    try:
        # Create and switch to new branch
        result = subprocess.run(
            ["git", "checkout", "-b", new_branch],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            click.echo(click.style(f"[BRANCH] Created branch '{new_branch}'", fg="green"))
            return True
        else:
            # Try to switch to existing branch
            switch_result = subprocess.run(
                ["git", "checkout", new_branch],
                capture_output=True, text=True, timeout=10
            )
            if switch_result.returncode == 0:
                click.echo(click.style(f"[BRANCH] Switched to '{new_branch}'", fg="green"))
                return True
            else:
                click.echo(click.style(f"[WARNING] Could not create branch: {result.stderr.strip()}", fg="yellow"))
                return click.confirm("Continue without creating branch?")
                
    except Exception as e:
        click.echo(click.style(f"[WARNING] Branch creation failed: {str(e)}", fg="yellow"))
        return click.confirm("Continue without creating branch?")


def _handle_code_extraction(response, original_request):
    """Extract and save any code from the agent response."""
    if '```' not in response:
        return
    
    # Extract code blocks
    code_blocks = []
    parts = response.split('```')
    
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Odd indices are code blocks
            lines = part.strip().split('\n')
            language = ""
            code_content = part.strip()
            
            # Check if first line is a language identifier
            if lines and lines[0].strip() in ['python', 'py', 'javascript', 'js', 'java', 'cpp', 'c', 'html', 'css']:
                language = lines[0].strip()
                code_content = '\n'.join(lines[1:])
            
            if code_content.strip():
                code_blocks.append({
                    'language': language,
                    'content': code_content
                })
    
    if not code_blocks:
        return
    
    # Ask user if they want to save the code
    if len(code_blocks) == 1:
        if click.confirm(f"\n[SAVE] Save the generated code to a file?"):
            _save_code_block(code_blocks[0], original_request)
    else:
        click.echo(f"\n[SAVE] Found {len(code_blocks)} code blocks")
        for i, block in enumerate(code_blocks):
            lang_info = f" ({block['language']})" if block['language'] else ""
            if click.confirm(f"Save code block {i+1}{lang_info}?"):
                _save_code_block(block, original_request, suffix=f"_{i+1}")


def _save_code_block(code_block, original_request, suffix=""):
    """Save a single code block to a file."""
    # Suggest filename
    filename = _suggest_filename(original_request, code_block['language']) + suffix
    
    # Ask for filename
    filename = click.prompt("Filename", default=filename)
    
    try:
        with open(filename, 'w') as f:
            f.write(code_block['content'])
        
        click.echo(click.style(f"[SAVED] Code saved to {filename}", fg="green"))
        
        # Auto-commit if in git repo
        _auto_git_commit(filename, original_request)
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Could not save file: {str(e)}", fg="red"))


def _suggest_filename(request, language):
    """Suggest a filename based on the request and language."""
    # Extract meaningful words from request
    words = re.findall(r'\b\w+\b', request.lower())
    meaningful_words = [w for w in words if w not in [
        'create', 'generate', 'add', 'build', 'make', 'write', 'the', 'a', 'an', 
        'for', 'with', 'in', 'to', 'of', 'and', 'or', 'but'
    ]]
    
    if meaningful_words:
        base_name = "_".join(meaningful_words[:3])
    else:
        base_name = "generated_code"
    
    # Determine extension
    extensions = {
        'python': '.py', 'py': '.py',
        'javascript': '.js', 'js': '.js', 
        'java': '.java',
        'cpp': '.cpp', 'c++': '.cpp',
        'c': '.c',
        'html': '.html',
        'css': '.css'
    }
    
    ext = extensions.get(language.lower(), '.py')
    return base_name + ext


def _auto_git_commit(filename, description):
    """Auto-commit the file if in a git repository."""
    try:
        subprocess.run(["git", "add", filename], capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"Add: {description}"], 
            capture_output=True, timeout=10
        )
        click.echo(click.style(f"[COMMIT] Committed {filename}", fg="cyan"))
    except:
        pass  # Silent fail for git operations


def _is_project_creation_request(request_text):
    """Detect if the request is for creating a new project."""
    request_lower = request_text.lower()
    
    # Project creation indicators
    creation_indicators = [
        'create a', 'build a', 'make a', 'develop a', 'generate a',
        'create an', 'build an', 'make an', 'develop an', 'generate an',
        'new project', 'new app', 'new application', 'new website',
        'todo app', 'calculator app', 'web app', 'api', 'website',
        'mobile app', 'desktop app', 'game', 'dashboard'
    ]
    
    # Check if request contains creation indicators
    for indicator in creation_indicators:
        if indicator in request_lower:
            return True
    
    # Check for patterns like "create [something] with [technology]"
    if 'create' in request_lower and ('with' in request_lower or 'using' in request_lower):
        return True
    
    return False


def _handle_project_creation(request_text, agent):
    """Handle project creation requests."""
    click.echo(click.style("[PROJECT CREATION] Detected project creation request", fg="green", bold=True))
    
    try:
        # Initialize project manager
        project_manager = ProjectManager()
        
        # Get enhanced project details from agent
        click.echo(click.style("[AGENT] Analyzing project requirements...", fg="blue"))
        
        analysis_prompt = f"""
Analyze this project creation request: "{request_text}"

Provide a brief analysis including:
1. Project type and complexity
2. Suggested technology stack
3. Key features to implement
4. Development approach

Keep the response concise and focused on the project planning aspects.
"""
        
        agent_response = agent.process_query(analysis_prompt)
        agent_analysis = agent_response.get('response', '') if isinstance(agent_response, dict) else str(agent_response)
        
        # Create the project structure
        click.echo(click.style("[PROJECT] Creating project structure...", fg="blue"))
        project_info = project_manager.create_new_project(request_text, agent_analysis)
        
        # Display success information
        click.echo(click.style("[SUCCESS] Project created successfully!", fg="green", bold=True))
        click.echo(f"Project Name: {project_info['project_name']}")
        click.echo(f"Location: {project_info['project_dir']}")
        click.echo(f"")
        click.echo("Project Structure:")
        click.echo(f"  {project_info['project_name']}/")
        click.echo(f"  +-- Metis/           # Project management files")
        click.echo(f"  |   +-- plan.md      # Development plan")
        click.echo(f"  |   +-- tasks.md     # Task breakdown")
        click.echo(f"  |   +-- design.md    # Technical design")
        click.echo(f"  |   +-- session.json # Session tracking")
        click.echo(f"  +-- src/             # Source code directory")
        click.echo(f"  +-- README.md        # Project documentation")
        click.echo(f"")
        click.echo(click.style("Next Steps:", fg="cyan", bold=True))
        click.echo(f"1. Navigate to the project: cd '{project_info['project_dir']}'")
        click.echo(f"2. Continue development: metis code 'implement the core functionality'")
        click.echo(f"3. Check project status: metis code")
        
        # Show agent analysis if available
        if agent_analysis and len(agent_analysis.strip()) > 0:
            click.echo(f"")
            click.echo(click.style("[AGENT ANALYSIS]", fg="blue", bold=True))
            click.echo(agent_analysis)
        
        return project_info
        
    except Exception as e:
        click.echo(click.style(f"[ERROR] Failed to create project: {str(e)}", fg="red"))
        return None


# Export the main command
def _is_complete_project_request(request_text: str) -> bool:
    """Determine if request should use complete project development blueprint."""
    request_lower = request_text.lower()
    
    # Keywords that indicate complete project development
    project_keywords = [
        'create', 'build', 'make', 'develop', 'generate'
    ]
    
    app_keywords = [
        'app', 'application', 'project', 'system', 'tool', 'website', 'service'
    ]
    
    # Check if request contains project creation keywords + app type
    has_project_keyword = any(keyword in request_lower for keyword in project_keywords)
    has_app_keyword = any(keyword in request_lower for keyword in app_keywords)
    
    # Also check for specific project types
    project_types = [
        'todo app', 'calculator', 'web app', 'api', 'dashboard', 'bot', 'game',
        'cli tool', 'desktop app', 'mobile app', 'microservice'
    ]
    
    has_project_type = any(proj_type in request_lower for proj_type in project_types)
    
    return (has_project_keyword and has_app_keyword) or has_project_type


def _handle_metis_code_workflow(agent, request_text: str, project_context: str, auto: bool = False) -> None:
    """Handle Metis Code multi-phase interactive development workflow using SingleAgent."""
    if auto:
        click.echo(click.style("[AUTO MODE] Building your app automatically...", fg="yellow", bold=True))
        click.echo("I'll create your app without asking questions - using smart defaults.")
    else:
        click.echo(click.style("Hi! I'm excited to help you build your app.", fg="cyan"))
        click.echo("Let's work together to create something amazing - I'll guide you through each step.")
    click.echo()
    
    # Generate a meaningful project name based on the user's request
    project_name = generate_project_name(request_text)
    
    try:
        # Phase 1: Design - Let the agent analyze and ask clarifying questions
        click.echo("\nFirst, let me understand what you want to build...")
        
        design_prompt = f"""
I need to help the user build an application. Here's their request: "{request_text}"

Please:
1. Analyze their request and identify what type of application they want
2. Ask 2-3 specific clarifying questions to better understand their needs
3. Suggest a technology stack and project structure
4. Create a brief project plan

Be conversational and helpful. Focus on understanding their exact requirements before we start coding.
"""
        
        click.echo("Analyzing your request...")
        design_response = agent.process_query(design_prompt)
        
        click.echo("\nMetis:")
        if isinstance(design_response, dict):
            click.echo(design_response.get("response", str(design_response)))
        else:
            click.echo(design_response)
        
        # Get user's clarifications
        click.echo("\n" + "="*50)
        if auto:
            click.echo("\nContinuing with default settings...")
            user_clarifications = ""
        else:
            try:
                user_clarifications = input("\nPlease answer the questions above (or press Enter to continue): ").strip()
            except (EOFError, KeyboardInterrupt):
                click.echo("\nContinuing with default settings...")
                user_clarifications = ""
        
        # Phase 2: Code Creation - Let the agent create the project
        if auto or click.confirm("\nShall we start building your app now?", default=True):
            click.echo("\nGreat! Now let's bring your app to life with code...")
            
            code_prompt = f"""
Now I need to create the actual application code and project structure.

Original request: "{request_text}"
User clarifications: "{user_clarifications or 'None provided'}"
Project context: {project_context}
Suggested project name: "{project_name}"

Please:
1. Create a complete project structure with all necessary files
2. Generate working code for their application
3. Include proper documentation and setup instructions
4. Show the exact file paths and what was created
5. Provide instructions on how to run the application

Use the ProjectManagementTool to create the actual project files. Use the suggested project name "{project_name}" for the project directory. Be specific about file locations and contents.

IMPORTANT: At the end of your response, clearly state the main project directory path in this format:
"PROJECT_LOCATION: [full path to project directory]"
"""
            
            click.echo("Creating your application...")
            code_response = agent.process_query(code_prompt)
            
            click.echo("\nMetis:")
            if isinstance(code_response, dict):
                click.echo(code_response.get("response", str(code_response)))
            else:
                click.echo(code_response)
            
            # Phase 3: Iteration - Let the agent improve and polish
            if auto or click.confirm("\nWould you like me to improve and polish your app?", default=True):
                click.echo("\nTime to polish and improve your app...")
                
                iteration_prompt = f"""
The application has been created. Now I need to improve and polish it.

Original request: "{request_text}"
User clarifications: "{user_clarifications or 'None provided'}"
Project name: "{project_name}"

Please:
1. Review the created project and identify areas for improvement
2. Add error handling, validation, and best practices
3. Enhance the user interface and user experience
4. Add tests if appropriate
5. Provide final setup and deployment instructions
6. Show the final project structure and how to use it

Focus on making the application production-ready and user-friendly.
"""
                
                click.echo("Polishing your application...")
                iteration_response = agent.process_query(iteration_prompt)
                
                click.echo("\nMetis:")
                if isinstance(iteration_response, dict):
                    click.echo(iteration_response.get("response", str(iteration_response)))
                else:
                    click.echo(iteration_response)
        
        # Extract project location from the agent's responses
        project_location = None
        
        # Try to find project path in the responses
        try:
            responses_to_check = []
            if 'design_response' in locals():
                responses_to_check.append(design_response)
            if 'code_response' in locals():
                responses_to_check.append(code_response)
            if 'iteration_response' in locals():
                responses_to_check.append(iteration_response)
            
            for response in responses_to_check:
                if not response:
                    continue
                    
                try:
                    if isinstance(response, dict):
                        response_text = response.get("response", "")
                    else:
                        response_text = str(response)
                    
                    # Look for common project path patterns
                    import re
                    path_patterns = [
                        r'PROJECT_LOCATION:\s*([^\n]+)',  # Our structured format
                        r'(?:Created|Project).*?(?:at|in):?\s*([C-Z]:\\[^\n\s]+)',  # Windows paths
                        r'(?:Created|Project).*?(?:at|in):?\s*(/[^\n\s]+)',  # Unix paths
                        r'(?:find all your files at|located at):?\s*([C-Z]:\\[^\n\s]+)',  # Common phrases
                        r'(?:find all your files at|located at):?\s*(/[^\n\s]+)',
                        r'([C-Z]:\\Users\\[^\\]+\\Desktop\\[^\\\s\n]+)',  # Direct Windows desktop paths
                        r'(/Users/[^/]+/Desktop/[^/\s\n]+)'  # Direct Unix desktop paths
                    ]
                    
                    for pattern in path_patterns:
                        try:
                            matches = re.findall(pattern, response_text, re.IGNORECASE)
                            if matches:
                                # Clean up the match
                                potential_path = matches[0].strip()
                                if len(potential_path) > 5 and ('\\' in potential_path or '/' in potential_path):
                                    project_location = potential_path
                                    break
                        except Exception:
                            continue
                    
                    if project_location:
                        break
                        
                except Exception:
                    continue
                    
        except Exception:
            pass  # Silently handle any extraction errors
        
        # Display completion message with project location
        click.echo(click.style("\nPerfect! Your app is complete and ready to use!", fg="green", bold=True))
        
        if project_location:
            click.echo(click.style(f"\nProject Location: {project_location}", fg="cyan", bold=True))
            click.echo(f"You can find all your files at: {project_location}")
        else:
            click.echo("Check the output above for your project location.")
        
        click.echo("\nHappy coding!")
        
    except KeyboardInterrupt:
        click.echo("\nWorkflow interrupted by user.")
    except Exception as e:
        click.echo(click.style(f"\nError in Metis Code workflow: {str(e)}", fg="red"))

def _handle_blueprint_project_development(agent, request_text: str, project_context: str) -> None:
    """Handle complete project development using enhanced blueprint workflow."""
    click.echo(click.style("[BLUEPRINT WORKFLOW] Detected complete project development request", fg="magenta", bold=True))
    click.echo("Initiating enhanced blueprint development workflow...\n")
    
    try:
        # Import and directly execute BlueprintExecutionTool
        from ..tools.core_tools.blueprint_execution_tool import BlueprintExecutionTool
        
        click.echo(click.style("[BLUEPRINT] Initializing BlueprintExecutionTool...", fg="blue"))
        blueprint_tool = BlueprintExecutionTool()
        
        # Prepare inputs for enhanced workflow
        inputs = {
            "project_request": request_text,
            "skip_questions": False,
            "auto_implement": True,
            "desktop_path": "~/Desktop"
        }
        
        click.echo(click.style(f"[BLUEPRINT] Executing enhanced 'complete_project_development' blueprint...", fg="blue"))
        click.echo(f"Project Request: {request_text}")
        click.echo("Parameters: skip_questions=False, auto_implement=True\n")
        
        # Execute blueprint
        result = blueprint_tool.execute(
            task="execute complete project development blueprint",
            blueprint_name="complete_project_development",
            inputs=inputs
        )
        
        # Display results
        if result.get('success', False):
            click.echo(click.style("[SUCCESS] Blueprint executed successfully!", fg="green", bold=True))
            
            exec_result = result.get('execution_result', {})
            if exec_result.get('success', False):
                click.echo(click.style("[BLUEPRINT COMPLETED] All workflow steps completed!", fg="green"))
                
                # Show outputs if available
                outputs = result.get('outputs', {})
                if outputs:
                    click.echo("\n" + click.style("[OUTPUTS]", fg="cyan", bold=True))
                    for key, value in outputs.items():
                        click.echo(f"  {key}: {value}")
                        
                # Show step summary
                step_results = exec_result.get('step_results', {})
                if step_results:
                    click.echo("\n" + click.style("[STEP SUMMARY]", fg="cyan", bold=True))
                    for step_id, step_result in step_results.items():
                        status = "[SUCCESS]" if step_result.get('success', False) else "[FAILED]"
                        click.echo(f"  {status} {step_id}")
                        
            else:
                click.echo(click.style("[BLUEPRINT FAILED] Workflow execution failed", fg="red", bold=True))
                error = exec_result.get('error', 'Unknown error')
                click.echo(f"Error: {error}")
                
                # Show failed steps
                step_results = exec_result.get('step_results', {})
                for step_id, step_result in step_results.items():
                    if not step_result.get('success', False):
                        click.echo(f"[FAILED] {step_id}: {step_result.get('error', 'Failed')}")
        else:
            click.echo(click.style("[ERROR] Blueprint tool execution failed", fg="red", bold=True))
            error = result.get('error', 'Unknown error')
            click.echo(f"Error: {error}")
            
    except Exception as e:
        click.echo(click.style(f"[CRITICAL ERROR] Blueprint execution failed: {str(e)}", fg="red", bold=True))
        import traceback
        click.echo(traceback.format_exc())


__all__ = ['code']