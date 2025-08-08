#!/usr/bin/env python3
"""
WarpClaude - Universal BDD Project Generator for Claude Code
Automatically sets up Claude Code environment and manages BDD development lifecycle
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
import platform
import time

# Try to import optional packages
try:
    import questionary
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Constants removed - now loaded from assets

def print_console(message, style=""):
    """Print with rich console if available, otherwise plain print"""
    if console and RICH_AVAILABLE:
        console.print(message, style=style)
    else:
        print(message)

def print_panel(title, content):
    """Print a panel with rich if available"""
    if console and RICH_AVAILABLE:
        console.print(Panel(content, title=title))
    else:
        print(f"\n=== {title} ===")
        print(content)
        print("=" * (len(title) + 8))

def check_command(command, timeout=None):
    """Check if a command exists and return version or status"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip() or "Installed"
        return None
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None

def is_claude_installed():
    """Quick check if Claude Code is accessible in PATH"""
    # Try fast version check first
    version = check_command(["claude", "--version"], timeout=2)
    if version:
        return True
    
    # Check common npm global bin locations
    npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
    if npm_prefix:
        npm_bin = Path(npm_prefix.strip()) / "bin" / "claude"
        if npm_bin.exists():
            # Claude is installed but not in PATH
            return "installed_not_in_path"
    
    return False

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return "Installed"
    except ImportError:
        return None

def get_shell_config():
    """Get appropriate shell config file"""
    system = platform.system()
    home = Path.home()
    
    if system == "Darwin":  # macOS
        if (home / ".zshrc").exists():
            return home / ".zshrc"
        return home / ".bash_profile"
    elif system == "Linux":
        return home / ".bashrc"
    elif system == "Windows":
        return None
    
def install_nvm_and_node():
    """Install nvm and Node.js"""
    if platform.system() == "Windows":
        print_console("⚠️  Windows detected. Please install Node.js from nodejs.org", style="yellow")
        print_console("Then install Claude Code with: npm install -g @anthropic-ai/claude-code")
        return False
    
    print_console("📦 Installing nvm (Node Version Manager)...")
    
    # Install nvm
    nvm_install_cmd = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash'
    result = subprocess.run(nvm_install_cmd, shell=True)
    
    if result.returncode != 0:
        print_console("❌ Failed to install nvm", style="red")
        return False
    
    # Source nvm
    shell_config = get_shell_config()
    if shell_config:
        subprocess.run(f'source {shell_config}', shell=True)
    
    # Install node using nvm
    print_console("📦 Installing Node.js...")
    # We need to run this in a new shell that has nvm loaded
    install_node_cmd = f'source {shell_config} && nvm install node'
    result = subprocess.run(install_node_cmd, shell=True, executable='/bin/bash')
    
    if result.returncode == 0:
        print_console("✅ Node.js installed successfully", style="green")
        return True
    else:
        print_console("❌ Failed to install Node.js", style="red")
        return False

