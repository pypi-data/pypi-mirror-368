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
        """Stream text output with Claude Code-like visual effects."""
        click.echo(click.style("\n[THINKING] Processing your request...", fg="blue", bold=True))
        time.sleep(0.3)  # Brief pause for thinking effect
        
        click.echo(click.style("[RESPONSE]", fg="green", bold=True))
        click.echo(click.style("-" * 50, fg="green", dim=True))
        
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
        
        click.echo("\n")
    
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
        """Stream individual file creation with Claude Code-style progress indicators."""
        # Progress indicator with better visual hierarchy
        progress = f"[{index}/{total}]"
        click.echo(click.style(f"\n{progress} Processing {filename}...", fg="cyan", bold=True))
        
        # Show file analysis
        lines = len(content.split('\n'))
        chars = len(content)
        size_kb = len(content.encode('utf-8')) / 1024
        click.echo(click.style(f"├─ Language: {language.title()}", fg="white", dim=True))
        click.echo(click.style(f"├─ Size: {lines} lines, {chars} chars ({size_kb:.1f} KB)", fg="white", dim=True))
        
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
            
            # Show writing progress
            click.echo(click.style(f"├─ Encoding content as UTF-8...", fg="white", dim=True))
            time.sleep(0.05)
            
            # Write file using tools if available
            if self.write_tool:
                try:
                    self.write_tool.execute({
                        'file_path': filepath,
                        'content': content,
                        'mode': 'write'
                    })
                    click.echo(click.style(f"├─ Used WriteTool for file operation", fg="white", dim=True))
                except:
                    # Fallback to direct file write
                    self._write_file_with_fallback(filepath, content)
                    click.echo(click.style(f"├─ Used direct file write (WriteTool failed)", fg="white", dim=True))
            else:
                self._write_file_with_fallback(filepath, content)
                click.echo(click.style(f"├─ Used direct file write", fg="white", dim=True))
            
            # Success with file path
            click.echo(click.style(f"└─ Success: {filename}", fg="green", bold=True))
            rel_path = os.path.relpath(filepath, os.getcwd())
            click.echo(click.style(f"   File: {rel_path}", fg="green", dim=True))
            
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
        """Extract code blocks with improved detection."""
        code_blocks = []
        
        # Pattern for filename: format
        filename_pattern = r'```filename:\s*([^\n]+)\n(.*?)```'
        filename_matches = re.findall(filename_pattern, text, re.DOTALL)
        
        for filename, content in filename_matches:
            language = self._detect_language(content, filename.strip())
            code_blocks.append((filename.strip(), content.strip(), language))
        
        # Pattern for regular code blocks
        code_pattern = r'```(?:([a-zA-Z]+)\n)?(.*?)```'
        all_matches = re.findall(code_pattern, text, re.DOTALL)
        
        for lang_hint, content in all_matches:
            content = content.strip()
            if not content or any(content == existing[1] for existing in code_blocks):
                continue
            
            language, filename = self._detect_language_and_filename(content, lang_hint)
            
            # Avoid duplicates
            counter = 1
            original_filename = filename
            while any(filename == existing[0] for existing in code_blocks):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
            
            code_blocks.append((filename, content, language))
        
        return code_blocks
    
    def _detect_language_and_filename(self, content: str, lang_hint: str = "") -> tuple:
        """Detect programming language and suggest filename."""
        content_lower = content.lower()
        
        # Python detection
        if ('def ' in content or 'import ' in content or 'from ' in content or 
            'class ' in content or lang_hint == 'python'):
            if 'flask' in content_lower or 'app.run' in content:
                return 'python', 'app.py'
            elif 'requirements' in content_lower or lang_hint == 'makefile':
                return 'text', 'requirements.txt'
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
    
    def _should_auto_commit(self) -> bool:
        """Check if we should auto-commit (if in git repo)."""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         cwd=self.project_location, 
                         capture_output=True, check=True, timeout=2)
            return True
        except:
            return False
    
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
        """Show session summary with Claude Code-style formatting."""
        click.echo(click.style("\n" + "=" * 60, fg="cyan", dim=True))
        click.echo(click.style("SESSION COMPLETE", fg="cyan", bold=True))
        click.echo(click.style("=" * 60, fg="cyan", dim=True))
        
        # Show statistics
        total_files = len(self.files_created) + len(self.files_modified)
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
        """Show a simple diff preview like Claude Code."""
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
