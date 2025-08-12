from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm, Prompt
import questionary

from .config import Config, ConfigManager
from .providers import APIClient
from .clipboard import ClipboardManager
from .language_detector import LanguageDetector
from .version import UpdateChecker, __version__


class PromptEnhancerCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.clipboard_manager = ClipboardManager()
        self.language_detector = LanguageDetector()
        self.update_checker = UpdateChecker()
        self.config = self.config_manager.load_config()
        
        self.style = Style.from_dict({
            'title': '#00aa00 bold',
            'subtitle': '#888888',
            'prompt': '#0088ff bold',
            'enhanced': '#00ff88',
            'error': '#ff0088 bold',
        })
        
        # Enhancement styles
        self.enhancement_styles = {
            "gentle": {
                "name": "Gentle",
                "color": "#90EE90",
                "description": "Makes minimal alterations, focusing on minor grammatical corrections",
                "prompt": "Make minimal changes to this prompt. Focus only on minor grammatical corrections and subtle rephrasing without changing the core intent or structure. Preserve as much of the user's original phrasing as possible. Return ONLY the enhanced prompt."
            },
            "enhanced": {
                "name": "Enhanced",
                "color": "#FFA500",
                "description": "Strikes a balance with moderate improvements and added clarity",
                "prompt": "Apply moderate improvements to this prompt. Use better word choice, minor structural adjustments, and add some useful context or clarity without a complete overhaul. Enhance readability and professionalism while maintaining a clear connection to the original input. Return ONLY the enhanced prompt."
            },
            "structured": {
                "name": "Structured", 
                "color": "#4169E1",
                "description": "Extensively reformats with detailed elaboration and professional language",
                "prompt": "Extensively reformat and enhance this prompt. Apply significant restructuring, detailed elaboration, add context and formatting specifications (e.g., code block formatting, type hints). Use professional language and aim for a highly polished and articulate output. Return ONLY the enhanced prompt."
            },
            "creative": {
                "name": "Creative",
                "color": "#FF69B4", 
                "description": "Adds creative flair while preserving the core request",
                "prompt": "Enhance this prompt by keeping the user's core request and intent unchanged, but add creative elements to make it more engaging. You can enrich it with vivid examples, interesting analogies, compelling details, or imaginative context that supports the original goal. Feel free to be creative with language and add flair, but always preserve what the user is fundamentally asking for. Return ONLY the enhanced prompt."
            }
        }
        
        # Create command and file completer
        from prompt_toolkit.completion import Completer, Completion
        import os
        import glob
        
        class CommandAndFileCompleter(Completer):
            def __init__(self):
                self.commands = ['/help', '/style', '/quit', '/version']
            
            def get_completions(self, document, complete_event):
                text_before_cursor = document.text_before_cursor
                
                # Complete commands if line starts with /
                if text_before_cursor.startswith('/'):
                    for command in self.commands:
                        if command.startswith(text_before_cursor):
                            yield Completion(
                                command,
                                start_position=-len(text_before_cursor)
                            )
                
                # Complete files if @ is in the text - only when environment is detected
                elif '@' in text_before_cursor:
                    # Check if we're in a development environment before showing file suggestions
                    has_dev_files = any(os.path.exists(f) for f in [
                        'requirements.txt', 'package.json', 'Cargo.toml', 'pom.xml', 
                        'setup.py', 'pyproject.toml', '.gitignore', 'Makefile'
                    ])
                    
                    if not has_dev_files:
                        return  # Don't show file suggestions outside development environments
                    
                    # Find the last @ position
                    at_pos = text_before_cursor.rfind('@')
                    file_partial = text_before_cursor[at_pos + 1:]
                    
                    # Get file list for suggestions
                    try:
                        all_files = []
                        file_count = 0
                        max_files = 200  # Increased limit for file processing
                        max_depth = 4    # Allow deeper directory traversal
                        
                        for root, dirs, files in os.walk('.'):
                            # Calculate current depth
                            depth = root.replace('.', '').count(os.sep)
                            if depth >= max_depth:
                                dirs.clear()  # Don't go deeper
                                continue
                                
                            # Skip hidden directories and common build/cache directories
                            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist', '.pytest_cache', 'htmlcov']]
                            
                            for file in files:
                                if file_count >= max_files:
                                    break
                                    
                                # Skip hidden files and certain file types
                                if (not file.startswith('.') and 
                                    not file.endswith(('.pyc', '.pyo', '.log', '.tmp', '.cache')) and
                                    file not in ['__pycache__']):
                                    
                                    # Get relative path
                                    rel_path = os.path.relpath(os.path.join(root, file), '.')
                                    if rel_path.startswith('./'):
                                        rel_path = rel_path[2:]
                                    all_files.append(rel_path)
                                    file_count += 1
                            
                            if file_count >= max_files:
                                break
                        
                        # Prioritize certain file types for better relevance
                        def get_file_priority(file_path):
                            name = file_path.lower()
                            # Higher priority (lower number) for common development files
                            if name.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt', '.json', '.yml', '.yaml')):
                                return 1
                            elif name.endswith(('.xml', '.cfg', '.ini', '.conf', '.toml')):
                                return 2
                            else:
                                return 3
                        
                        # Filter files based on partial input
                        if file_partial:
                            # Match by filename or path
                            matching_files = []
                            for file_path in all_files:
                                filename = os.path.basename(file_path)
                                # Match by filename or full path
                                if (file_partial.lower() in filename.lower() or 
                                    file_partial.lower() in file_path.lower()):
                                    matching_files.append(file_path)
                            
                            # Sort by relevance: exact filename matches first, then priority, then alphabetical
                            matching_files.sort(key=lambda f: (
                                not os.path.basename(f).lower().startswith(file_partial.lower()),
                                not f.lower().startswith(file_partial.lower()),
                                get_file_priority(f),
                                f
                            ))
                        else:
                            # No partial input, show prioritized files
                            all_files.sort(key=lambda f: (get_file_priority(f), f))
                            matching_files = all_files[:30]  # Show up to 30 files when no filter
                        
                        # Yield completions - show up to 30 suggestions
                        for file_path in matching_files[:30]:  # Increased to 30 suggestions max
                            yield Completion(
                                file_path,
                                start_position=-len(file_partial),
                                display=f"@{file_path}"
                            )
                    
                    except Exception:
                        pass  # Silently ignore file system errors
        
        completer = CommandAndFileCompleter()
        
        # Create key bindings for custom Enter behavior
        bindings = KeyBindings()
        
        @bindings.add('enter')
        def _(event):
            """Submit on Enter"""
            event.app.exit(result=event.app.current_buffer.text)
        
        @bindings.add('escape', 'enter')  # Alt+Enter
        def _(event):
            """New line on Alt+Enter"""
            event.current_buffer.insert_text('\n')
        
        # Create prompt session with multiline support for main prompts
        self.prompt_session = PromptSession(
            multiline=True,
            completer=completer,
            key_bindings=bindings
        )
        
        # Create single-line prompt session for configuration inputs
        self.config_prompt_session = PromptSession(
            multiline=False,
            completer=None
        )
    
    def _extract_file_references(self, prompt: str) -> list:
        """Extract file references (@filepath) from prompt text"""
        import re
        
        # Match @filepath patterns - handle both @filename and @path/to/file
        pattern = r'@([^\s@]+(?:/[^\s@]*)*)'
        matches = re.findall(pattern, prompt)
        
        # Filter out duplicates and validate files exist
        file_paths = []
        for match in matches:
            if os.path.isfile(match):
                file_paths.append(match)
        
        return file_paths
    
    def _read_file_content(self, file_path: str) -> str:
        """Read and return file content with proper encoding handling"""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            # Fall back to other encodings if UTF-8 fails
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, read as binary and decode with errors ignored
            with open(file_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
            return content
        except Exception as e:
            return f"[Error reading file {file_path}: {str(e)}]"
    
    def _integrate_file_context(self, prompt: str) -> str:
        """Integrate file contents into the prompt context"""
        file_references = self._extract_file_references(prompt)
        
        if not file_references:
            return prompt
        
        # Build context from referenced files
        file_contexts = []
        for file_path in file_references:
            content = self._read_file_content(file_path)
            
            # Truncate very large files to avoid token limits
            if len(content) > 8000:  # Reasonable limit for context
                content = content[:8000] + "\n... [File truncated for brevity]"
            
            file_context = f"--- File: {file_path} ---\n{content}\n--- End of {file_path} ---\n"
            file_contexts.append(file_context)
        
        # Integrate file contexts with the original prompt
        if file_contexts:
            context_section = "\n".join(file_contexts)
            enhanced_prompt = f"{prompt}\n\n[File Context for Reference:]\n{context_section}"
            return enhanced_prompt
        
        return prompt
    
    async def run(self):
        """Main application loop"""
        try:
            # Check if this is first run (no config file)
            if not self.config_manager.config_file.exists():
                self._show_initial_setup()
                if not await self._configure_provider():
                    return
            
            self._show_welcome()
            
            while True:
                try:
                    # Check if configured
                    if not self.config_manager.is_configured(self.config):
                        self._show_configuration_needed()
                        if not await self._configure_provider():
                            break
                    
                    # Get user prompt
                    user_prompt = await self._get_user_prompt()
                    if user_prompt is None:
                        break
                    if not user_prompt:
                        continue
                    
                    # Enhance prompt with streaming
                    enhanced_prompt = await self._enhance_prompt_stream(user_prompt)
                    if not enhanced_prompt:
                        continue
                    
                    # Ask to copy to clipboard
                    if Confirm.ask("[yellow]Copy enhanced prompt to clipboard?[/yellow]", default=True):
                        if self.clipboard_manager.copy_to_clipboard(enhanced_prompt):
                            self.console.print("[green]✓ Copied to clipboard![/green]")
                        else:
                            self.console.print("[red]✗ Failed to copy to clipboard[/red]")
                    
                    self.console.print("\n" + "─" * 50 + "\n")
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.console.print(f"[red]Error: {e}[/red]")
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Goodbye![/yellow]")
    
    def _show_welcome(self):
        """Display welcome message"""
        title = Text("PMPT CLI", style="bold cyan")
        
        current_style_name = self.enhancement_styles[self.config.current_style]['name']
        detected_language = self.language_detector.detect_language()
        
        if self.config.provider:
            subtitle = f"Provider: {self.config.provider} | Model: {self.config.get_model()} | Style: {current_style_name}"
        else:
            subtitle = f"Base URL: {self.config.get_base_url()} | Model: {self.config.get_model()} | Style: {current_style_name}"
        
        if detected_language:
            subtitle += f" | Environment: {detected_language.title()}"
        
        panel = Panel(
            f"[bold cyan]{title}[/bold cyan]\n"
            f"[dim]{subtitle}[/dim]\n\n"
            "[bold]How to use:[/bold]\n"
            "• Enter your prompt and get an enhanced version\n"
            "• [yellow]Enter[/yellow] - Process prompt\n"
            "• [yellow]Alt+Enter[/yellow] - New line\n\n"
            "[bold]Available commands:[/bold]\n"
            "• [green]/help[/green] - Show detailed help\n"
            "• [green]/style[/green] - Change enhancement style\n"
            "• [green]/version[/green] - Show version info\n"
            "• [green]/quit[/green] - Exit application\n\n"
            "[bold]External commands:[/bold]\n"
            "• [cyan]pmpt config[/cyan] - Configure settings\n"
            "• [cyan]pmpt update[/cyan] - Check for updates",
            title="🚀 Welcome",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def _show_initial_setup(self):
        """Show initial setup welcome message"""
        panel = Panel(
            "[bold cyan]Welcome to PMPT CLI![/bold cyan]\n\n"
            "This is your first time running the tool.\n"
            "Let's set up your AI provider configuration.\n\n"
            "[dim]You'll need to provide:[/dim]\n"
            "• API key for your chosen provider\n"
            "• Provider name (openai, anthropic, openrouter) or custom base URL\n" 
            "• Model name (e.g., gpt-4o, claude-3-5-sonnet-20241022)",
            title="Initial Setup",
            border_style="green"
        )
        self.console.print(panel)
        self.console.print()
    
    def _show_configuration_needed(self):
        """Show configuration needed message"""
        self.console.print("[yellow]⚠ Configuration incomplete[/yellow]")
    
    async def _configure_provider(self) -> bool:
        """Configure API settings"""
        try:
            self.console.print("[bold]Configuration:[/bold]")
            
            # Step 1: Choose provider with menu
            self.console.print("\n[bold cyan]Step 1: Choose Provider[/bold cyan]")
            
            provider_choice = await questionary.select(
                "Select your AI provider:",
                choices=[
                    questionary.Choice("OpenAI", value="openai"),
                    questionary.Choice("Anthropic (Claude)", value="anthropic"), 
                    questionary.Choice("OpenRouter", value="openrouter"),
                    questionary.Choice("Custom (enter base URL)", value="custom")
                ],
                style=questionary.Style([
                    ('highlighted', 'fg:#00aa00 bold'),
                    ('pointer', 'fg:#00aa00 bold'),
                    ('question', 'bold')
                ])
            ).ask_async()
            
            if not provider_choice:
                self.console.print("[yellow]Configuration cancelled[/yellow]")
                return False
            
            # Configure provider or custom URL
            if provider_choice == "custom":
                self.console.print("\n[bold cyan]Custom Provider Configuration[/bold cyan]")
                base_url = await self.config_prompt_session.prompt_async("Enter base URL: ", is_password=False)
                base_url = base_url.strip()
                
                # Remove /chat/completions if user accidentally included it
                if base_url.endswith('/chat/completions'):
                    base_url = base_url[:-len('/chat/completions')]
                    self.console.print("[yellow]ℹ Automatically removed /chat/completions from URL[/yellow]")
                
                if not base_url:
                    self.console.print("[red]Base URL is required[/red]")
                    return False
                
                self.config.provider = None
                self.config.base_url = base_url
                self.console.print(f"[green]✓ Using custom URL: {base_url}[/green]")
            else:
                self.config.provider = provider_choice
                self.config.base_url = None
                self.console.print(f"[green]✓ Using {provider_choice} provider[/green]")
            
            # Step 2: Get API key
            self.console.print("\n[bold cyan]Step 2: API Key[/bold cyan]")
            api_key = await self.config_prompt_session.prompt_async("Enter your API key: ", is_password=True)
            api_key = api_key.strip()
            if not api_key:
                self.console.print("[red]API key is required[/red]")
                return False
            
            # Step 3: Get model
            self.console.print("\n[bold cyan]Step 3: Model Name[/bold cyan]")
            
            model = await self.config_prompt_session.prompt_async("Enter model name: ", is_password=False)
            model = model.strip()
            if not model:
                self.console.print("[red]Model is required[/red]")
                return False
            
            # Save configuration
            self.config.api_key = api_key
            self.config.model = model
            self.config_manager.save_config(self.config)
            
            self.console.print(f"\n[green]✓ Configuration saved successfully![/green]")
            self.console.print(f"Provider: {self.config.provider or 'Custom'}")
            self.console.print(f"Base URL: {self.config.get_base_url()}")
            self.console.print(f"Model: {self.config.model}")
            
            return True
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Configuration cancelled[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]Configuration error: {e}[/red]")
            return False
    
    async def _select_style(self):
        """Show style selection menu"""
        try:
            style_choice = await questionary.select(
                "Select enhancement style:",
                choices=[
                    questionary.Choice(f"{style_info['name']} - {style_info['description']}", value=style_key)
                    for style_key, style_info in self.enhancement_styles.items()
                ],
                default=self.config.current_style,
                style=questionary.Style([
                    ('highlighted', 'fg:#00aa00 bold'),
                    ('pointer', 'fg:#00aa00 bold'),
                    ('question', 'bold')
                ])
            ).ask_async()
            
            if style_choice:
                self.config.current_style = style_choice
                self.config_manager.save_config(self.config)
                style_name = self.enhancement_styles[style_choice]['name']
                self.console.print(f"[green]✓ Style changed to: {style_name}[/green]")
        except KeyboardInterrupt:
            pass

    def _show_help(self):
        """Show help information"""
        self.console.print("\n[bold cyan]📖 PMPT CLI Help[/bold cyan]")
        self.console.print("=" * 50)
        
        # Commands section
        self.console.print("\n[bold yellow]🔧 Available Commands:[/bold yellow]")
        self.console.print("  [cyan]/help[/cyan]    - Show this help message")
        self.console.print("  [cyan]/style[/cyan]   - Change enhancement style (Gentle/Structured/Creative)")
        self.console.print("  [cyan]/version[/cyan] - Show version information")
        self.console.print("  [cyan]/quit[/cyan]    - Exit the application")
        
        # Usage section  
        self.console.print("\n[bold yellow]💡 How to Use:[/bold yellow]")
        self.console.print("  • Simply type your prompt and press [bold]Ctrl+D[/bold] or [bold]Meta+Enter[/bold] to submit")
        self.console.print("  • Your prompt will be enhanced using AI and displayed")
        self.console.print("  • Enhanced prompts are automatically copied to clipboard")
        self.console.print("  • Supports multiline input - paste long texts freely")
        
        # Styles section
        current_style = self.enhancement_styles[self.config.current_style]
        self.console.print(f"\n[bold yellow]🎨 Current Style:[/bold yellow] [bold]{current_style['name']}[/bold]")
        self.console.print(f"  {current_style['description']}")
        
        self.console.print("\n[bold yellow]🎨 Available Styles:[/bold yellow]")
        for style_key, style_info in self.enhancement_styles.items():
            marker = "→" if style_key == self.config.current_style else " "
            self.console.print(f"  {marker} [bold]{style_info['name']}[/bold]: {style_info['description']}")
        
        # Environment info
        detected_language = self.language_detector.detect_language()
        if detected_language:
            self.console.print(f"\n[bold yellow]🌍 Detected Environment:[/bold yellow] [green]{detected_language.title()}[/green]")
        
        # Tips section
        self.console.print(f"\n[bold yellow]💰 Tips:[/bold yellow]")
        self.console.print("  • Use [cyan]/style[/cyan] to experiment with different enhancement approaches")
        self.console.print("  • Run [cyan]pmpt config[/cyan] in terminal to change providers and settings")
        self.console.print("  • Environment detection helps tailor enhancements to your project")
        self.console.print("  • Run [cyan]pmpt update[/cyan] in terminal to check for updates")
        
        self.console.print(f"\n[dim]Version: {__version__}[/dim]")
        self.console.print()

    def _show_version(self):
        """Show version information"""
        self.console.print(f"\n[bold cyan]🚀 PMPT CLI[/bold cyan]")
        self.console.print(f"[bold]Version:[/bold] {__version__}")
        self.console.print(f"[dim]Run [cyan]pmpt update[/cyan] to check for updates[/dim]")
        self.console.print()

    async def _get_user_prompt(self) -> Optional[str]:
        """Get prompt from user"""
        try:
            current_style = self.enhancement_styles[self.config.current_style]
            style_color = current_style['color']
            style_name = current_style['name']
            
            # Use formatted text instead of HTML to avoid parsing errors
            from prompt_toolkit.formatted_text import FormattedText
            
            color_map = {
                "#90EE90": "ansibrightgreen",
                "#4169E1": "ansiblue", 
                "#FF69B4": "ansibrightmagenta",
                "#FFA500": "ansiyellow",
                "#20B2AA": "ansicyan"
            }
            
            pt_color = color_map.get(style_color, "ansiwhite")
            colored_prompt = FormattedText([
                (f'bold {pt_color}', style_name),
                ('', ' | Your prompt: ')
            ])
            
            # Use prompt_toolkit with multiline for proper paste support
            user_input = await self.prompt_session.prompt_async(
                colored_prompt
            )
            user_input = user_input.strip()
            
            if user_input.lower() == '/quit':
                return None
            elif user_input.lower() == '/style':
                await self._select_style()
                return ""
            elif user_input.lower() == '/help':
                self._show_help()
                return ""
            elif user_input.lower() == '/version':
                self._show_version()
                return ""
            # Legacy support for old commands
            elif user_input.lower() == 'quit':
                return None
            elif user_input.lower() == 'help':
                self._show_help()
                return ""
            elif user_input.lower() == 'version':
                self._show_version()
                return ""
            
            return user_input if user_input else ""
            
        except KeyboardInterrupt:
            return None
        except EOFError:
            return None
    
    async def _enhance_prompt_stream(self, user_prompt: str) -> Optional[str]:
        """Enhance user prompt using AI with streaming"""
        if not user_prompt:
            return ""
        
        try:
            # Integrate file context if @filepath references are found
            integrated_prompt = self._integrate_file_context(user_prompt)
            
            # Show file integration info if files were referenced
            file_references = self._extract_file_references(user_prompt)
            if file_references:
                self.console.print(f"[dim]🔗 Integrated {len(file_references)} file(s): {', '.join(file_references)}[/dim]")
            
            client = APIClient(self.config)
            current_style = self.enhancement_styles[self.config.current_style]
            
            # Add language context to the system prompt
            language_context = self.language_detector.get_language_context()
            enhanced_system_prompt = current_style['prompt']
            if language_context:
                enhanced_system_prompt += f" The user is working on a {language_context}, so consider this context when enhancing their prompt."
            
            # If files were integrated, add instruction to use the context
            if file_references:
                enhanced_system_prompt += " The user has provided file context that should inform and improve the enhanced prompt. Use the provided file contents to make the prompt more specific, relevant, and powerful."
            
            # Show label first
            self.console.print(f"\n[bold green]Enhanced Prompt ({current_style['name']}):[/bold green]")
            
            # Stream the response using the integrated prompt
            enhanced_prompt = ""
            async for chunk in client.enhance_prompt_stream(integrated_prompt, enhanced_system_prompt):
                self.console.print(chunk, end="")
                enhanced_prompt += chunk
            
            self.console.print()  # New line after streaming
            return enhanced_prompt
            
        except Exception as e:
            self.console.print(f"[red]Enhancement failed: {e}[/red]")
            return None
    
