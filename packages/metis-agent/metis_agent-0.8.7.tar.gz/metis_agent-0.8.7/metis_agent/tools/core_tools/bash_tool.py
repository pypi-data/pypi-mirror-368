#!/usr/bin/env python3
"""
BashTool - Framework-Compliant Command Execution Tool
Follows Metis Agent Tools Framework v2.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import os
import platform
import shlex
import tempfile
from ..base import BaseTool


class BashTool(BaseTool):
    """
    Production-ready command execution tool with safety features and cross-platform support.
    
    This tool handles executing shell commands with proper error handling,
    timeout management, and security restrictions.
    
    Follows Metis Agent Tools Framework v2.0 standards.
    """
    
    def __init__(self):
        """Initialize bash tool with required attributes."""
        # Required attributes (Framework Rule)
        self.name = "BashTool"  # MUST match class name exactly
        self.description = "Executes shell commands with safety features and cross-platform support"
        
        # Optional metadata
        self.version = "1.0.0"
        self.category = "core_tools"
        
        # Safety configuration
        self.default_timeout = 30  # seconds
        self.max_timeout = 300     # 5 minutes max
        self.max_output_size = 1024 * 1024  # 1MB output limit
        
        # Platform detection
        self.is_windows = platform.system() == 'Windows'
        self.shell_executable = 'cmd.exe' if self.is_windows else '/bin/bash'
        
        # Dangerous commands to block
        self.blocked_commands = {
            'rm -rf /', 'del /f /s /q', 'format', 'fdisk', 'mkfs',
            'dd if=', 'shutdown', 'reboot', 'halt', 'poweroff',
            'passwd', 'sudo su', 'su -', 'chmod 777', 'chown root'
        }
        
        # Safe command patterns
        self.safe_patterns = {
            'ls', 'dir', 'pwd', 'cd', 'echo', 'cat', 'type', 'head', 'tail',
            'grep', 'find', 'which', 'where', 'ps', 'tasklist', 'whoami',
            'date', 'time', 'uptime', 'df', 'du', 'free', 'top', 'htop'
        }
    
    def can_handle(self, task: str) -> bool:
        """
        Intelligent command execution task detection.
        
        Uses multi-layer analysis following Framework v2.0 standards.
        
        Args:
            task: The task description to evaluate
            
        Returns:
            True if task requires command execution, False otherwise
        """
        if not task or not isinstance(task, str):
            return False
        
        task_clean = task.strip().lower()
        
        # Layer 1: Direct command keywords
        command_keywords = {
            'run', 'execute', 'bash', 'shell', 'command', 'cmd',
            'terminal', 'console', 'script', 'process'
        }
        
        has_command_keyword = any(keyword in task_clean for keyword in command_keywords)
        
        # Layer 2: Command-specific phrases
        command_phrases = [
            'run command', 'execute command', 'bash command',
            'shell command', 'run script', 'execute script',
            'in terminal', 'in console', 'command line'
        ]
        
        has_command_phrase = any(phrase in task_clean for phrase in command_phrases)
        
        # Layer 3: Direct command patterns (starts with common commands)
        starts_with_command = any(task_clean.startswith(cmd) for cmd in self.safe_patterns)
        
        # Layer 4: Contains shell operators
        shell_operators = ['&&', '||', '|', '>', '>>', '<', ';']
        has_shell_operators = any(op in task for op in shell_operators)
        
        # Decision logic
        if has_command_keyword or has_command_phrase:
            return True
        elif starts_with_command:
            return True
        elif has_shell_operators and len(task.split()) <= 10:  # Simple commands with operators
            return True
        
        return False
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute shell command with robust error handling and safety features.
        
        Args:
            task: Command execution task to perform
            **kwargs: Additional parameters (command, timeout, working_dir, etc.)
            
        Returns:
            Structured dictionary with command results and metadata
        """
        try:
            # Extract command
            command = self._extract_command(task, kwargs)
            
            if not command:
                return self._error_response("No command found in task or parameters")
            
            # Safety checks
            safety_check = self._check_command_safety(command)
            if not safety_check['safe']:
                return self._error_response(f"Command blocked for safety: {safety_check['reason']}")
            
            # Get execution parameters
            timeout = min(kwargs.get('timeout', self.default_timeout), self.max_timeout)
            working_dir = kwargs.get('working_dir', os.getcwd())
            capture_output = kwargs.get('capture_output', True)
            shell = kwargs.get('shell', True)
            
            # Validate working directory
            if not os.path.exists(working_dir):
                return self._error_response(f"Working directory does not exist: {working_dir}")
            
            # Prepare command for execution
            if self.is_windows and not shell:
                # On Windows, split command for subprocess
                cmd_args = shlex.split(command, posix=False)
            else:
                cmd_args = command
            
            # Execute command
            start_time = datetime.now()
            
            result = subprocess.run(
                cmd_args,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=working_dir,
                env=os.environ.copy()
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Check output size
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
            
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... (error output truncated)"
            
            return {
                "success": result.returncode == 0,
                "type": "bash_response",
                "data": {
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time_seconds": execution_time,
                    "working_directory": working_dir,
                    "platform": platform.system()
                },
                "metadata": {
                    "tool_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "execution_stats": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeout_used": timeout,
                        "stdout_length": len(result.stdout or ""),
                        "stderr_length": len(result.stderr or "")
                    }
                }
            }
            
        except subprocess.TimeoutExpired:
            return self._error_response(f"Command timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            return self._error_response(f"Command failed with return code {e.returncode}: {e.stderr}")
        except Exception as e:
            return self._error_response(f"Command execution failed: {str(e)}", e)
    
    def _extract_command(self, task: str, kwargs: Dict[str, Any]) -> Optional[str]:
        """Extract command from task or parameters."""
        # Check kwargs first
        if 'command' in kwargs:
            return kwargs['command']
        if 'cmd' in kwargs:
            return kwargs['cmd']
        
        # Extract from task text
        import re
        
        # Look for quoted commands
        quoted_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'`([^`]+)`'
        ]
        
        for pattern in quoted_patterns:
            matches = re.findall(pattern, task)
            if matches:
                return matches[0]
        
        # Look for command after keywords
        command_patterns = [
            r'(?:run|execute|bash)\s+(?:command\s+)?(.+)',
            r'(?:command|cmd):\s*(.+)',
            r'(?:shell|terminal):\s*(.+)'
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # If task starts with a known command, use the whole task
        if any(task.strip().lower().startswith(cmd) for cmd in self.safe_patterns):
            return task.strip()
        
        return None
    
    def _check_command_safety(self, command: str) -> Dict[str, Any]:
        """Check if command is safe to execute."""
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                return {
                    'safe': False,
                    'reason': f"Contains blocked command pattern: {blocked}"
                }
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'del\s+/[fs]\s+',
            r'>\s*/dev/',
            r'chmod\s+777',
            r'sudo\s+rm',
            r'dd\s+if='
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                return {
                    'safe': False,
                    'reason': f"Contains dangerous pattern: {pattern}"
                }
        
        # Additional safety checks
        if len(command) > 1000:
            return {
                'safe': False,
                'reason': "Command too long (max 1000 characters)"
            }
        
        return {'safe': True, 'reason': 'Command passed safety checks'}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capability metadata."""
        return {
            "complexity_levels": ["simple", "moderate", "complex"],
            "input_types": ["text", "shell_command"],
            "output_types": ["structured_data", "command_output"],
            "estimated_execution_time": "1-30s",
            "requires_internet": False,
            "requires_filesystem": True,
            "concurrent_safe": False,  # Commands may conflict
            "resource_intensive": True,
            "supported_intents": ["run", "execute", "bash", "shell", "command"],
            "api_dependencies": [],
            "memory_usage": "low-moderate"
        }
    
    def get_examples(self) -> list:
        """Get example tasks that this tool can handle."""
        return [
            "Run command 'ls -la'",
            "Execute 'pwd' to show current directory",
            "Run 'ps aux | grep python'",
            "Execute bash command 'find . -name \"*.py\"'",
            "Run 'df -h' to check disk space",
            "Execute 'whoami' to show current user"
        ]
    
    def _error_response(self, message: str, exception: Exception = None) -> Dict[str, Any]:
        """Generate standardized error response following Framework v2.0."""
        return {
            'success': False,
            'error': message,
            'error_type': type(exception).__name__ if exception else 'ValidationError',
            'suggestions': [
                "Ensure the command is safe and not in the blocked list",
                "Check that you have permissions to execute the command",
                "Verify the working directory exists and is accessible",
                "Use shorter commands (max 1000 characters)",
                "Consider using timeout parameter for long-running commands",
                f"Platform detected: {platform.system()}"
            ],
            'metadata': {
                'tool_name': self.name,
                'error_timestamp': datetime.now().isoformat(),
                'platform': platform.system(),
                'max_timeout': self.max_timeout,
                'blocked_commands': list(self.blocked_commands)[:5]  # Show first 5
            }
        }
