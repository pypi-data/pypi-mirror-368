#!/usr/bin/env python3
"""
Enhanced Python Help Tool with Rich Library and Pager Support
Author: Hadi Cahyadi (cumulus13@gmail.com)
License: MIT
"""

import os
import sys
import time
import importlib
import subprocess
from pathlib import Path
from typing import Optional, List, Any, Union
import threading
import io
from contextlib import redirect_stdout
import argparse
import inspect
import tempfile
# import shutil
from licface import CustomRichHelpFormatter
# from textwrap import wrap
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.align import Align
    from rich.layout import Layout
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich import box
    from rich.traceback import install
    from rich.pager import Pager
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to basic console if Rich is not available
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

class EnhancedPyHelp:
    """Enhanced Python Help Tool with Rich library support and pager functionality"""
    
    def __init__(self):
        self.version = "2.2.0"
        self.author = "Enhanced PyHelp with Rich and Pager"
        self.python_paths = []
        self.cache = {}
        self.use_pager = True
        self.pager_command = None
        
        # Initialize Rich console
        self.console = Console()
        
        # Install rich traceback handler for better error display
        if RICH_AVAILABLE:
            install()
        
        # Check if Rich is available
        if not RICH_AVAILABLE:
            self.console.print("⚠️  Rich library not found. Install with: pip install rich")
            self.console.print("Falling back to basic output...\n")
            
        # Detect available pager
        self.detect_pager()
    
    def detect_pager(self):
        """Detect available pager command"""
        pagers = ['less', 'more', 'most', 'pg']
        
        # Check environment variable first
        env_pager = os.environ.get('PAGER')
        if env_pager:
            self.pager_command = env_pager
            return
            
        # Check for available pagers
        for pager in pagers:
            try:
                result = subprocess.run(['which', pager], capture_output=True, text=True)
                if result.returncode == 0:
                    self.pager_command = pager
                    return
            except:
                pass
                
        # Windows fallback
        if os.name == 'nt':
            self.pager_command = 'more'
        else:
            # Final fallback - disable pager
            self.use_pager = False
    
    def get_terminal_height(self) -> int:
        """Get terminal height"""
        try:
            return os.get_terminal_size().lines
        except:
            return 24  # Default height
    
    def should_use_pager(self, content: str) -> bool:
        """Determine if content should be paged"""
        if not self.use_pager or not self.pager_command:
            return False
            
        lines = content.count('\n')
        terminal_height = self.get_terminal_height()
        
        # Use pager if content is longer than 75% of terminal height
        return lines > (terminal_height * 0.75)
    
    def display_with_pager(self, content: str, title: str = "Output"):
        """Display content using system pager"""
        if not self.should_use_pager(content):
            # Just print normally
            self.console.print(content)
            return
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Use pager to display
            if self.pager_command == 'less':
                # less with nice options
                cmd = ['less', '-R', '-S', '-F', '-X', temp_file_path]
            else:
                cmd = [self.pager_command, temp_file_path]
                
            subprocess.run(cmd)
            
        except Exception as e:
            self.console.print(f"[yellow]Pager failed ({e}), showing directly:[/yellow]")
            self.console.print(content)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def display_with_rich_pager(self, renderable, title: str = "Output"):
        """Display Rich renderable with pager support"""
        if not RICH_AVAILABLE:
            print(str(renderable))
            return
            
        # Render to string first to check length
        with self.console.capture() as capture:
            self.console.print(renderable)
        content = capture.get()
        
        if self.should_use_pager(content):
            # Ask user preference
            use_pager = Confirm.ask(
                f"[yellow]Content is long ({content.count(chr(10))} lines). Use pager?[/yellow]",
                default=True
            )
            
            if use_pager:
                self.display_with_pager(content, title)
                return
        
        # Display normally
        self.console.print(renderable)

    def get_version(self):
        """
        Get the version.
        Version is taken from the __version__.py file if it exists.
        The content of __version__.py should be:
        version = "0.33"
        """
        try:
            version_file = Path(__file__).parent / "__version__.py"
            if version_file.is_file():
                with open(version_file, "r") as f:
                    for line in f:
                        if line.strip().startswith("version"):
                            parts = line.split("=")
                            if len(parts) == 2:
                                return parts[1].strip().strip('"').strip("'")
        except Exception as e:
            if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
                self.console.log(Syntax(traceback.format_exc(), 'pytb'))
            else:
                self.console.log(f"[white on red]{e}[/]")

        return self.version

    def get_width(self) -> int:
        """Get terminal width for code display"""
        try:
            columns = os.get_terminal_size()[0]
            return min(columns - 4, 120)  # Leave some margin and cap at 120
        except:
            return 100  # Default width
    
    def print_header(self) -> None:
        """Print beautiful application header using Rich"""
        if not RICH_AVAILABLE:
            print("Enhanced Python Help Tool v" + self.get_version())
            print("=" * 60)
            return
            
        # Create a beautiful header panel
        header_text = Text()
        header_text.append("🐍 Enhanced Python Help Tool ", style="bold cyan")
        header_text.append(f"v{self.version}", style="bold yellow")
        header_text.append(" 🚀", style="bold cyan")
        
        description = Text()
        description.append("Beautiful terminal help for Python modules with pager support", style="italic bright_blue")
        
        # Show pager info
        pager_info = Text()
        if self.use_pager and self.pager_command:
            pager_info.append(f"📖 Pager: {self.pager_command}", style="dim green")
        else:
            pager_info.append("📖 Pager: disabled", style="dim red")
        
        header_content = header_text + "\n" + description + "\n" + pager_info
        
        header_panel = Panel(
            Align.center(header_content),
            style="bold blue",
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def show_usage(self) -> None:
        """Show usage information with Rich formatting"""
        if not RICH_AVAILABLE:
            filename = Path(sys.argv[0]).name
            print(f"Usage: {filename} [options] [module/module.function/module.class]")
            print(f"Example: {filename} os.path")
            print(f"Example: {filename} --no-pager json.loads")
            return
            
        filename = Path(sys.argv[0]).name
        
        # Create usage table
        usage_table = Table(show_header=False, box=box.SIMPLE)
        usage_table.add_column("Command", style="bold green")
        usage_table.add_column("Description", style="bright_blue")
        
        usage_table.add_row(f"{filename} os.path", "Show help for os.path module")
        usage_table.add_row(f"{filename} json.loads", "Show help for json.loads function")
        usage_table.add_row(f"{filename} --no-pager requests", "Show help without pager")
        usage_table.add_row(f"{filename} -s collections.Counter", "Show source code")
        usage_table.add_row(f"{filename} --pager less requests", "Use specific pager")
        
        usage_panel = Panel(
            usage_table,
            title="📚 Usage Examples",
            title_align="left",
            style="bright_yellow"
        )
        
        self.display_with_rich_pager(usage_panel, "Usage")
    
    def find_python_executables(self) -> List[str]:
        """Find all Python executables with Rich progress bar"""
        if self.python_paths:
            return self.python_paths
            
        if not RICH_AVAILABLE:
            self.console.print("Searching for Python interpreters...")
            # Basic search without progress bar
            executables = []
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            search_names = ['python', 'python3', 'python.exe', 'python3.exe']
            
            for directory in path_dirs:
                if not directory or not os.path.isdir(directory):
                    continue
                for name in search_names:
                    exe_path = os.path.join(directory, name)
                    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                        if exe_path not in executables:
                            executables.append(exe_path)
            
            if not executables:
                executables.append(sys.executable)
            
            self.python_paths = executables
            return executables
        
        executables = []
        search_names = ['python', 'python3', 'python.exe', 'python3.exe']
        
        # Get PATH directories
        path_dirs = [d for d in os.environ.get('PATH', '').split(os.pathsep) if d and os.path.isdir(d)]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            search_task = progress.add_task("🔍 Scanning PATH directories...", total=len(path_dirs))
            
            for directory in path_dirs:
                for name in search_names:
                    exe_path = os.path.join(directory, name)
                    if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                        if exe_path not in executables:
                            executables.append(exe_path)
                progress.update(search_task, advance=1)
        
        # Check common locations
        common_paths = [
            '/usr/bin', '/usr/local/bin',
            'C:\\Python*', 'C:\\Program Files\\Python*',
        ]
        
        for path_pattern in common_paths:
            for path in Path().glob(path_pattern):
                if path.is_dir():
                    for name in search_names:
                        exe_path = path / name
                        if exe_path.is_file() and str(exe_path) not in executables:
                            executables.append(str(exe_path))
        
        # Use current Python if no others found
        if not executables:
            executables.append(sys.executable)
            
        self.python_paths = executables
        
        # Show results in a nice panel
        result_text = Text()
        result_text.append("✅ Found ", style="bold green")
        result_text.append(f"{len(executables)}", style="bold yellow")
        result_text.append(" Python interpreter(s)", style="bold green")
        
        self.console.print(Panel(result_text, style="green"))
        
        return executables
    
    def test_python_executable(self, python_path: str) -> tuple[bool, str]:
        """Test if Python executable is working and return version info"""
        try:
            result = subprocess.run([python_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version
            return False, result.stderr.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, str(e)
    
    def get_working_python(self) -> Optional[str]:
        """Get the first working Python executable with Rich display"""
        executables = self.find_python_executables()
        
        if not RICH_AVAILABLE:
            for python_path in executables:
                working, version = self.test_python_executable(python_path)
                if working:
                    self.console.print(f"Using: {python_path} ({version})")
                    return python_path
            return None
        
        # Create a table to show Python interpreters
        python_table = Table(title="🐍 Available Python Interpreters", box=box.ROUNDED)
        python_table.add_column("Path", style="bright_cyan")
        python_table.add_column("Version", style="bright_green")
        python_table.add_column("Status", style="bold")
        
        working_python = None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("🧪 Testing Python interpreters...", total=len(executables))
            
            for python_path in executables:
                working, version_or_error = self.test_python_executable(python_path)
                
                if working:
                    python_table.add_row(
                        python_path,
                        version_or_error,
                        "✅ Working"
                    )
                    if working_python is None:
                        working_python = python_path
                else:
                    python_table.add_row(
                        python_path,
                        version_or_error,
                        "❌ Failed"
                    )
                progress.update(task, advance=1)
        
        self.display_with_rich_pager(python_table, "Python Interpreters")
        
        if working_python:
            selected_text = Text()
            selected_text.append("🎯 Selected: ", style="bold yellow")
            selected_text.append(working_python, style="bold cyan")
            self.console.print(Panel(selected_text, style="yellow"))
        
        return working_python
    
    def get_source(self, source: Any) -> bool:
        """Get and display source code with Rich syntax highlighting and pager"""
        if not RICH_AVAILABLE:
            try:
                source_code = inspect.getsource(source)
                print("Source Code:")
                print("-" * 50)
                if self.should_use_pager(source_code):
                    self.display_with_pager(source_code, "Source Code")
                else:
                    print(source_code)
                print("-" * 50)
                return True
            except Exception as e:
                print(f"Error getting source: {e}")
                return False
        
        try:
            # Get source code
            source_code = inspect.getsource(source)
            
            # Display with Rich syntax highlighting
            syntax = Syntax(
                source_code, 
                "python", 
                theme='fruity', 
                line_numbers=True, 
                tab_size=2, 
                code_width=self.get_width(), 
                word_wrap=True
            )
            
            # Create a panel for the source code
            source_panel = Panel(
                syntax,
                title=f"📄 Source Code - {getattr(source, '__name__', 'Unknown')}",
                title_align="left",
                style="bright_green",
                box=box.ROUNDED
            )
            
            # Use pager for source code
            self.display_with_rich_pager(source_panel, "Source Code")
            
            # Show terminal width info
            width_info = Text()
            width_info.append("📏 Terminal Width: ", style="bold")
            width_info.append(f"{self.get_width()}", style="bold yellow")
            width_info.append(" characters", style="bold")
            
            self.console.print(Panel(width_info, style="dim"))
            
            return True
            
        except Exception as e:
            if sys.version_info.major == 2:
                # Fallback for Python 2
                return self.get_source_python2(source)
            else:
                error_text = Text()
                error_text.append("❌ Error getting source: ", style="bold red")
                error_text.append(str(e), style="red")
                self.console.print(Panel(error_text, style="red"))
                return False
    
    def get_source_python2(self, source: Any) -> bool:
        """Fallback method for Python 2"""
        try:
            module_name = getattr(source, '__module__', getattr(source, '__name__', 'unknown'))
            width = self.get_width()
            
            # Try with module
            cmd = f"""python3 -c "import {module_name};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({module_name}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={width}))" """
            
            result = os.system(cmd)
            if result == 0:
                return True
            
            # Try with object name
            obj_name = getattr(source, '__name__', 'unknown')
            cmd = f"""python3 -c "import {obj_name};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({obj_name}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={width}))" """
            
            result = os.system(cmd)
            return result == 0
            
        except Exception as e:
            self.console.print(f"❌ Error in Python 2 fallback: {e}")
            return False
    
    def import_module_safely(self, module_name: str) -> tuple[Any, Optional[str]]:
        """Safely import a module and return (module, error)"""
        try:
            if '.' in module_name:
                # Handle submodules
                parts = module_name.split('.')
                module = importlib.import_module(parts[0])
                obj = module
                for part in parts[1:]:
                    obj = getattr(obj, part)
                return obj, None
            else:
                module = importlib.import_module(module_name)
                return module, None
        except Exception as e:
            return None, str(e)
    
    def format_help_with_rich(self, obj: Any) -> None:
        """Format and display help output using Rich with pager support"""
        if not RICH_AVAILABLE:
            # Capture help output and use pager if needed
            help_output = io.StringIO()
            with redirect_stdout(help_output):
                help(obj)
            help_text = help_output.getvalue()
            
            if self.should_use_pager(help_text):
                self.display_with_pager(help_text, "Help Documentation")
            else:
                help(obj)
            return
            
        # Capture help output
        help_output = io.StringIO()
        with redirect_stdout(help_output):
            help(obj)
        
        help_text = help_output.getvalue()
        
        # Create syntax highlighted help
        help_panel = Panel(
            Syntax(help_text, "restructuredtext", theme='fruity', word_wrap=True, code_width=os.get_terminal_size()[0] - 5),
            title="📖 Help Documentation",
            title_align="left",
            style="bright_blue",
            box=box.ROUNDED,
        )
        
        # Use pager for help
        self.display_with_rich_pager(help_panel, "Help Documentation")
    
    def show_attributes_with_rich(self, obj: Any) -> None:
        """Show object attributes in a beautiful Rich table with pager support"""
        if not RICH_AVAILABLE:
            attrs_text = "Attributes: " + ", ".join(dir(obj))
            if self.should_use_pager(attrs_text):
                self.display_with_pager(attrs_text, "Attributes")
            else:
                print("Attributes:", dir(obj))
            return
            
        attributes = dir(obj)
        public_attrs = [attr for attr in attributes if not attr.startswith('_')]
        private_attrs = [attr for attr in attributes if attr.startswith('_')]
        
        # Create attributes table
        attr_table = Table(title="🔧 Attributes & Methods", box=box.ROUNDED)
        attr_table.add_column("Name", style="bright_cyan")
        attr_table.add_column("Type", style="bright_yellow")
        attr_table.add_column("Visibility", style="bright_green")
        
        # Add public attributes
        for attr in public_attrs[:20]:  # Limit to first 20 for readability
            try:
                attr_obj = getattr(obj, attr)
                attr_type = type(attr_obj).__name__
                attr_table.add_row(attr, attr_type, "Public")
            except:
                attr_table.add_row(attr, "Unknown", "Public")
        
        # Add some private attributes
        for attr in private_attrs[:10]:  # Limit to first 10
            try:
                attr_obj = getattr(obj, attr)
                attr_type = type(attr_obj).__name__
                attr_table.add_row(attr, attr_type, "Private")
            except:
                attr_table.add_row(attr, "Unknown", "Private")
        
        self.display_with_rich_pager(attr_table, "Attributes")
        
        # Show summary
        summary_text = Text()
        summary_text.append(f"📊 Total: ", style="bold")
        summary_text.append(f"{len(public_attrs)}", style="bold green")
        summary_text.append(" public, ", style="bold")
        summary_text.append(f"{len(private_attrs)}", style="bold yellow")
        summary_text.append(" private attributes", style="bold")
        
        if len(public_attrs) > 20:
            summary_text.append(f" (showing first 20 public)", style="dim")
        if len(private_attrs) > 10:
            summary_text.append(f" (showing first 10 private)", style="dim")
        
        self.console.print(Panel(summary_text, style="bright_magenta"))

    def show_module_help(self, module_name: str, show_source: bool = False) -> bool:
        """Show help for a specific module with Rich formatting and pager support"""
        if not RICH_AVAILABLE:
            # Fallback to basic help
            try:
                obj, error = self.import_module_safely(module_name)
                if obj:
                    if show_source:
                        self.get_source(obj)
                    else:
                        help_output = io.StringIO()
                        with redirect_stdout(help_output):
                            help(obj)
                        help_text = help_output.getvalue()
                        
                        if self.should_use_pager(help_text):
                            self.display_with_pager(help_text + "\n\nAttributes: " + str(dir(obj)), "Help")
                        else:
                            help(obj)
                            print("\nAttributes:", dir(obj))
                    return True
                else:
                    print(f"Error: {error}")
                    return False
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        # Show loading spinner
        with self.console.status(f"[bold green]Loading module: {module_name}...") as status:
            obj, error = self.import_module_safely(module_name)
        
        if obj is not None:
            # Success message
            success_text = Text()
            success_text.append("✅ Module loaded successfully: ", style="bold green")
            success_text.append(module_name, style="bold cyan")
            self.console.print(Panel(success_text, style="green"))
            
            if show_source:
                # Show source code instead of help
                return self.get_source(obj)
            else:
                # Show help documentation
                self.format_help_with_rich(obj)
                
                # Show attributes
                self.show_attributes_with_rich(obj)
            
            return True
        else:
            # Show error and try subprocess method
            error_text = Text()
            error_text.append("⚠️  Direct import failed: ", style="bold yellow")
            error_text.append(error, style="red")
            self.console.print(Panel(error_text, style="yellow"))
            
            if show_source:
                self.console.print("❌ Cannot show source code for failed imports")
                return False
            else:
                self.console.print("🔄 Trying external Python interpreter...")
                return self.show_module_help_subprocess(module_name)
    
    def show_module_help_subprocess(self, module_name: str) -> bool:
        """Show help using subprocess with Rich progress and pager support"""
        python_path = self.get_working_python()
        
        if not python_path:
            if RICH_AVAILABLE:
                self.console.print(Panel("❌ No working Python interpreter found!", style="bold red"))
            else:
                self.console.print("❌ No working Python interpreter found!")
            return False
        
        # Prepare the command
        if '.' in module_name:
            parts = module_name.split('.')
            cmd = f"import {parts[0]}; help({module_name}); print('\\n' + '='*50 + '\\nATTRIBUTES:\\n' + '='*50); print(dir({module_name}))"
        else:
            builtins = ['dict', 'list', 'str', 'int', 'float', 'bool', 'tuple', 'set']
            if module_name in builtins:
                cmd = f"help({module_name}); print('\\n' + '='*50 + '\\nATTRIBUTES:\\n' + '='*50); print(dir({module_name}))"
            else:
                cmd = f"import {module_name}; help({module_name}); print('\\n' + '='*50 + '\\nATTRIBUTES:\\n' + '='*50); print(dir({module_name}))"
        
        try:
            if RICH_AVAILABLE:
                with self.console.status("[bold blue]Executing help command...") as status:
                    result = subprocess.run([python_path, '-c', cmd], 
                                          capture_output=True, text=True, timeout=30)
            else:
                self.console.print("Executing help command...")
                result = subprocess.run([python_path, '-c', cmd], 
                                      capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if RICH_AVAILABLE:
                    # Show output in a nice panel with pager
                    output_panel = Panel(
                        result.stdout,
                        title="📋 Help Output",
                        title_align="left",
                        style="bright_green"
                    )
                    self.display_with_rich_pager(output_panel, "Help Output")
                else:
                    if self.should_use_pager(result.stdout):
                        self.display_with_pager(result.stdout, "Help Output")
                    else:
                        self.console.print("Help Output:")
                        self.console.print(result.stdout)
                return True
            else:
                if RICH_AVAILABLE:
                    error_panel = Panel(
                        result.stderr,
                        title="❌ Error",
                        title_align="left",
                        style="bold red"
                    )
                    self.console.print(error_panel)
                else:
                    self.console.print("Error:", result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            if RICH_AVAILABLE:
                self.console.print(Panel("⏱️ Help command timed out!", style="bold red"))
            else:
                self.console.print("⏱️ Help command timed out!")
            return False
        except Exception as e:
            if RICH_AVAILABLE:
                self.console.print(Panel(f"💥 Unexpected error: {str(e)}", style="bold red"))
            else:
                self.console.print(f"💥 Unexpected error: {str(e)}")
            return False
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            prog='pyhelp/helpman',
            description='🐍 Enhanced Python Help Tool with Rich formatting and pager support',
            formatter_class=CustomRichHelpFormatter,
            epilog="""
Examples:
  pyhelp os.path                    # Show help for os.path module
  pyhelp json.loads                 # Show help for json.loads function
  pyhelp -s requests.get            # Show source code for requests.get
  pyhelp --source collections.Counter  # Show source code for Counter class
  pyhelp --no-pager requests       # Disable pager for this session
  pyhelp --pager less os.path      # Use specific pager command
            """
        )
        
        parser.add_argument(
            'module',
            nargs='?',
            help='Module, function, or class to get help for (e.g., os.path, json.loads)'
        )
        
        parser.add_argument(
            '-s', '--source',
            action='store_true',
            help='Show source code instead of help documentation'
        )
        
        parser.add_argument(
            '--no-pager',
            action='store_true',
            help='Disable pager and show output directly'
        )
        
        parser.add_argument(
            '--pager',
            type=str,
            help='Specify pager command to use (e.g., less, more, most)'
        )
        
        parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'pyhelp v{self.get_version()}'
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> None:
        """Main application entry point with argparse and pager support"""
        parser = self.create_argument_parser()
        
        if len(sys.argv) == 1:
            self.print_header()
            self.show_usage()
            return
        
        # Parse arguments
        try:
            parsed_args = parser.parse_args(args)
        except SystemExit:
            return
        
        # Handle pager options
        if parsed_args.no_pager:
            self.use_pager = False
        
        if parsed_args.pager:
            self.pager_command = parsed_args.pager
            self.use_pager = True
        
        # Check if module is provided
        if not parsed_args.module:
            self.print_header()
            self.show_usage()
            return
        
        self.print_header()
        
        module_name = parsed_args.module
        show_source = parsed_args.source
        
        # Show module info
        if RICH_AVAILABLE:
            action = "source code" if show_source else "help"
            pager_status = "enabled" if self.use_pager else "disabled"
            
            module_info = Text()
            module_info.append("🎯 Target: ", style="bold")
            module_info.append(module_name, style="bold cyan")
            module_info.append(f" ({action})", style="bold yellow")
            module_info.append(f" | Pager: {pager_status}", style="dim")
            
            self.console.print(Panel(module_info, style="blue"))
        else:
            action = "source code" if show_source else "help"
            pager_status = "enabled" if self.use_pager else "disabled"
            self.console.print(f"🎯 Target: {module_name} ({action}) | Pager: {pager_status}")
        
        start_time = time.time()
        success = self.show_module_help(module_name, show_source)
        end_time = time.time()
        
        # Show completion status
        if RICH_AVAILABLE:
            if success:
                completion_text = Text()
                completion_text.append("🎉 Operation completed in ", style="bold green")
                completion_text.append(f"{end_time - start_time:.2f}s", style="bold yellow")
                self.console.print(Panel(completion_text, style="green"))
            else:
                failure_text = Text()
                failure_text.append("❌ Failed to complete operation", style="bold red")
                failure_text.append("\n💡 Please check the module name and try again", style="yellow")
                self.console.print(Panel(failure_text, style="red"))
        else:
            if success:
                self.console.print(f"🎉 Operation completed in {end_time - start_time:.2f}s")
            else:
                self.console.print("❌ Failed to complete operation")

def main():
    """Main function with Rich error handling"""
    try:
        app = EnhancedPyHelp()
        app.run()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console = Console()
            console.print(Panel("⚠️ Operation cancelled by user", style="bold yellow"))
        else:
            print("⚠️ Operation cancelled by user")
    except Exception as e:
        if RICH_AVAILABLE:
            console = Console()
            console.print(Panel(f"💥 Unexpected error: {str(e)}", style="bold red"))
        else:
            print(f"💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()