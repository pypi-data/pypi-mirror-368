"""
Gemini-style streaming interface for real-time code generation and editing.
Provides active session management with continuous streaming capabilities.
"""

import click
import os
import re
import time
import datetime
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
import subprocess

# Try to import Rich for enhanced visuals, fallback to basic if not available
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# Fix Windows console encoding issues
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # Fallback to default encodings

class GeminiStreamingInterface:
    """Gemini-style streaming interface with active session management."""
    
    def __init__(self, agent, project_location: str, tools_registry: Dict = None):
        self.agent = agent
        self.project_location = project_location
        self.tools_registry = tools_registry or {}
        self.session_active = True
        self.files_created = []
        self.files_modified = []
        self.current_operation = None
        self.operation_start_time = None
        
        # Initialize tools if available
        self.write_tool = tools_registry.get('WriteTool') if tools_registry else None
        self.project_tool = tools_registry.get('ProjectManagementTool') if tools_registry else None
        
        # Session preferences for Claude Code-style interaction
        self.auto_write_files = False  # Ask user by default
        self.session_write_preference = None  # None, 'all', 'ask', 'skip'
        
        # Set up project directory and git if it's a new project
        self._setup_project_directory()
        
    def start_session(self):
        """Start an active streaming session like Gemini."""
        click.echo(click.style("[STREAMING] Starting Metis Session", fg="cyan", bold=True))
        click.echo(click.style(f"[PROJECT] {os.path.basename(self.project_location)}", fg="blue"))
        click.echo(click.style("-" * 60, fg="white", dim=True))
        
    def stream_response(self, query: str, session_id: Optional[str] = None) -> Generator[str, None, None]:
        """Stream agent response with natural language editing support like Claude Code."""
        self._start_operation("Analyzing request")
        
        try:
            # Check if this is a natural language editing request
            edit_request = self._parse_natural_language_edit(query)
            
            if edit_request:
                # Handle natural language editing like Claude Code
                yield from self._handle_natural_language_edit(edit_request, session_id)
            else:
                # Regular agent response flow
                self._start_operation("Generating response")
                
                # Get response from agent
                response = self.agent.process_query(query, session_id=session_id)
                response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
                
                # Stream the response
                self._stream_text_output(response_text)
                
                # Process and stream code blocks
                yield from self._stream_code_processing(response_text)
            
        except Exception as e:
            self._show_error(f"Streaming error: {str(e)}")
            
        finally:
            self._end_operation()
    
    def _stream_text_output(self, text: str):
        """Stream text output with enhanced formatting for code sections."""
        click.echo(click.style("\n[THINKING] Processing your request...", fg="blue", bold=True))
        time.sleep(0.3)  # Brief pause for thinking effect
        
        click.echo(click.style("[RESPONSE]", fg="green", bold=True))
        click.echo(click.style("-" * 50, fg="green", dim=True))
        
        # Check if text contains inline code or code blocks
        if '```' in text or '`' in text:
            self._stream_formatted_text(text)
        else:
            self._stream_plain_text(text)
        
        click.echo("\n")
    
    def _stream_formatted_text(self, text: str):
        """Stream text with code block formatting using Rich if available."""
        try:
            from rich.console import Console
            from rich.syntax import Syntax
            from rich.panel import Panel
            from rich.markdown import Markdown
            
            console = Console()
            
            # Try to render as markdown for better code block handling
            try:
                md = Markdown(text)
                console.print(md)
                return
            except:
                # Fallback to manual parsing
                pass
                
        except ImportError:
            pass
        
        # Fallback to manual parsing for code blocks
        parts = text.split('```')
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Regular text
                self._stream_plain_text(part)
            else:  # Code block
                lines = part.split('\n')
                if lines:
                    # First line might be language
                    language = lines[0].strip() if lines[0].strip() else 'text'
                    code_content = '\n'.join(lines[1:] if lines[0].strip() else lines)
                    
                    click.echo(click.style(f"\n┌─ {language.title()} Code ─────────────────────────", fg="blue"))
                    
                    # Display code with line numbers
                    code_lines = code_content.split('\n')
                    for line_num, line in enumerate(code_lines, 1):
                        if line.strip():  # Skip empty lines
                            click.echo(click.style(f"│ {line_num:2d} │ {line}", fg="cyan"))
                    
                    click.echo(click.style("└─────────────────────────────────────────────────", fg="blue"))
                    click.echo()
    
    def _stream_plain_text(self, text: str):
        """Stream plain text word by word."""
        if not text.strip():
            return
            
        # Clean text to avoid encoding issues
        try:
            clean_text = text.encode('ascii', 'replace').decode('ascii')
        except:
            clean_text = text
        
        # Word-by-word streaming to avoid character spacing issues
        words = clean_text.split()
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed line length
            if len(current_line + word) > 80 and current_line:
                click.echo()  # New line
                current_line = word + " "
            else:
                current_line += word + " "
            
            try:
                click.echo(word + " ", nl=False)
            except UnicodeEncodeError:
                click.echo("[word] ", nl=False)  # Fallback for problematic characters
            
            # Add slight delay for streaming effect
            time.sleep(0.02)  # Slightly slower for better readability
    
    def _stream_code_processing(self, response_text: str) -> Generator[str, None, None]:
        """Process and stream code blocks with support for file creation and editing."""
        if '```' not in response_text:
            click.echo(click.style("[INFO] No code blocks detected", fg="yellow"))
            return
        
        self._start_operation("Processing code blocks")
        
        # Detect editing operations from response text
        edit_operations = self._detect_edit_operations(response_text)
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(response_text)
        
        if not code_blocks and not edit_operations:
            click.echo(click.style("[INFO] No valid code blocks or edit operations found", fg="yellow"))
            return
        
        total_operations = len(code_blocks) + len(edit_operations)
        click.echo(click.style(f"\n[PROCESSING] {total_operations} file operations", fg="cyan", bold=True))
        click.echo(click.style("-" * 40, fg="cyan", dim=True))
        
        operation_index = 1
        
        # Process edit operations first
        for edit_op in edit_operations:
            yield from self._stream_file_edit(edit_op, operation_index, total_operations)
            operation_index += 1
        
        # Process new file creations
        for filename, content, language in code_blocks:
            yield from self._stream_file_creation(filename, content, language, operation_index, total_operations)
            operation_index += 1
        
        self._show_session_summary()
    
    def _stream_file_creation(self, filename: str, content: str, language: str, index: int, total: int) -> Generator[str, None, None]:
        """Stream individual file creation with Claude Code-style progress indicators and user confirmation."""
        # Progress indicator with better visual hierarchy
        progress = f"[{index}/{total}]"
        click.echo(click.style(f"\n{progress} Processing {filename}...", fg="cyan", bold=True))
        
        # Show file analysis
        lines = len(content.split('\n'))
        chars = len(content)
        size_kb = len(content.encode('utf-8')) / 1024
        click.echo(click.style(f"├─ Language: {language.title()}", fg="white", dim=True))
        click.echo(click.style(f"├─ Size: {lines} lines, {chars} chars ({size_kb:.1f} KB)", fg="white", dim=True))
        
        # Claude Code-style user confirmation
        should_write = self._get_write_permission(filename, content)
        
        if not should_write:
            click.echo(click.style(f"└─ Skipped: {filename}", fg="yellow", bold=True))
            click.echo(click.style(f"   User chose not to write file", fg="yellow", dim=True))
            yield f"⊘ {filename}"
            return
        
        # Show real-time writing steps
        click.echo(click.style(f"├─ Creating directory structure...", fg="blue"))
        time.sleep(0.1)
        
        try:
            # Create file
            filepath = os.path.join(self.project_location, filename)
            file_dir = os.path.dirname(filepath)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)
                if file_dir != self.project_location:
                    rel_dir = os.path.relpath(file_dir, self.project_location)
                    click.echo(click.style(f"├─ Directory ready: {rel_dir}/", fg="blue"))
            
            # Check if file exists
            operation_type = "update" if os.path.exists(filepath) else "create"
            if operation_type == "update":
                click.echo(click.style(f"├─ File exists - updating content...", fg="yellow"))
                self.files_modified.append(filename)
            else:
                click.echo(click.style(f"├─ Writing new file...", fg="blue"))
                self.files_created.append(filename)
            
            # Show code preview with syntax highlighting
            self._display_code_preview(content, language, filename)
            
            # Show writing progress
            click.echo(click.style(f"├─ Encoding content as UTF-8...", fg="white", dim=True))
            time.sleep(0.05)
            
            # Write file using tools if available
            if self.write_tool:
                try:
                    result = self.write_tool.execute("write file", file_path=filepath, content=content, mode='write')
                    if result and result.get('success', False):
                        click.echo(click.style(f"├─ Used WriteTool for file operation", fg="white", dim=True))
                    else:
                        # WriteTool failed, use fallback
                        self._write_file_with_fallback(filepath, content)
                        click.echo(click.style(f"├─ Used direct file write (WriteTool failed)", fg="white", dim=True))
                except Exception as e:
                    # Fallback to direct file write
                    click.echo(click.style(f"├─ WriteTool error: {str(e)}", fg="yellow", dim=True))
                    self._write_file_with_fallback(filepath, content)
                    click.echo(click.style(f"├─ Used direct file write (WriteTool failed)", fg="white", dim=True))
            else:
                self._write_file_with_fallback(filepath, content)
                click.echo(click.style(f"├─ Used direct file write", fg="white", dim=True))
            
            # Verify file was actually written
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                click.echo(click.style(f"└─ Success: {filename}", fg="green", bold=True))
                rel_path = os.path.relpath(filepath, os.getcwd())
                click.echo(click.style(f"   File: {rel_path}", fg="green", dim=True))
                file_size = os.path.getsize(filepath)
                click.echo(click.style(f"   Size: {file_size} bytes", fg="green", dim=True))
            else:
                click.echo(click.style(f"└─ Warning: File may not have been written correctly", fg="yellow", bold=True))
                if os.path.exists(filepath):
                    click.echo(click.style(f"   File exists but is empty", fg="yellow", dim=True))
                else:
                    click.echo(click.style(f"   File does not exist", fg="yellow", dim=True))
                rel_path = os.path.relpath(filepath, os.getcwd())
                click.echo(click.style(f"   Expected: {rel_path}", fg="yellow", dim=True))
            
            # Auto-commit
            if self._should_auto_commit():
                self._auto_git_commit(filepath, f"Add {operation_type}d file: {filename}")
                click.echo(click.style(f"   Git: Committed to repository", fg="cyan", dim=True))
            
            yield f"✓ {filename}"
            
        except Exception as e:
            click.echo(click.style(f"└─ Error: Failed to {operation_type} {filename}", fg="red", bold=True))
            click.echo(click.style(f"   {str(e)}", fg="red", dim=True))
            yield f"✗ {filename}"
    
    def _show_progress_bar(self, operation: str):
        """Show a simple progress bar animation."""
        click.echo(f"    {operation}... ", nl=False)
        for i in range(3):
            click.echo("#", nl=False)
            time.sleep(0.1)
        click.echo(" Done")
    
    def _extract_code_blocks(self, text: str) -> List[tuple]:
        """Extract code blocks with improved detection, filtering out non-programmable content."""
        code_blocks = []
        
        # Pattern for filename: format (highest priority)
        filename_pattern = r'```filename:\s*([^\n]+)\n(.*?)```'
        filename_matches = re.findall(filename_pattern, text, re.DOTALL)
        
        for filename, content in filename_matches:
            language = self._detect_language(content, filename.strip())
            code_blocks.append((filename.strip(), content.strip(), language))
        
        # Pattern for regular code blocks with language hints
        code_pattern = r'```(?:([a-zA-Z]+)\n)?(.*?)```'
        all_matches = re.findall(code_pattern, text, re.DOTALL)
        
        # Filter out command-like content and focus on actual programming code
        excluded_languages = {'bash', 'shell', 'sh', 'cmd', 'terminal', 'console'}
        excluded_patterns = [
            r'^\$\s+',  # Starts with $ (bash command)
            r'^[A-Z_]+:',  # Environment variables 
            r'^cd\s+',  # cd commands
            r'^mkdir\s+',  # mkdir commands
            r'^npm\s+',  # npm commands
            r'^pip\s+',  # pip commands
            r'^\w+\s*:\s*$',  # Single word labels (like "Result:")
        ]
        
        for lang_hint, content in all_matches:
            content = content.strip()
            if not content or any(content == existing[1] for existing in code_blocks):
                continue
            
            # Skip if it's a bash/shell command or similar non-programming content
            if lang_hint and lang_hint.lower() in excluded_languages:
                continue
            
            # Skip if content matches excluded patterns
            if any(re.match(pattern, content, re.MULTILINE) for pattern in excluded_patterns):
                continue
            
            # Skip very short content that's not meaningful code
            if len(content) < 10 and not any(keyword in content.lower() for keyword in ['print', 'function', 'def', 'class', 'import']):
                continue
            
            language, filename = self._detect_language_and_filename(content, lang_hint)
            
            # Only include if it's actual programming content
            if language in ['text'] and not any(keyword in content.lower() for keyword in ['print', 'function', 'def', 'class', 'import', '<html', '{', 'const', 'let', 'var']):
                continue
            
            # Avoid duplicates
            counter = 1
            original_filename = filename
            while any(filename == existing[0] for existing in code_blocks):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            code_blocks.append((filename, content, language))
        
        return code_blocks
    
    def _get_write_permission(self, filename: str, content: str) -> bool:
        """Get user permission to write file like Claude Code."""
        # If we already have a session preference, use it
        if self.session_write_preference == 'all':
            return True
        elif self.session_write_preference == 'skip':
            return False
        
        # Show file preview with Rich panel
        if RICH_AVAILABLE:
            console = Console()
            
            # Create file info table
            file_table = Table.grid(padding=(0, 1))
            file_table.add_column(style="dim", min_width=12)
            file_table.add_column()
            
            lines_count = len(content.split('\n'))
            chars_count = len(content)
            size_kb = len(content.encode('utf-8')) / 1024
            
            file_table.add_row("Filename:", Text(filename, style="bold yellow"))
            file_table.add_row("Lines:", Text(str(lines_count), style="cyan"))
            file_table.add_row("Characters:", Text(str(chars_count), style="cyan")) 
            file_table.add_row("Size:", Text(f"{size_kb:.1f} KB", style="cyan"))
            
            # Show content preview with syntax highlighting
            preview_lines = content.split('\n')[:6]
            preview_content = '\n'.join(preview_lines)
            
            if len(content.split('\n')) > 6:
                remaining_lines = len(content.split('\n')) - 6
                preview_content += f"\n... ({remaining_lines} more lines)"
            
            # Try to apply syntax highlighting based on file extension
            file_ext = filename.split('.')[-1] if '.' in filename else 'text'
            try:
                syntax = Syntax(preview_content, file_ext, theme="github-dark", line_numbers=True, background_color="default")
                content_panel = Panel(syntax, title="[bold white]Content Preview[/bold white]", border_style="bright_black", padding=(0, 1))
            except:
                # Fallback without syntax highlighting
                content_panel = Panel(preview_content, title="[bold white]Content Preview[/bold white]", border_style="bright_black", padding=(0, 1))
            
            # Main confirmation panel
            main_panel = Panel(
                file_table,
                title="[bold yellow]File Write Confirmation[/bold yellow]",
                title_align="left",
                border_style="yellow",
                padding=(0, 1)
            )
            
            console.print(main_panel)
            console.print(content_panel)
            console.print()
        else:
            # Fallback for non-Rich environments
            click.echo(click.style(f"├─ Ready to write: {filename}", fg="blue"))
            
            # Show content preview (first few lines)
            preview_lines = content.split('\n')[:4]
            click.echo(click.style("├─ Content preview:", fg="white", dim=True))
            for line in preview_lines:
                if line.strip():
                    preview = line[:60] + "..." if len(line) > 60 else line
                    click.echo(click.style(f"│   {preview}", fg="white", dim=True))
            content_lines = content.split('\n')
            if len(content_lines) > 4:
                remaining_lines = len(content_lines) - 4
                click.echo(click.style(f"│   ... ({remaining_lines} more lines)", fg="white", dim=True))
            
            # Ask for user confirmation
            click.echo(click.style("├─ Write this file?", fg="yellow", bold=True))
        
        while True:
            try:
                choice = click.prompt(
                    click.style("└─", fg="blue") + " " +
                    click.style("(y)es", fg="green") + " / " +
                    click.style("(n)o", fg="red") + " / " +
                    click.style("(A)ll remaining", fg="cyan") + " / " +
                    click.style("(s)kip all", fg="yellow") + " / " +
                    click.style("(c)ontinue session", fg="magenta"),
                    type=str,
                    show_default=False
                ).lower().strip()
                
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no']:
                    return False
                elif choice in ['a', 'all']:
                    self.session_write_preference = 'all'
                    click.echo(click.style("   Session preference: Write all remaining files", fg="cyan", dim=True))
                    return True
                elif choice in ['s', 'skip']:
                    self.session_write_preference = 'skip'
                    click.echo(click.style("   Session preference: Skip all remaining files", fg="yellow", dim=True))
                    return False
                elif choice in ['c', 'continue']:
                    click.echo(click.style("   Continuing session - will ask for each file", fg="magenta", dim=True))
                    return True
                else:
                    click.echo(click.style("   Please choose: y/n/A/s/c", fg="red", dim=True))
                    
            except (KeyboardInterrupt, EOFError):
                click.echo(click.style("\n   Cancelled by user", fg="yellow"))
                return False
    
    def _get_edit_permission(self, filename: str, operation_type: str, instructions: str) -> bool:
        """Get user permission to edit file like Claude Code."""
        # If we already have a session preference, use it
        if self.session_write_preference == 'all':
            return True
        elif self.session_write_preference == 'skip':
            return False
        
        # Show edit preview with Rich panel
        if RICH_AVAILABLE:
            console = Console()
            
            # Create edit info table
            edit_table = Table.grid(padding=(0, 1))
            edit_table.add_column(style="dim", min_width=12)
            edit_table.add_column()
            
            edit_table.add_row("Filename:", Text(filename, style="bold blue"))
            edit_table.add_row("Operation:", Text(operation_type.title(), style="yellow"))
            
            # Show current file content preview if it exists
            filepath = os.path.join(self.project_location, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                    
                    lines_count = len(current_content.split('\n'))
                    chars_count = len(current_content)
                    edit_table.add_row("Current Size:", Text(f"{lines_count} lines, {chars_count} chars", style="cyan"))
                    
                    # Show current content preview with syntax highlighting
                    preview_lines = current_content.split('\n')[:4]
                    preview_content = '\n'.join(preview_lines)
                    
                    if len(current_content.split('\n')) > 4:
                        remaining_lines = len(current_content.split('\n')) - 4
                        preview_content += f"\n... ({remaining_lines} more lines)"
                    
                    # Try to apply syntax highlighting
                    file_ext = filename.split('.')[-1] if '.' in filename else 'text'
                    try:
                        syntax = Syntax(preview_content, file_ext, theme="github-dark", line_numbers=True, background_color="default")
                        current_content_panel = Panel(syntax, title="[bold white]Current Content[/bold white]", border_style="bright_black", padding=(0, 1))
                    except:
                        current_content_panel = Panel(preview_content, title="[bold white]Current Content[/bold white]", border_style="bright_black", padding=(0, 1))
                    
                except:
                    edit_table.add_row("Current Size:", Text("Unable to read", style="red"))
                    current_content_panel = Panel("Unable to read current content", title="[bold white]Current Content[/bold white]", border_style="red")
            else:
                edit_table.add_row("Status:", Text("File does not exist", style="yellow"))
                current_content_panel = Panel("File will be created", title="[bold green]New File[/bold green]", border_style="green")
            
            # Show edit instructions
            instruction_text = instructions if len(instructions) <= 200 else instructions[:200] + "..."
            instruction_panel = Panel(instruction_text, title="[bold cyan]Edit Instructions[/bold cyan]", border_style="cyan", padding=(0, 1))
            
            # Main confirmation panel
            main_panel = Panel(
                edit_table,
                title="[bold blue]File Edit Confirmation[/bold blue]",
                title_align="left",
                border_style="blue",
                padding=(0, 1)
            )
            
            console.print(main_panel)
            if os.path.exists(filepath):
                console.print(current_content_panel)
            console.print(instruction_panel)
            console.print()
        else:
            # Fallback for non-Rich environments
            click.echo(click.style(f"├─ Ready to edit: {filename}", fg="blue"))
            click.echo(click.style(f"├─ Edit type: {operation_type.title()}", fg="white", dim=True))
            
            # Show current file content preview if it exists
            filepath = os.path.join(self.project_location, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                    
                    preview_lines = current_content.split('\n')[:3]
                    click.echo(click.style("├─ Current content preview:", fg="white", dim=True))
                    for line in preview_lines:
                        if line.strip():
                            preview = line[:50] + "..." if len(line) > 50 else line
                            click.echo(click.style(f"│   {preview}", fg="white", dim=True))
                    if len(current_content.split('\n')) > 3:
                        remaining_lines = len(current_content.split('\n')) - 3
                        click.echo(click.style(f"│   ... ({remaining_lines} more lines)", fg="white", dim=True))
                except:
                    click.echo(click.style("├─ Current content: Unable to preview", fg="white", dim=True))
            
            # Show edit instructions
            instruction_preview = instructions[:80] + "..." if len(instructions) > 80 else instructions
            click.echo(click.style(f"├─ Edit instructions: {instruction_preview}", fg="cyan", dim=True))
            
            # Ask for user confirmation
            click.echo(click.style("├─ Apply this edit?", fg="yellow", bold=True))
        
        while True:
            try:
                choice = click.prompt(
                    click.style("└─", fg="blue") + " " +
                    click.style("(y)es", fg="green") + " / " +
                    click.style("(n)o", fg="red") + " / " +
                    click.style("(A)ll remaining", fg="cyan") + " / " +
                    click.style("(s)kip all", fg="yellow") + " / " +
                    click.style("(c)ontinue session", fg="magenta"),
                    type=str,
                    show_default=False
                ).lower().strip()
                
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no']:
                    return False
                elif choice in ['a', 'all']:
                    self.session_write_preference = 'all'
                    click.echo(click.style("   Session preference: Apply all remaining edits", fg="cyan", dim=True))
                    return True
                elif choice in ['s', 'skip']:
                    self.session_write_preference = 'skip'
                    click.echo(click.style("   Session preference: Skip all remaining operations", fg="yellow", dim=True))
                    return False
                elif choice in ['c', 'continue']:
                    click.echo(click.style("   Continuing session - will ask for each operation", fg="magenta", dim=True))
                    return True
                else:
                    click.echo(click.style("   Please choose: y/n/A/s/c", fg="red", dim=True))
                    
            except (KeyboardInterrupt, EOFError):
                click.echo(click.style("\n   Cancelled by user", fg="yellow"))
                return False
    
    def _detect_language_and_filename(self, content: str, lang_hint: str = "") -> tuple:
        """Detect programming language and suggest filename."""
        content_lower = content.lower()
        
        # Python detection
        if ('def ' in content or 'import ' in content or 'from ' in content or 
            'class ' in content or 'print(' in content or lang_hint == 'python'):
            if 'flask' in content_lower or 'app.run' in content:
                return 'python', 'app.py'
            elif 'requirements' in content_lower or lang_hint == 'makefile':
                return 'text', 'requirements.txt'
            elif 'hello' in content_lower and 'world' in content_lower:
                return 'python', 'hello.py'
            elif 'print(' in content and len(content.split('\n')) <= 3:
                # Simple one-liner or few-liner Python scripts
                return 'python', 'simple.py'
            else:
                return 'python', 'main.py'
        
        # HTML detection
        elif ('<html' in content_lower or '<!doctype' in content_lower or 
              '<div' in content_lower or lang_hint == 'html'):
            if 'index' in content_lower or 'home' in content_lower:
                return 'html', 'index.html'
            else:
                return 'html', 'page.html'
        
        # CSS detection
        elif ('{' in content and '}' in content and ':' in content and 
              ('color' in content_lower or 'font' in content_lower or lang_hint == 'css')):
            return 'css', 'style.css'
        
        # JavaScript detection
        elif ('function' in content or 'const ' in content or 'let ' in content or 
              'var ' in content or lang_hint == 'javascript'):
            return 'javascript', 'script.js'
        
        # JSON detection
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            return 'json', 'config.json'
        
        # Default
        return 'text', 'file.txt'
    
    def _detect_language(self, content: str, filename: str = "") -> str:
        """Detect programming language from content and filename."""
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            ext_map = {
                '.py': 'python', '.js': 'javascript', '.html': 'html',
                '.css': 'css', '.json': 'json', '.txt': 'text',
                '.md': 'markdown', '.yml': 'yaml', '.yaml': 'yaml'
            }
            if ext in ext_map:
                return ext_map[ext]
        
        return self._detect_language_and_filename(content)[0]
    
    def _detect_language_from_filename(self, filename: str) -> str:
        """Detect programming language from filename only."""
        ext = os.path.splitext(filename)[1].lower()
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.json': 'json', '.txt': 'text',
            '.md': 'markdown', '.yml': 'yaml', '.yaml': 'yaml',
            '.ts': 'typescript', '.jsx': 'javascript', '.tsx': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.rs': 'rust'
        }
        return ext_map.get(ext, 'text')
    
    def _write_file_with_fallback(self, filepath: str, content: str):
        """Write file with encoding fallbacks for Windows compatibility."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeEncodeError:
            try:
                with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
            except:
                with open(filepath, 'w', encoding='ascii', errors='replace') as f:
                    f.write(content)
    
    def _display_code_preview(self, content: str, language: str, filename: str):
        """Display prettified code preview with syntax highlighting as it streams."""
        try:
            from rich.console import Console
            from rich.syntax import Syntax
            from rich.panel import Panel
            
            console = Console()
            
            # Limit preview to reasonable size
            preview_lines = content.split('\n')[:25]  # Show first 25 lines
            preview_content = '\n'.join(preview_lines)
            
            # Add truncation indicator if content is longer
            truncated = len(content.split('\n')) > 25
            if truncated:
                remaining_lines = len(content.split('\n')) - 25
                preview_content += f"\n... ({remaining_lines} more lines)"
            
            # Create syntax highlighted preview
            syntax = Syntax(
                preview_content,
                language,
                theme="github-dark",
                line_numbers=True,
                background_color="default"
            )
            
            # Display in a panel with file info
            title = f"[bold white]Preview: {filename}[/bold white]"
            if truncated:
                title += f" [dim](showing first 25 lines)[/dim]"
                
            panel = Panel(
                syntax,
                title=title,
                border_style="bright_blue",
                padding=(0, 1)
            )
            
            click.echo()  # Add spacing before
            console.print(panel)
            click.echo()  # Add spacing after
            
        except ImportError:
            # Fallback for environments without Rich
            click.echo(click.style(f"├─ Code preview ({language}):", fg="cyan"))
            click.echo(click.style("┌" + "─" * 60 + "┐", fg="blue", dim=True))
            
            # Show first few lines with line numbers
            lines = content.split('\n')[:10]
            for i, line in enumerate(lines, 1):
                line_preview = line[:55] + "..." if len(line) > 55 else line
                click.echo(click.style(f"│ {i:2d} │ {line_preview}", fg="white", dim=True))
            
            if len(content.split('\n')) > 10:
                remaining = len(content.split('\n')) - 10
                click.echo(click.style(f"│ .. │ ... ({remaining} more lines)", fg="blue", dim=True))
                
            click.echo(click.style("└" + "─" * 60 + "┘", fg="blue", dim=True))
    
    def _should_auto_commit(self) -> bool:
        """Check if we should auto-commit (if in git repo)."""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         cwd=self.project_location, 
                         capture_output=True, check=True, timeout=2)
            return True
        except:
            return False
    
    def _initialize_git_repo(self) -> bool:
        """Initialize git repository in project location if not exists."""
        try:
            # Check if already a git repo
            if self._should_auto_commit():
                return True
                
            # Initialize git repo
            result = subprocess.run(['git', 'init'], 
                                  cwd=self.project_location, 
                                  capture_output=True, check=False, timeout=10)
            
            if result.returncode == 0:
                # Set up initial git config if needed (basic)
                subprocess.run(['git', 'config', '--local', 'user.name', 'Metis Agent'], 
                             cwd=self.project_location, 
                             capture_output=True, check=False, timeout=5)
                subprocess.run(['git', 'config', '--local', 'user.email', 'metis@agent.local'], 
                             cwd=self.project_location, 
                             capture_output=True, check=False, timeout=5)
                
                # Create initial .gitignore for common patterns
                gitignore_content = """# Metis Agent generated .gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
node_modules/
*.log
.DS_Store
Thumbs.db
*.tmp
*.temp
.metis/
"""
                gitignore_path = os.path.join(self.project_location, '.gitignore')
                if not os.path.exists(gitignore_path):
                    with open(gitignore_path, 'w', encoding='utf-8') as f:
                        f.write(gitignore_content)
                
                # Initial commit
                subprocess.run(['git', 'add', '.gitignore'], 
                             cwd=self.project_location, 
                             capture_output=True, check=False, timeout=5)
                subprocess.run(['git', 'commit', '-m', 'Initial commit: Metis project setup'], 
                             cwd=self.project_location, 
                             capture_output=True, check=False, timeout=5)
                
                click.echo(click.style("├─ Git: Repository initialized", fg="cyan", dim=True))
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Git initialization failed: {e}")
            return False
    
    def _setup_project_directory(self):
        """Set up project directory structure and initialize git if needed."""
        # Ensure project directory exists
        if not os.path.exists(self.project_location):
            os.makedirs(self.project_location, exist_ok=True)
            click.echo(click.style("├─ Project directory created", fg="blue", dim=True))
            
            # Initialize git for new projects
            self._initialize_git_repo()
        else:
            # For existing directories, only initialize git if not already a git repo
            if not self._should_auto_commit():
                self._initialize_git_repo()
    
    def _auto_git_commit(self, filepath: str, message: str):
        """Auto-commit files to git if in a git repo."""
        try:
            subprocess.run(['git', 'add', filepath], 
                         cwd=self.project_location, 
                         capture_output=True, check=False, timeout=5)
            result = subprocess.run(['git', 'commit', '-m', message], 
                         cwd=self.project_location, 
                         capture_output=True, check=False, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_operation(self, operation: str):
        """Start tracking an operation."""
        self.current_operation = operation
        self.operation_start_time = time.time()
        click.echo(click.style(f"[OPERATION] {operation}...", fg="cyan"))
    
    def _end_operation(self):
        """End current operation and show timing."""
        if self.operation_start_time:
            duration = time.time() - self.operation_start_time
            click.echo(click.style(f"[COMPLETE] {duration:.2f}s", fg="green"))
        self.current_operation = None
        self.operation_start_time = None
    
    def _show_error(self, error_msg: str):
        """Show error message with styling."""
        click.echo(click.style(f"[ERROR] {error_msg}", fg="red", bold=True))
    
    def _show_interactive_help(self):
        """Show help for interactive session."""
        click.echo(click.style("\nInteractive Session Commands:", fg="cyan", bold=True))
        click.echo(click.style("-" * 40, fg="cyan", dim=True))
        click.echo(click.style("help", fg="green") + "                    - Show this help")
        click.echo(click.style("status, info", fg="green") + "            - Show project status")
        click.echo(click.style("clear", fg="green") + "                   - Clear screen")
        click.echo(click.style("exit, quit, bye, done", fg="green") + "    - End session")
        
        click.echo(click.style("\nExample Requests:", fg="cyan", bold=True))
        click.echo("• 'Create a Python function to calculate fibonacci'")
        click.echo("• 'Add error handling to the main.py file'")
        click.echo("• 'Generate a web API with Flask'")
        click.echo("• 'Write unit tests for my calculator class'")
        click.echo("• 'Refactor the code to be more efficient'")
        click.echo("• 'Add documentation to all functions'")
        click.echo()
    
    def _show_project_status(self):
        """Show current project status."""
        click.echo(click.style("\nProject Status:", fg="cyan", bold=True))
        click.echo(click.style("-" * 20, fg="cyan", dim=True))
        click.echo(click.style(f"Location: ", fg="white") + click.style(f"{self.project_location}", fg="blue"))
        
        # Show files in project
        try:
            if os.path.exists(self.project_location):
                all_files = []
                for root, dirs, files in os.walk(self.project_location):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), self.project_location)
                        all_files.append(rel_path)
                
                if all_files:
                    click.echo(click.style(f"Files: ", fg="white") + click.style(f"{len(all_files)} total", fg="green"))
                    # Show first few files
                    for file in all_files[:5]:
                        click.echo(click.style(f"  • {file}", fg="white", dim=True))
                    if len(all_files) > 5:
                        click.echo(click.style(f"  ... and {len(all_files) - 5} more", fg="white", dim=True))
                else:
                    click.echo(click.style("Files: ", fg="white") + click.style("No files yet", fg="yellow"))
            else:
                click.echo(click.style("Status: ", fg="white") + click.style("Project directory not created yet", fg="yellow"))
        except:
            click.echo(click.style("Status: ", fg="white") + click.style("Unable to read project directory", fg="red"))
        
        # Show session stats
        if self.files_created or self.files_modified:
            click.echo(click.style("Session: ", fg="white") + 
                      click.style(f"{len(self.files_created)} created, {len(self.files_modified)} modified", fg="green"))
        else:
            click.echo(click.style("Session: ", fg="white") + click.style("No files processed yet", fg="yellow"))
        click.echo()
    
    def _show_session_summary(self):
        """Show session summary with Rich panels or fallback formatting."""
        total_files = len(self.files_created) + len(self.files_modified)
        
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text
            
            console = Console()
            console.print()
            
            # Create summary table
            summary_table = Table(show_header=False, show_edge=False, padding=(0, 2))
            summary_table.add_column(style="bold cyan", width=20)
            summary_table.add_column()
            
            summary_table.add_row("Total Files:", f"{total_files}")
            summary_table.add_row("Created:", f"{len(self.files_created)}")
            summary_table.add_row("Modified:", f"{len(self.files_modified)}")
            
            # Main session panel
            session_panel = Panel(
                summary_table,
                title="[bold cyan]Session Complete[/bold cyan]",
                title_align="center",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(session_panel)
            
            # Files details if any files were processed
            if total_files > 0:
                details_table = Table(show_header=False, show_edge=False, padding=(0, 1))
                details_table.add_column(style="bold", width=15)
                details_table.add_column()
                
                if self.files_created:
                    details_table.add_row("[green]Created:[/green]", "")
                    for file in self.files_created:
                        details_table.add_row("", f"[green]• {file}[/green]")
                
                if self.files_modified:
                    if self.files_created:  # Add spacing if we have both
                        details_table.add_row("", "")
                    details_table.add_row("[yellow]Modified:[/yellow]", "")
                    for file in self.files_modified:
                        details_table.add_row("", f"[yellow]• {file}[/yellow]")
                
                details_panel = Panel(
                    details_table,
                    title="[bold white]File Operations[/bold white]",
                    title_align="left",
                    border_style="bright_black",
                    padding=(0, 1)
                )
                console.print(details_panel)
            
        except ImportError:
            # Fallback for non-Rich environments
            click.echo(click.style("\n" + "=" * 60, fg="cyan", dim=True))
            click.echo(click.style("SESSION COMPLETE", fg="cyan", bold=True))
            click.echo(click.style("=" * 60, fg="cyan", dim=True))
            
            # Show statistics
            if total_files > 0:
                click.echo(click.style(f"\nFiles processed: {total_files}", fg="white", bold=True))
                
                if self.files_created:
                    click.echo(click.style(f"\n✓ Created ({len(self.files_created)}):", fg="green", bold=True))
                    for file in self.files_created:
                        click.echo(click.style(f"  • {file}", fg="green", dim=True))
                
                if self.files_modified:
                    click.echo(click.style(f"\n✓ Modified ({len(self.files_modified)}):", fg="yellow", bold=True))
                    for file in self.files_modified:
                        click.echo(click.style(f"  • {file}", fg="yellow", dim=True))
        
        # Show project location
        click.echo(click.style(f"\nProject location:", fg="blue", bold=True))
        click.echo(click.style(f"  {self.project_location}", fg="blue", dim=True))
        
        # Show next steps
        if total_files > 0:
            click.echo(click.style(f"\nNext steps:", fg="cyan", bold=True))
            rel_path = os.path.relpath(self.project_location, os.getcwd())
            click.echo(click.style(f"  cd {rel_path}", fg="white", dim=True))
            if any(f.endswith('.py') for f in self.files_created):
                click.echo(click.style(f"  python main.py  # (if applicable)", fg="white", dim=True))
        
        click.echo(click.style("\n" + "-" * 60, fg="white", dim=True))
    
    def interactive_session(self):
        """Start an interactive Claude Code-style session for continuous editing."""
        self.start_session()
        
        # Show session intro
        click.echo(click.style("\nInteractive Development Session", fg="cyan", bold=True))
        click.echo(click.style("Type your requests naturally. I'll help you build and modify code in real-time.", fg="white"))
        click.echo(click.style("Commands: 'help' for examples, 'status' for project info, 'exit' to quit", fg="white", dim=True))
        click.echo()
        
        while self.session_active:
            try:
                # Get user input with better prompt
                query = click.prompt(
                    click.style("You", fg="blue", bold=True),
                    prompt_suffix=click.style(" > ", fg="blue")
                )
                
                if not query.strip():
                    continue
                    
                # Handle special commands
                if query.lower() in ['exit', 'quit', 'bye', 'done']:
                    self.session_active = False
                    click.echo(click.style("\nSession ended. Happy coding!", fg="green", bold=True))
                    self._show_session_summary()
                    break
                elif query.lower() == 'help':
                    self._show_interactive_help()
                    continue
                elif query.lower() in ['status', 'info']:
                    self._show_project_status()
                    continue
                elif query.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                
                # Stream response
                list(self.stream_response(query))
                
            except KeyboardInterrupt:
                click.echo(click.style("\n\nSession interrupted. Type 'exit' to quit or continue chatting.", fg="yellow"))
                continue
            except EOFError:
                click.echo(click.style("\n\nSession ended.", fg="green"))
                break
            except Exception as e:
                self._show_error(f"Session error: {str(e)}")
                continue

    def _parse_natural_language_edit(self, query: str) -> Optional[dict]:
        """Parse natural language editing requests like Claude Code."""
        import re
        
        # Patterns for natural language editing commands
        edit_patterns = [
            # Direct file editing: "edit file.py to add function"
            (r'edit\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)\s+to\s+(.+)', 'edit_file'),
            # Modify patterns: "modify the calculate function in utils.py"
            (r'modify\s+(?:the\s+)?([a-zA-Z_]\w+)\s+(?:function|method|class)\s+in\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)', 'modify_function'),
            # Add patterns: "add error handling to main.py"
            (r'add\s+(.+?)\s+to\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)', 'add_to_file'),
            # Update patterns: "update the login method in auth.py"
            (r'update\s+(?:the\s+)?([a-zA-Z_]\w+)\s+(?:function|method|class)\s+in\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)', 'update_function'),
            # Refactor patterns: "refactor user_login in app.py to use async"
            (r'refactor\s+([a-zA-Z_]\w+)\s+in\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)\s+to\s+(.+)', 'refactor_function'),
            # Fix patterns: "fix the bug in parser.py"
            (r'fix\s+(?:the\s+)?(.+?)\s+in\s+([a-zA-Z_][a-zA-Z0-9_./]*\.py)', 'fix_issue'),
        ]
        
        for pattern, edit_type in edit_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if edit_type == 'edit_file':
                    return {
                        'type': edit_type,
                        'file': groups[0],
                        'instruction': groups[1],
                        'query': query
                    }
                elif edit_type in ['modify_function', 'update_function']:
                    return {
                        'type': edit_type,
                        'function': groups[0],
                        'file': groups[1],
                        'query': query
                    }
                elif edit_type == 'add_to_file':
                    return {
                        'type': edit_type,
                        'instruction': groups[0],
                        'file': groups[1],
                        'query': query
                    }
                elif edit_type == 'refactor_function':
                    return {
                        'type': edit_type,
                        'function': groups[0],
                        'file': groups[1],
                        'instruction': groups[2],
                        'query': query
                    }
                elif edit_type == 'fix_issue':
                    return {
                        'type': edit_type,
                        'instruction': groups[0],
                        'file': groups[1],
                        'query': query
                    }
        
        return None
    
    def _handle_natural_language_edit(self, edit_request: dict, session_id: Optional[str] = None) -> Generator[str, None, None]:
        """Handle natural language editing requests with Claude Code-style interface."""
        filename = edit_request['file']
        filepath = os.path.join(self.project_location, filename)
        
        click.echo(click.style(f"\n[EDIT REQUEST] {edit_request['type'].replace('_', ' ').title()}", fg="yellow", bold=True))
        click.echo(click.style(f"├─ Target: {filename}", fg="white", dim=True))
        click.echo(click.style(f"├─ Instruction: {edit_request.get('instruction', edit_request['query'])[:80]}...", fg="white", dim=True))
        
        # Check if file exists
        if not os.path.exists(filepath):
            click.echo(click.style(f"├─ File not found: {filename}", fg="red"))
            click.echo(click.style(f"└─ Creating new file with requested content", fg="blue"))
            yield from self._create_file_for_edit_request(edit_request)
            return
        
        # Read existing file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            original_lines = len(original_content.split('\n'))
            click.echo(click.style(f"├─ Current file: {original_lines} lines", fg="green"))
            
            # Generate edit using agent with context
            edit_prompt = self._create_edit_prompt(edit_request, original_content)
            click.echo(click.style(f"├─ Generating targeted edit...", fg="blue"))
            time.sleep(0.2)
            
            response = self.agent.process_query(edit_prompt, session_id=session_id)
            response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
            
            # Extract and apply the edit
            new_content = self._extract_edited_content(response_text, original_content)
            
            if new_content and new_content != original_content:
                # Apply the edit
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                new_lines = len(new_content.split('\n'))
                lines_diff = new_lines - original_lines
                
                click.echo(click.style(f"├─ Edit applied successfully", fg="green"))
                click.echo(click.style(f"├─ New file: {new_lines} lines ({lines_diff:+d})", fg="green"))
                
                # Show diff preview
                self._show_edit_diff(original_content, new_content, filename)
                
                # Track modification
                if filename not in self.files_modified:
                    self.files_modified.append(filename)
                
                # Auto-commit
                if self._should_auto_commit():
                    self._auto_git_commit(filepath, f"Edit {filename}: {edit_request['type']}")
                    click.echo(click.style(f"├─ Git: Changes committed", fg="cyan", dim=True))
                
                click.echo(click.style(f"└─ Success: {filename} updated", fg="green", bold=True))
                yield f"✓ Edited {filename}"
                
            else:
                click.echo(click.style(f"└─ No changes needed or edit failed", fg="yellow"))
                yield f"- No changes to {filename}"
                
        except Exception as e:
            click.echo(click.style(f"└─ Error: Failed to edit {filename}", fg="red", bold=True))
            click.echo(click.style(f"   {str(e)}", fg="red", dim=True))
            yield f"✗ Edit failed: {filename}"
    
    def _create_edit_prompt(self, edit_request: dict, original_content: str) -> str:
        """Create a targeted edit prompt for the agent."""
        filename = edit_request['file']
        edit_type = edit_request['type']
        
        if edit_type == 'edit_file':
            instruction = edit_request['instruction']
            return f"""You are a code editor. I need to edit the file {filename} based on this instruction: "{instruction}"

Current file content:
```python
{original_content}
```

Please implement the requested changes and return ONLY the complete updated Python file content between triple backticks. Do not include any explanations, just the code.

Example format:
```python
# Your updated code here
```"""

        elif edit_type in ['modify_function', 'update_function']:
            function_name = edit_request['function']
            return f"""I need to modify the {function_name} function in {filename}. Here's the current file:

```python
{original_content}
```

Please update the {function_name} function based on this request: {edit_request['query']}
Return ONLY the complete updated file content, nothing else."""

        elif edit_type == 'add_to_file':
            instruction = edit_request['instruction']
            return f"""I need to add {instruction} to {filename}. Here's the current content:

```python
{original_content}
```

Please add the requested functionality. Return ONLY the complete updated file content, nothing else."""

        elif edit_type == 'refactor_function':
            function_name = edit_request['function']
            instruction = edit_request['instruction']
            return f"""I need to refactor the {function_name} function in {filename} to {instruction}. Here's the current file:

```python
{original_content}
```

Please refactor the {function_name} function accordingly. Return ONLY the complete updated file content, nothing else."""

        elif edit_type == 'fix_issue':
            instruction = edit_request['instruction']
            return f"""I need to fix {instruction} in {filename}. Here's the current content:

```python
{original_content}
```

Please fix the issue. Return ONLY the complete updated file content, nothing else."""

        else:
            return f"""Please help with this edit request for {filename}: {edit_request['query']}

Current file content:
```python
{original_content}
```

Return ONLY the complete updated file content, nothing else."""
    
    def _extract_edited_content(self, response_text: str, original_content: str) -> str:
        """Extract the edited file content from agent response."""
        import re
        
        # Look for code blocks in the response - more flexible pattern
        code_patterns = [
            r'```python\n(.*?)```',  # python code blocks
            r'```\n(.*?)```',        # generic code blocks
            r'```(?:py)?\n(.*?)```'  # py code blocks
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                # Return the first substantial code block that looks like Python
                for match in matches:
                    content = match.strip()
                    # Check if it looks like valid Python content
                    if (len(content) > 10 and 
                        ('def ' in content or 'import ' in content or 'class ' in content or
                         content.startswith('"""') or content.startswith('#'))):
                        return content
                # If no Python-like content, return the first match if it's different
                if matches and matches[0].strip() != original_content.strip():
                    return matches[0].strip()
        
        
        # If no code blocks, look for the content directly
        lines = response_text.split('\n')
        content_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class ') or line.strip().startswith('import '):
                in_code = True
            if in_code:
                content_lines.append(line)
        
        if content_lines:
            return '\n'.join(content_lines)
        
        return original_content
    
    def _show_edit_diff(self, original: str, new: str, filename: str):
        """Show a Rich diff preview with green/red styling."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text
            
            console = Console()
            original_lines = original.split('\n')
            new_lines = new.split('\n')
            
            # Create diff table
            diff_table = Table(show_header=False, show_edge=False, padding=(0, 1))
            diff_table.add_column(width=3)  # For +/- symbols
            diff_table.add_column()  # For content
            
            # Simple diff - show first few different lines
            max_diff_lines = 5
            diff_count = 0
            
            for i, (old_line, new_line) in enumerate(zip(original_lines, new_lines)):
                if old_line.strip() != new_line.strip() and diff_count < max_diff_lines:
                    # Show removed line
                    old_preview = old_line[:80] + "..." if len(old_line) > 80 else old_line
                    diff_table.add_row("[red]-[/red]", f"[red dim]{old_preview}[/red dim]")
                    
                    # Show added line  
                    new_preview = new_line[:80] + "..." if len(new_line) > 80 else new_line
                    diff_table.add_row("[green]+[/green]", f"[green]{new_preview}[/green]")
                    
                    diff_count += 1
            
            # Show summary for added/removed lines
            if len(new_lines) > len(original_lines):
                added = len(new_lines) - len(original_lines)
                diff_table.add_row("[green]+[/green]", f"[green dim]{added} new lines added[/green dim]")
            elif len(original_lines) > len(new_lines):
                removed = len(original_lines) - len(new_lines)
                diff_table.add_row("[red]-[/red]", f"[red dim]{removed} lines removed[/red dim]")
            
            # Create panel with changes
            if diff_count > 0 or len(new_lines) != len(original_lines):
                diff_panel = Panel(
                    diff_table,
                    title=f"[bold cyan]Changes Preview: {filename}[/bold cyan]",
                    border_style="cyan",
                    padding=(0, 1)
                )
                console.print(diff_panel)
            
        except ImportError:
            # Fallback for non-Rich environments
            original_lines = original.split('\n')
            new_lines = new.split('\n')
            
            click.echo(click.style(f"├─ Changes preview for {filename}:", fg="cyan"))
            
            # Simple diff - show first few different lines
            max_diff_lines = 3
            diff_count = 0
            
            for i, (old_line, new_line) in enumerate(zip(original_lines, new_lines)):
                if old_line.strip() != new_line.strip() and diff_count < max_diff_lines:
                    click.echo(click.style(f"│  - {old_line[:60]}{'...' if len(old_line) > 60 else ''}", fg="red", dim=True))
                    click.echo(click.style(f"│  + {new_line[:60]}{'...' if len(new_line) > 60 else ''}", fg="green", dim=True))
                    diff_count += 1
            
            # Show added lines if new file is longer
            if len(new_lines) > len(original_lines):
                added = len(new_lines) - len(original_lines)
                click.echo(click.style(f"│  + {added} new lines added", fg="green", dim=True))
    
    def _create_file_for_edit_request(self, edit_request: dict) -> Generator[str, None, None]:
        """Create a new file based on edit request when file doesn't exist."""
        filename = edit_request['file']
        instruction = edit_request.get('instruction', edit_request['query'])
        
        # Generate content for new file
        create_prompt = f"""Create a new Python file {filename} that {instruction}.
        
Return ONLY the complete file content, nothing else."""
        
        response = self.agent.process_query(create_prompt)
        response_text = response.get("response", str(response)) if isinstance(response, dict) else str(response)
        
        # Extract content and create file
        content = self._extract_edited_content(response_text, "")
        if content:
            filepath = os.path.join(self.project_location, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            lines = len(content.split('\n'))
            click.echo(click.style(f"└─ Created {filename} ({lines} lines)", fg="green", bold=True))
            
            if filename not in self.files_created:
                self.files_created.append(filename)
            
            yield f"✓ Created {filename}"
        else:
            click.echo(click.style(f"└─ Failed to generate content for {filename}", fg="red"))
            yield f"✗ Failed to create {filename}"

    def _detect_edit_operations(self, response_text: str) -> List[dict]:
        """Detect file editing operations from agent response."""
        import re
        
        edit_operations = []
        
        # Look for patterns that indicate file editing
        edit_patterns = [
            r'edit\s+(?:the\s+)?(?:file\s+)?(?:"`?([^`"\s]+)`?"|\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b)',
            r'modify\s+(?:the\s+)?(?:file\s+)?(?:"`?([^`"\s]+)`?"|\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b)',
            r'update\s+(?:the\s+)?(?:file\s+)?(?:"`?([^`"\s]+)`?"|\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b)',
            r'change\s+(?:the\s+)?(?:file\s+)?(?:"`?([^`"\s]+)`?"|\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b)',
            r'add\s+(?:to\s+)?(?:the\s+)?(?:file\s+)?(?:"`?([^`"\s]+)`?"|\b([a-zA-Z_][a-zA-Z0-9_]*\.py)\b)',
        ]
        
        for pattern in edit_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                filename = match.group(1) or match.group(2)
                if filename:
                    # Look for associated code block or instructions
                    edit_op = {
                        'type': 'edit',
                        'filename': filename,
                        'operation': self._extract_edit_operation_type(response_text, filename),
                        'instructions': self._extract_edit_instructions(response_text, filename)
                    }
                    edit_operations.append(edit_op)
        
        return edit_operations
    
    def _extract_edit_operation_type(self, response_text: str, filename: str) -> str:
        """Extract the type of edit operation."""
        filename_context = self._get_filename_context(response_text, filename)
        
        if any(word in filename_context.lower() for word in ['add', 'insert', 'include']):
            return 'add'
        elif any(word in filename_context.lower() for word in ['replace', 'change', 'modify']):
            return 'replace'
        elif any(word in filename_context.lower() for word in ['remove', 'delete']):
            return 'remove'
        else:
            return 'modify'
    
    def _extract_edit_instructions(self, response_text: str, filename: str) -> str:
        """Extract editing instructions for a specific file."""
        lines = response_text.split('\n')
        instructions = []
        collecting = False
        
        for line in lines:
            if filename.lower() in line.lower() and any(keyword in line.lower() for keyword in ['edit', 'modify', 'add', 'change']):
                collecting = True
            elif collecting:
                if line.strip() and not line.startswith('```'):
                    instructions.append(line.strip())
                elif line.startswith('```') and instructions:
                    break
        
        return ' '.join(instructions[:3])  # First few instruction lines
    
    def _get_filename_context(self, response_text: str, filename: str) -> str:
        """Get context around filename mention."""
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if filename.lower() in line.lower():
                context_lines = lines[max(0, i-1):i+2]
                return ' '.join(context_lines)
        return ''
    
    def _stream_file_edit(self, edit_op: dict, index: int, total: int) -> Generator[str, None, None]:
        """Stream file editing operations with diff-style progress."""
        filename = edit_op['filename']
        operation_type = edit_op['operation']
        instructions = edit_op['instructions']
        
        progress = f"[{index}/{total}]"
        click.echo(click.style(f"\n{progress} Editing {filename}...", fg="yellow", bold=True))
        
        # Show edit analysis
        click.echo(click.style(f"├─ Operation: {operation_type.title()}", fg="white", dim=True))
        click.echo(click.style(f"├─ Instructions: {instructions[:60]}{'...' if len(instructions) > 60 else ''}", fg="white", dim=True))
        
        # User confirmation for edits
        should_edit = self._get_edit_permission(filename, operation_type, instructions)
        
        if not should_edit:
            click.echo(click.style(f"└─ Skipped: {filename} edit", fg="yellow", bold=True))
            click.echo(click.style(f"   User chose not to edit file", fg="yellow", dim=True))
            yield f"⊘ {filename} edit"
            return
        
        filepath = os.path.join(self.project_location, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            click.echo(click.style(f"├─ File not found, creating new file...", fg="blue"))
            # If file doesn't exist, treat as creation
            yield from self._create_missing_file_for_edit(filename, instructions, index, total)
            return
        
        # Read current file content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            original_lines = len(original_content.split('\n'))
            click.echo(click.style(f"├─ Current: {original_lines} lines", fg="white", dim=True))
            
            # Apply edit using EditTool if available
            if self.tools_registry and 'EditTool' in self.tools_registry:
                edit_tool = self.tools_registry['EditTool']
                click.echo(click.style(f"├─ Using EditTool for precise editing...", fg="blue"))
                
                # For now, simulate edit operation
                # In a full implementation, this would parse the instructions
                # and apply specific edits
                new_content = self._apply_edit_instructions(original_content, instructions, operation_type)
                
                # Write the edited content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                new_lines = len(new_content.split('\n'))
                lines_diff = new_lines - original_lines
                
                click.echo(click.style(f"├─ Applied edits successfully", fg="green"))
                click.echo(click.style(f"├─ New: {new_lines} lines ({lines_diff:+d})", fg="green"))
                
            else:
                click.echo(click.style(f"├─ EditTool not available, skipping precise editing", fg="yellow"))
            
            # Track modification
            if filename not in self.files_modified:
                self.files_modified.append(filename)
            
            # Success
            click.echo(click.style(f"└─ Success: Edited {filename}", fg="green", bold=True))
            rel_path = os.path.relpath(filepath, os.getcwd())
            click.echo(click.style(f"   File: {rel_path}", fg="green", dim=True))
            
            # Auto-commit
            if self._should_auto_commit():
                self._auto_git_commit(filepath, f"Edit {filename}: {operation_type}")
                click.echo(click.style(f"   Git: Committed changes", fg="cyan", dim=True))
            
            yield f"✓ Edited {filename}"
            
        except Exception as e:
            click.echo(click.style(f"└─ Error: Failed to edit {filename}", fg="red", bold=True))
            click.echo(click.style(f"   {str(e)}", fg="red", dim=True))
            yield f"✗ Edit failed: {filename}"
    
    def _apply_edit_instructions(self, content: str, instructions: str, operation_type: str) -> str:
        """Apply edit instructions to content (simplified implementation)."""
        # This is a simplified implementation
        # In a full version, this would parse specific instructions and apply targeted edits
        
        if operation_type == 'add':
            # Simple append operation
            return content + f"\n\n# Added based on instructions: {instructions}\n"
        elif operation_type == 'replace':
            # Simple replacement (would need more sophisticated parsing)
            return content + f"\n\n# Modified based on instructions: {instructions}\n"
        else:
            # Default modification
            return content + f"\n\n# Updated based on instructions: {instructions}\n"
    
    def _create_missing_file_for_edit(self, filename: str, instructions: str, index: int, total: int) -> Generator[str, None, None]:
        """Create a new file when edit target doesn't exist."""
        # Generate basic content based on file type and instructions
        content = self._generate_basic_file_content(filename, instructions)
        language = self._detect_language_from_filename(filename)
        
        # Use the existing file creation method
        yield from self._stream_file_creation(filename, content, language, index, total)
    
    def _generate_basic_file_content(self, filename: str, instructions: str) -> str:
        """Generate basic file content based on filename and instructions."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.py':
            return f'"""Generated file: {filename}\nInstructions: {instructions}\n"""\n\n# Add your code here\n'
        elif ext in ['.js', '.ts']:
            return f'// Generated file: {filename}\n// Instructions: {instructions}\n\n// Add your code here\n'
        elif ext == '.html':
            return f'<!DOCTYPE html>\n<html>\n<head>\n    <title>{filename}</title>\n</head>\n<body>\n    <!-- Instructions: {instructions} -->\n</body>\n</html>\n'
        else:
            return f'Generated file: {filename}\nInstructions: {instructions}\n\nAdd your content here.\n'


def create_streaming_session(agent, project_location: str) -> GeminiStreamingInterface:
    """Create a new streaming session."""
    return GeminiStreamingInterface(agent, project_location)
