"""Tool implementations for LocalClaw"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


class ToolRegistry:
    """Registry of available tools"""
    
    def __init__(self, workspace_path: str, restrict_to_workspace: bool = True):
        self.workspace_path = Path(workspace_path).resolve()
        self.restrict_to_workspace = restrict_to_workspace
        self._tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Any]:
        """Register all available tools"""
        return {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "list_dir": self.list_dir,
            "exec": self.exec_command,
        }
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed workspace"""
        if not self.restrict_to_workspace:
            return True
        try:
            resolved = path.resolve()
            return str(resolved).startswith(str(self.workspace_path))
        except Exception:
            return False
    
    def read_file(self, file_path: str, offset: int = 1, limit: int = 100) -> str:
        """Read contents of a file"""
        path = self.workspace_path / file_path
        
        if not self._is_path_allowed(path):
            return f"Error: Access denied. Path '{file_path}' is outside workspace."
        
        if not path.exists():
            return f"Error: File '{file_path}' not found."
        
        if not path.is_file():
            return f"Error: '{file_path}' is not a file."
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start = max(0, offset - 1)
                end = min(len(lines), start + limit)
                content = ''.join(lines[start:end])
                return content if content else "(empty file)"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file"""
        path = self.workspace_path / file_path
        
        if not self._is_path_allowed(path):
            return f"Error: Access denied. Path '{file_path}' is outside workspace."
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def list_dir(self, dir_path: str = ".") -> str:
        """List contents of a directory"""
        path = self.workspace_path / dir_path
        
        if not self._is_path_allowed(path):
            return f"Error: Access denied. Path '{dir_path}' is outside workspace."
        
        if not path.exists():
            return f"Error: Directory '{dir_path}' not found."
        
        if not path.is_dir():
            return f"Error: '{dir_path}' is not a directory."
        
        try:
            items = []
            for item in path.iterdir():
                item_type = "📁" if item.is_dir() else "📄"
                items.append(f"{item_type} {item.name}")
            return "\n".join(items) if items else "(empty directory)"
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def exec_command(self, command: str, timeout: int = 30) -> str:
        """Execute a shell command"""
        if self.restrict_to_workspace:
            # Change to workspace directory
            cwd = str(self.workspace_path)
        else:
            cwd = None
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output if output else "(no output)"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for LLM"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file within the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file relative to workspace"},
                            "offset": {"type": "integer", "description": "Starting line number (1-indexed)", "default": 1},
                            "limit": {"type": "integer", "description": "Maximum number of lines to read", "default": 100}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the file relative to workspace"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "List contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dir_path": {"type": "string", "description": "Path to directory relative to workspace", "default": "."}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "exec",
                    "description": "Execute a shell command in the workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Shell command to execute"},
                            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
    
    def execute(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name"""
        if tool_name not in self._tools:
            return f"Error: Unknown tool '{tool_name}'"
        
        # Map 'exec' to 'exec_command'
        if tool_name == "exec":
            tool_name = "exec_command"
        
        tool = self._tools.get(tool_name)
        if tool is None:
            return f"Error: Tool '{tool_name}' not implemented"
        
        return tool(**kwargs)