def check_and_install_claude():
    """Ensure Claude Code is installed and working"""
    print_console("🔍 Checking Claude Code installation...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        venv_path = sys.prefix
        print_console(f"📦 Virtual environment detected: {venv_path}", style="cyan")
    
    # Quick check first
    claude_status = is_claude_installed()
    if claude_status == True:
        print_console("✅ Claude Code is installed and accessible", style="green")
        return True
    elif claude_status == "installed_not_in_path":
        print_console("⚠️  Claude Code is installed but not in PATH", style="yellow")
        npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
        if npm_prefix:
            print_console(f"💡 Add this to your PATH: {npm_prefix.strip()}/bin", style="cyan")
            print_console("   Then restart your terminal", style="dim")
        return False
    
    # Not installed, continue with installation
    print_console("❌ Claude Code not found.", style="yellow")
    
    # Check if npm exists
    try:
        print_console("🔍 Checking for npm...", style="dim")
        npm_check = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        if npm_check.returncode != 0:
            raise FileNotFoundError
        print_console(f"✅ npm found: v{npm_check.stdout.strip()}", style="green")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_console("❌ npm not found.", style="red")
        
        if in_venv:
            print_console("\n⚠️  WARNING: You're in a virtual environment!", style="yellow bold")
            print_console("Claude Code needs to be installed globally with npm.", style="yellow")
            print_console("Options:", style="cyan")
            print_console("1. Exit venv and run: pip install warpcoder && warp", style="white")
            print_console("2. Or manually install: npm install -g @anthropic-ai/claude-code", style="white")
            print_console("\nPress Ctrl+C to exit and handle this manually.", style="yellow")
            try:
                input("\nPress Enter to continue anyway (not recommended)...")
            except KeyboardInterrupt:
                print_console("\n👋 Exiting. Please install Claude Code globally.", style="cyan")
                sys.exit(0)
        
        print_console("📦 Installing Node.js...", style="yellow")
        if not install_nvm_and_node():
            return False
        # After installing node, we need to reload the shell environment
        print_console("⚠️  Please run this script again in a new terminal to continue", style="yellow")
        sys.exit(0)
    
    # Install Claude Code
    print_console("📦 Installing Claude Code globally with npm...", style="cyan")
    print_console("⏳ This may take a minute...", style="dim")
    
    # Show the command being run
    install_cmd = ["npm", "install", "-g", "@anthropic-ai/claude-code"]
    print_console(f"🏃 Running: {' '.join(install_cmd)}", style="dim")
    
    # Run with real-time output
    already_installed = False
    try:
        process = subprocess.Popen(
            install_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
            # Detect if already installed
            if "changed" in line and "added" in line:
                if "changed" in line.split("added")[0]:
                    already_installed = True
        
        process.wait()
        result_code = process.returncode
    except Exception as e:
        print_console(f"❌ Error during installation: {e}", style="red")
        result_code = 1
    
    if result_code == 0:
        if already_installed:
            print_console("✅ Claude Code was already installed (updated)", style="green")
        else:
            print_console("✅ npm install completed", style="green")
        
        # Quick verify with version check instead of doctor
        print_console("🔍 Verifying Claude Code installation...", style="dim")
        claude_check = is_claude_installed()
        if claude_check == True:
            print_console("✅ Claude Code installed successfully!", style="green")
            return True
        elif claude_check == "installed_not_in_path":
            print_console("⚠️  Claude Code installed but not in PATH", style="yellow")
            npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
            if npm_prefix:
                print_console(f"\n💡 To fix this, add npm's bin directory to your PATH:", style="yellow")
                print_console(f"   export PATH=\"{npm_prefix.strip()}/bin:$PATH\"", style="cyan")
                print_console("   Then restart your terminal or run:", style="dim")
                print_console(f"   source ~/.zshrc  # or ~/.bashrc", style="cyan")
            return False
    
    print_console("❌ Failed to install Claude Code", style="red")
    print_console("Please install manually: npm install -g @anthropic-ai/claude-code")
    return False

def setup_context7():
    """Install and configure Context7 MCP server"""
    return install_mcp_server(
        "context7",
        ["context7", "--", "npx", "-y", "@upstash/context7-mcp@latest"],
        "Context7 MCP (Enhanced memory)"
    )

def install_mcp_server(server_name, command_args, description):
    """Generic function to install an MCP server"""
    print_console(f"\n🔧 Installing {description}...", style="cyan")
    
    if not is_claude_installed():
        print_console(f"⚠️  Claude Code not found. Skipping {server_name} setup.", style="yellow")
        return False
    
    try:
        # Build the full command
        cmd = ["claude", "mcp", "add"] + command_args
        
        print_console(f"🏃 Running: claude mcp add {' '.join(command_args[:3])}...", style="dim")
        
        # Run with timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        timeout_seconds = 60
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout_seconds:
                process.terminate()
                print_console(f"\n⏱️  {server_name} setup timed out after 60 seconds", style="yellow")
                return False
                
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
                
            if line:
                line = line.rstrip()
                if line:
                    print_console(f"   {line}", style="dim")
        
        return_code = process.poll()
        
        if return_code == 0:
            print_console(f"✅ {description} configured successfully!", style="green")
            return True
        else:
            print_console(f"⚠️  Could not configure {server_name} automatically", style="yellow")
            return False
    except Exception as e:
        print_console(f"⚠️  Error setting up {server_name}: {e}", style="yellow")
        return False

def setup_all_mcp_servers():
    """Install all recommended MCP servers"""
    print_console("\n🚀 Setting up MCP servers for enhanced Claude capabilities...", style="cyan bold")
    
    servers = [
        {
            "name": "context7",
            "args": ["context7", "--", "npx", "-y", "@upstash/context7-mcp@latest"],
            "description": "Context7 MCP (Enhanced memory)"
        },
        {
            "name": "puppeteer",
            "args": ["puppeteer", "--", "npx", "-y", "@modelcontextprotocol/server-puppeteer"],
            "description": "Puppeteer MCP (Browser automation)"
        },
        {
            "name": "magic",
            "args": ["magic", "--", "npx", "-y", "@modelcontextprotocol/server-magic"],
            "description": "Magic MCP (AI-powered utilities)"
        },
        {
            "name": "sequence-mcp",
            "args": ["--transport", "http", "sequence-mcp", "--", "npx", "-y", "@modelcontextprotocol/server-sequence"],
            "description": "Sequence MCP (Sequential operations)"
        }
    ]
    
    success_count = 0
    for server in servers:
        if install_mcp_server(server["name"], server["args"], server["description"]):
            success_count += 1
        time.sleep(1)  # Brief pause between installations
    
    print_console(f"\n📊 MCP Server Installation Summary:", style="cyan bold")
    print_console(f"   Successfully installed: {success_count}/{len(servers)} servers", style="green" if success_count == len(servers) else "yellow")
    
    if success_count < len(servers):
        print_console("\n💡 To manually install missing servers:", style="yellow")
        print_console("   Context7: claude mcp add context7 -- npx -y @upstash/context7-mcp@latest", style="dim")
        print_console("   Puppeteer: claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer", style="dim")
        print_console("   Magic: claude mcp add magic -- npx -y @modelcontextprotocol/server-magic", style="dim")
        print_console("   Sequence: claude mcp add --transport http sequence-mcp -- npx -y @modelcontextprotocol/server-sequence", style="dim")
    
    return success_count == len(servers)

def setup_claude_environment():
    """Copies the assets directory structure to the current working directory"""
    print_console("📁 Setting up Claude environment...", style="cyan")
    
    # Get the path to the assets directory in the package
    try:
        import importlib.resources as resources
        from . import assets
    except ImportError:
        # Python < 3.9 fallback
        import pkg_resources
        assets_path = Path(pkg_resources.resource_filename('warpcoder', 'assets'))
    else:
        # Python 3.9+
        with resources.as_file(resources.files('warpcoder') / 'assets') as assets_dir:
            assets_path = Path(assets_dir)
    
    # Copy entire assets directory structure to current working directory
    print_console("📋 Copying Claude configuration files...", style="dim")
    
    def copy_directory_contents(src_dir: Path, dst_parent: Path, base_src: Path = None):
        """Recursively copy directory contents to destination"""
        if base_src is None:
            base_src = src_dir
            
        for item in src_dir.iterdir():
            if item.is_file():
                # Get relative path from base assets directory
                relative_path = item.relative_to(base_src)
                dst_path = dst_parent / relative_path
                
                # Create parent directories if needed
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                print_console(f"   📄 {relative_path}", style="dim")
                shutil.copy2(item, dst_path)
            elif item.is_dir():
                # Recursively copy subdirectory
                copy_directory_contents(item, dst_parent, base_src)
    
    # Copy all contents from assets to current directory
    copy_directory_contents(assets_path, Path.cwd())
    
    # Ensure .claude directory exists (in case assets didn't have it)
    claude_dir = Path(".claude")
    claude_dir.mkdir(exist_ok=True)
    
    print_console("✅ Claude environment created (.claude/commands/)", style="green")
    
    # Print MCP setup instructions
    print_console("\n💡 To enhance Claude with MCP servers:", style="yellow")
    print_console("   Use menu option 7 to install all recommended servers", style="cyan")
    print_console("   Or install individually:", style="dim")
    print_console("   • Context7: claude mcp add context7 -- npx -y @upstash/context7-mcp@latest", style="dim")
    print_console("   • Puppeteer: claude mcp add puppeteer -- npx -y @modelcontextprotocol/server-puppeteer", style="dim")
    print_console("   • Magic: claude mcp add magic -- npx -y @modelcontextprotocol/server-magic", style="dim")
    print_console("   • Sequence: claude mcp add --transport http sequence-mcp npx -y @modelcontextprotocol/server-sequence", style="dim")

def detect_tech_stack(app_goal):
    """Detect appropriate tech stack from the app goal description"""
    goal_lower = app_goal.lower()
    
    # Python frameworks
    if any(word in goal_lower for word in ["fastapi", "fast api", "fast-api"]):
        return "python-fastapi"
    elif "django" in goal_lower:
        return "python-django"
    elif "flask" in goal_lower:
        return "python-flask"
    elif "python" in goal_lower:
        return "python-fastapi"  # Default Python stack
    
    # JavaScript/Node frameworks
    elif any(word in goal_lower for word in ["express", "nodejs", "node.js", "node"]):
        return "node-express"
    elif any(word in goal_lower for word in ["react", "nextjs", "next.js"]):
        return "node-react"
    elif any(word in goal_lower for word in ["vue", "vuejs", "vue.js"]):
        return "node-vue"
    elif "javascript" in goal_lower or "js" in goal_lower:
        return "node-express"  # Default Node stack
    
    # Ruby frameworks
    elif any(word in goal_lower for word in ["rails", "ruby on rails", "ror"]):
        return "ruby-rails"
    elif "ruby" in goal_lower:
        return "ruby-rails"
    
    # Other languages/frameworks
    elif any(word in goal_lower for word in ["rust", "actix", "rocket"]):
        return "rust"
    elif any(word in goal_lower for word in ["go", "golang", "gin", "echo"]):
        return "go"
    elif any(word in goal_lower for word in ["java", "spring", "springboot"]):
        return "java-spring"
    elif any(word in goal_lower for word in ["c#", "csharp", ".net", "aspnet"]):
        return "dotnet"
    
    # Default fallback
    else:
        return "python-fastapi"

def detect_bdd_project():
    """Returns True if features/ folder exists AND contains .feature files"""
    features_dir = Path("features")
    if features_dir.exists() and features_dir.is_dir():
        feature_files = list(features_dir.glob("*.feature"))
        return len(feature_files) > 0
    return False

def find_entry_points():
    """Find play.py, menu.py, start.py, run.py in current directory"""
    patterns = ["play.py", "menu.py", "start.py", "run.py"]
    found = []
    for pattern in patterns:
        if Path(pattern).exists():
            found.append(pattern)
    return found

def find_latest_app_directory():
    """Find the most recently created directory with features/ inside"""
    dirs_with_features = []
    for item in Path(".").iterdir():
        if item.is_dir() and (item / "features").exists():
            dirs_with_features.append(item)
    
    if dirs_with_features:
        # Return the most recently modified
        return max(dirs_with_features, key=lambda d: d.stat().st_mtime).name
    return "."

def run_bddinit(app_goal):
    """Run bddinit with the given app goal"""
    print_console("🚀 Starting BDD initialization...", style="cyan")
    print_console(f"📝 Goal: {app_goal}", style="dim")
    
    # Detect and display tech stack
    tech_stack = detect_tech_stack(app_goal)
    print_console(f"🔧 Detected tech stack: {tech_stack}", style="dim")
    print_console("", style="")
    
    try:
        print_console("🏃 Launching Claude Code with bddinit command...", style="dim")
        subprocess.run(["claude", f"/project:bddinit {app_goal}"])
    except FileNotFoundError:
        print_console("❌ Claude Code not found. Please ensure it's installed.", style="red")
        print_console("💡 Try running: npm install -g @anthropic-ai/claude-code", style="yellow")
        sys.exit(1)
    except KeyboardInterrupt:
        print_console("\n👋 Cancelled by user", style="yellow")
        sys.exit(0)

def run_bddwarp():
    """Run bddwarp with infinite iterations in current directory"""
    print_console(f"🔄 Starting BDD development loop...", style="cyan")
    print_console("📁 Working in: current directory", style="dim")
    print_console("🔢 Iterations: infinite", style="dim")
    print_console("📋 This will:", style="dim")
    print_console("   1. Run BDD tests", style="dim")
    print_console("   2. Generate step definitions", style="dim")
    print_console("   3. Implement code to pass tests", style="dim")
    print_console("   4. Create entry points (play.py/menu.py)", style="dim")
    print_console("", style="")
    
    try:
        print_console("🏃 Launching Claude Code with bddwarp command...", style="dim")
        subprocess.run(["claude", "/project:bddwarp"])
    except FileNotFoundError:
        print_console("❌ Claude Code not found. Please ensure it's installed.", style="red")
        print_console("💡 Try running: npm install -g @anthropic-ai/claude-code", style="yellow")
        sys.exit(1)
    except KeyboardInterrupt:
        print_console("\n👋 Cancelled by user", style="yellow")
        sys.exit(0)

def handle_with_goal(app_goal):
    """Handle warpcoder when given a goal directly"""
    # Setup claude environment first
    setup_claude_environment()
    
    # If BDD project already exists, just mention it and continue
    if detect_bdd_project():
        print_console("✓ BDD project already exists. Re-initializing with new goal...", style="yellow")
    
    # Run bddinit with the goal
    run_bddinit(app_goal)
    
    # Wait a moment for bddinit to complete
    print_console("\n⏳ Waiting for initialization to complete...", style="dim")
    time.sleep(3)
    
    # Now run bddwarp
    print_console("\n✅ Initialization complete! Starting development loop...", style="green")
    run_bddwarp()

def simple_input(prompt):
    """Simple input function when questionary not available"""
    return input(f"{prompt}: ")

def simple_select(prompt, choices):
    """Simple selection when questionary not available"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    while True:
        try:
            selection = int(input("Choose (number): "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
        except ValueError:
            pass
        print("Invalid choice. Please enter a number.")

def get_input(prompt, default=None):
    """Get input with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        if default is None:
            return questionary.text(prompt).ask()
        else:
            return questionary.text(prompt, default=default).ask()
    else:
        result = simple_input(prompt)
        return result if result else default

def get_select(prompt, choices):
    """Get selection with fallback for missing questionary"""
    if QUESTIONARY_AVAILABLE:
        return questionary.select(prompt, choices=choices).ask()
    else:
        return simple_select(prompt, choices)

def handle_quick_start():
    """Option 1: Quick start - auto init + warp"""
    if detect_bdd_project():
        print_console("✓ BDD project detected. Continuing development...", style="green")
        run_bddwarp()
    else:
        print_console("No BDD project found.", style="yellow")
        app_goal = get_input("What would you like to build?")
        if app_goal:
            print_console(f"\n💡 Tip: Next time you can run: warpcoder \"{app_goal}\"", style="dim")
            handle_with_goal(app_goal)

def handle_initialize():
    """Option 2: Initialize new project"""
    app_goal = get_input("What would you like to build?")
    if app_goal:
        run_bddinit(app_goal)
    else:
        print_console("❌ App goal is required.", style="red")

def handle_continue():
    """Option 3: Continue existing project"""
    if detect_bdd_project():
        run_bddwarp()
    else:
        print_console("❌ No BDD project found. Run option 2 first.", style="red")

def handle_run_project():
    """Option 4: Run finished project"""
    entry_points = find_entry_points()
    if entry_points:
        if len(entry_points) == 1:
            selected = entry_points[0]
        else:
            selected = get_select("Run which file?", entry_points)
        print_console(f"🎮 Starting {selected}...", style="cyan")
        try:
            subprocess.run(["python", selected])
        except FileNotFoundError:
            print_console("❌ Python not found in PATH", style="red")
        except KeyboardInterrupt:
            print_console("\n👋 Stopped by user", style="yellow")
    else:
        print_console("❌ No entry point (play.py/menu.py) found.", style="red")

def handle_install_claude():
    """Option 5: Install Claude Code and dependencies"""
    print_console("📦 Installing Claude Code and dependencies...", style="cyan")
    if check_and_install_claude():
        print_console("✅ Installation complete!", style="green")
        
        # Ask if user wants to install MCP servers
        if QUESTIONARY_AVAILABLE:
            install_mcp = questionary.confirm(
                "Would you like to install recommended MCP servers (Context7, Puppeteer, Magic, Sequence)?",
                default=True
            ).ask()
        else:
            response = input("\nInstall recommended MCP servers? (Y/n): ").strip().lower()
            install_mcp = response != 'n'
        
        if install_mcp:
            setup_all_mcp_servers()
        else:
            print_console("💡 You can install MCP servers later from the menu", style="dim")
    else:
        print_console("❌ Installation failed. Please try manually.", style="red")

def handle_setup_only():
    """Option 6: Setup Claude environment only"""
    setup_claude_environment()
    print_console("✅ Claude environment setup complete", style="green")

def create_sdk_example():
    """Option 6: Create SDK example"""
    sdk_example = '''#!/usr/bin/env python3
"""Example of using Claude Code SDK with Context7"""

from claude_code_sdk import ClaudeClient, ClaudeOptions

# Configure with Context7 MCP
options = ClaudeOptions(
    mcp_config="mcp-servers.json",
    allowed_tools=["mcp__context7"]
)

# Create client
client = ClaudeClient(options=options)

# Example: Use Context7 for memory
project_goal = "Your project goal here"
tech_stack = "Your tech stack here"

response = client.prompt(f"""
    Remember this project is about: {project_goal}
    Tech stack: {tech_stack}
""")

print(response)
'''
    
    with open("claude_sdk_example.py", "w") as f:
        f.write(sdk_example)
    print_console("📝 Created claude_sdk_example.py for SDK usage", style="green")

def check_mcp_servers():
    """Check which MCP servers are installed"""
    if not is_claude_installed():
        return {}
    
    try:
        result = subprocess.run(["claude", "mcp", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            mcp_servers = {}
            output = result.stdout.strip()
            
            # Handle case where no servers are configured
            if "No MCP servers configured" in output:
                return {}
            
            # Parse the output format: "server-name: command args"
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                
                # Extract server name (before the colon)
                server_name = line.split(':')[0].strip()
                if server_name:
                    mcp_servers[server_name] = "Installed"
                    
            return mcp_servers
        return {}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}

def check_installation_status():
    """Option 7: Check installation status"""
    print_panel("Installation Status", "Checking all components...")
    
    # Check each component
    checks = {
        "Node.js": check_command(["node", "--version"]),
        "npm": check_command(["npm", "--version"]),
        "Claude Code": check_command(["claude", "--version"]),
        "Python": check_command(["python", "--version"]),
    }
    
    # Add optional package checks
    if QUESTIONARY_AVAILABLE:
        checks["Questionary"] = "Installed"
    else:
        checks["Questionary"] = "Not installed (using fallback)"
    
    if RICH_AVAILABLE:
        checks["Rich"] = "Installed"
    else:
        checks["Rich"] = "Not installed (using plain text)"
    
    # Display results
    all_good = True
    for component, status in checks.items():
        if status and "Not installed" not in status:
            print_console(f"✅ {component}: {status}", style="green")
        else:
            print_console(f"❌ {component}: {status or 'Not installed'}", style="red")
            all_good = False
    
    # Check MCP servers
    print_console("\n📡 MCP Servers:", style="cyan bold")
    mcp_servers = check_mcp_servers()
    
    mcp_status = {
        "context7": "Context7 (Enhanced memory)",
        "puppeteer": "Puppeteer (Browser automation)",
        "magic": "Magic (AI-powered utilities)",
        "sequence-mcp": "Sequence (Sequential operations)"
    }
    
    for server_id, description in mcp_status.items():
        if server_id in mcp_servers:
            print_console(f"✅ {description}", style="green")
        else:
            print_console(f"❌ {description} - Not installed", style="dim")
    
    if not mcp_servers:
        print_console("   No MCP servers detected", style="dim")
    
    if all_good:
        print_console("\n✨ All core components installed!", style="green bold")
    else:
        print_console("\n⚠️  Some components missing. Run setup to install.", style="yellow")

def show_interactive_menu():
    """Show the interactive menu"""
    print_panel("WarpCoder BDD Tool", "Complete BDD Development Environment")
    
    choices = [
        "1. Quick Start (Auto Init + Warp)",
        "2. Initialize New Project (bddinit)",
        "3. Continue Project (bddwarp)",
        "4. Run Finished Project",
        "5. Install Claude Code & Dependencies",
        "6. Setup Claude Environment Only",
        "7. Install MCP Servers",
        "8. Create SDK Example",
        "9. Check Installation Status",
        "10. Exit"
    ]
    
    while True:
        choice = get_select("Choose an option:", choices)
        
        if "1." in choice:
            handle_quick_start()
            break
        elif "2." in choice:
            handle_initialize()
            break
        elif "3." in choice:
            handle_continue()
            break
        elif "4." in choice:
            handle_run_project()
            break
        elif "5." in choice:
            handle_install_claude()
        elif "6." in choice:
            handle_setup_only()
        elif "7." in choice:
            setup_all_mcp_servers()
        elif "8." in choice:
            create_sdk_example()
        elif "9." in choice:
            check_installation_status()
        elif "10." in choice:
            print_console("👋 Goodbye!", style="cyan")
            break

def show_help():
    """Show help information"""
    help_text = """
WarpCoder - BDD Development Tool for Claude Code

Usage:
  warpcoder "your app idea"         # Direct goal specification
  warpcoder                         # Interactive mode
  warpcoder [OPTIONS]              # Various options

Quick Start Examples:
  warpcoder "I want to build a tic tac toe game in python fastapi"
  warpcoder "Create a todo app with tags and categories"
  warpcoder "Build a REST API for managing books"
  
Options:
  --menu            Show interactive menu with all options
  --help            Show this help message
  --check           Check installation status (includes MCP servers)
  --installclaude   Install Claude Code and dependencies
  --installmcp      Install all recommended MCP servers

Default Behavior:
  - With goal: Initialize BDD project and start development
  - Without goal: Check for existing project or prompt for goal
  - Always works in current directory (no subfolders)
  - Always runs infinite iterations (no limits)

Features:
  ✓ Direct command line goal specification
  ✓ Smart tech stack detection from goal
  ✓ BDD project initialization with domain models
  ✓ Automated test-driven development loop
  ✓ Creates entry points (play.py/menu.py)

Inside Claude Code:
  /project:bddinit "your app goal"  # Initialize BDD project
  /project:bddwarp                  # Continue development (infinite)

Examples:
  warpcoder "build a chat app"      # Start new project with goal
  warpcoder                         # Continue existing or prompt
  warpcoder --menu                  # Interactive menu
  warpcoder --installclaude         # Install dependencies
"""
    print(help_text)

def main():
    """Main entry point"""
    # Check for direct goal as first argument (no --flag)
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        app_goal = sys.argv[1]
        print_console(f"🚀 WarpCoder - Building: {app_goal}", style="cyan bold")
        
        # Check Claude availability
        claude_status = is_claude_installed()
        if claude_status == "installed_not_in_path":
            print_console("\n⚠️  Claude Code is installed but not in PATH", style="yellow")
            npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
            if npm_prefix:
                print_console(f"💡 Add this to your PATH: {npm_prefix.strip()}/bin", style="cyan")
                print_console("   Then restart your terminal", style="dim")
            return
        elif not claude_status:
            print_console("\n❌ Claude Code not found.", style="red")
            print_console("Install with: warp --installclaude", style="yellow")
            return
            
        handle_with_goal(app_goal)
        return
    
    # Show banner for other modes
    if RICH_AVAILABLE:
        print_console("╭─────────────────────────────╮", style="cyan")
        print_console("│     🚀 WarpCoder v0.3.6     │", style="cyan bold")
        print_console("╰─────────────────────────────╯", style="cyan")
    else:
        print_console("=== 🚀 WarpCoder v0.3.6 ===", style="")
    
    # Handle command line arguments
    if "--help" in sys.argv:
        show_help()
        return
    
    if "--check" in sys.argv:
        check_installation_status()
        return
    
    if "--installclaude" in sys.argv:
        print_console("\n📦 Installing Claude Code...", style="cyan")
        if not check_and_install_claude():
            print_console("\n❌ Could not install Claude Code.", style="red")
            print_console("Please install manually:", style="yellow")
            print_console("  npm install -g @anthropic-ai/claude-code", style="white")
            return
        print_console("\n✅ Installation complete!", style="green")
        # Try to setup Context7, but don't fail if it doesn't work
        setup_context7()
        return
    
    if "--installmcp" in sys.argv:
        print_console("\n📡 Installing MCP Servers...", style="cyan")
        if not is_claude_installed():
            print_console("\n❌ Claude Code is required to install MCP servers.", style="red")
            print_console("Install with: warp --installclaude", style="yellow")
            return
        setup_all_mcp_servers()
        return
    
    print_console("", style="")  # Empty line
    
    # Just check if Claude exists, don't install
    claude_status = is_claude_installed()
    if claude_status == True:
        print_console("✅ Claude Code detected", style="green dim")
    elif claude_status == "installed_not_in_path":
        print_console("⚠️  Claude Code installed but not in PATH", style="yellow dim")
        npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
        if npm_prefix:
            print_console(f"💡 Add to PATH: {npm_prefix.strip()}/bin", style="cyan dim")
    else:
        print_console("⚠️  Claude Code not found. Install with: warp --installclaude", style="yellow dim")
    
    # Setup Claude environment
    setup_claude_environment()
    
    # Handle menu or auto-run
    if "--menu" in sys.argv:
        show_interactive_menu()
    else:
        # DEFAULT: Auto-run based on project state
        if claude_status != True:
            if claude_status == "installed_not_in_path":
                print_console("\n⚠️  Claude Code is installed but not in PATH.", style="yellow")
                npm_prefix = check_command(["npm", "config", "get", "prefix"], timeout=2)
                if npm_prefix:
                    print_console(f"💡 Fix by adding to PATH: {npm_prefix.strip()}/bin", style="cyan")
                    print_console("   Then restart your terminal", style="dim")
            else:
                print_console("\n⚠️  Claude Code is required to run BDD commands.", style="yellow")
                print_console("Install with: warp --installclaude", style="yellow")
            print_console("Or use menu: warp --menu", style="yellow")
            return
            
        if detect_bdd_project():
            print_console("✓ BDD project detected. Continuing development...", style="green")
            run_bddwarp()
        else:
            print_console("No BDD project found.", style="yellow")
            app_goal = get_input("What would you like to build?")
            if app_goal:
                print_console(f"\n💡 Tip: Next time you can run: warpcoder \"{app_goal}\"", style="dim")
                handle_with_goal(app_goal)

if __name__ == "__main__":
    main()