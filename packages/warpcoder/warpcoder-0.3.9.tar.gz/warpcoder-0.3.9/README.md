# WarpCoder

**License Notice:** This is commercial software. See pricing tiers below and LICENSE file for full terms.

Universal BDD Project Generator for Claude Code - Transform your ideas into working applications using AI-powered Behavior Driven Development.

## Why WarpCoder?

WarpCoder transforms the software development process into an AI-assisted journey that takes you from idea to working application. It combines:

- **AI-powered development** - Leverage Claude Code to generate, test, and fix code automatically
- **BDD workflow** - Follow a structured process from project initialization to deployment
- **Smart automation** - Automatically detects project state and continues where you left off
- **Full-stack support** - Handles backend, frontend, database, and integration seamlessly
- **Zero configuration** - Installs and configures all dependencies automatically

Whether you're building a new application from scratch or continuing an existing project, WarpCoder manages the entire development lifecycle for you.

## Installation

```bash
pip install warpcoder
```

## Requirements

- Python 3.8 or higher
- Git
- Internet connection (for AI-assisted features and initial setup)
- macOS, Linux, or Windows

## Quick Start

WarpCoder provides multiple ways to start your development journey:

### Direct Goal Specification (Recommended)
```bash
# Specify your goal directly - WarpCoder handles everything else
warpcoder "I want to build a tic tac toe game in python fastapi"
warpcoder "Create a todo app with tags and categories"
warpcoder "Build a REST API for managing books"
```

### Interactive Mode
```bash
# Run without arguments for guided setup
warpcoder

# Or use the menu for all options
warpcoder --menu
```

### Command Shortcuts
The package provides three equivalent commands:
- `warpcoder` - Main command
- `warp` - Short alias
- `warpclaude` - Alternative name

## Command Overview

### Main Commands

| Command | Description |
|---------|-------------|
| `warpcoder "your app idea"` | Start new project with your goal |
| `warpcoder` | Auto-detect and continue existing project |
| `warpcoder --menu` | Show interactive menu with all options |
| `warpcoder --check` | Check installation status (includes MCP servers) |
| `warpcoder --installclaude` | Install Claude Code and dependencies |
| `warpcoder --installmcp` | Install all recommended MCP servers |
| `warpcoder --help` | Show help message |

### Menu Options

When using `--menu`, you'll see:

1. **Quick Start** - Auto initialize and start development
2. **Initialize New Project** - Run bddinit with your app goal
3. **Continue Project** - Run bddwarp development loop
4. **Run Finished Project** - Execute play.py or menu.py
5. **Install Claude Code** - Set up Claude and dependencies
6. **Setup Claude Environment** - Create .claude configuration
7. **Install MCP Servers** - Add Context7, Puppeteer, Magic, Sequence
8. **Create SDK Example** - Generate example SDK usage
9. **Check Installation Status** - Verify all components
10. **Exit**

## How It Works

### Phase 1: Environment Setup
WarpCoder automatically:
- Installs Claude Code globally via npm
- Sets up Node.js if not present (via nvm on Unix)
- Configures MCP servers for enhanced capabilities
- Creates .claude configuration with BDD commands

### Phase 2: Project Initialization (bddinit)
When you provide an app goal, WarpCoder:
- Detects appropriate tech stack (Python/Node/Ruby)
- Creates domain models and architecture documents
- Generates BDD feature files
- Plans implementation with pseudocode
- Sets up testing framework (behave/cucumber)

### Phase 3: Development Loop (bddwarp)
The development loop:
- Runs BDD tests to identify failures
- Generates step definitions
- Implements code to pass tests
- Creates database models and migrations
- Builds API endpoints
- Connects frontend to backend
- Creates user entry points (play.py/menu.py)
- Captures screenshots and documentation

### Phase 4: Delivery
Your completed project includes:
- Working application with all tests passing
- Entry point for easy execution
- Full documentation
- Clean architecture following DDD principles

## Project Structure

WarpCoder creates a well-organized project:

```
your-project/
├── features/              # BDD feature files
│   ├── *.feature         # Gherkin scenarios
│   ├── steps/            # Step definitions
│   └── environment.py    # Test configuration
├── docs/                  # Documentation
│   ├── ddd.md            # Domain-Driven Design model
│   ├── state-diagram.md  # State flow visualization
│   └── mission.md        # Project mission and scope
├── pseudocode/           # Architecture planning
│   ├── main_controller.pseudo
│   ├── data_manager.pseudo
│   └── business_rules.pseudo
├── src/                  # Source code (auto-generated)
├── tests/                # Unit tests (auto-generated)
├── play.py              # Web app entry point
├── menu.py              # CLI app entry point
└── .claude/             # Claude configuration
    ├── commands/        # Custom BDD commands
    ├── settings.json
    └── settings.local.json
```

## MCP Servers

WarpCoder can install and configure Model Context Protocol (MCP) servers:

- **Context7** - Enhanced memory across Claude sessions
- **Puppeteer** - Browser automation for web testing
- **Magic** - AI-powered development utilities
- **Sequence** - Sequential operation management

Install all MCP servers:
```bash
warpcoder --installmcp
```

## Examples

### Create a New Web Application
```bash
# Direct approach - WarpCoder handles everything
warpcoder "build a recipe sharing platform with user accounts"
```

### Create a CLI Tool
```bash
warpcoder "create a command-line password manager with encryption"
```

### Continue Existing Project
```bash
# In a directory with existing BDD project
warpcoder
# Automatically detects and continues development
```

### Check Environment
```bash
# See what's installed
warpcoder --check
```

## Tech Stack Detection

WarpCoder automatically detects the best tech stack from your goal:
- **Python**: FastAPI, Django, Flask
- **JavaScript**: Express, React, Vue, Next.js
- **Ruby**: Rails
- **Other**: Rust, Go, Java Spring, C#/.NET

## Development

To contribute to WarpCoder:

```bash
git clone https://github.com/starshipagentic/warpcoder.git
cd warpcoder
pip install -e .
```

## Support

- **GitHub**: [https://github.com/starshipagentic/warpcoder](https://github.com/starshipagentic/warpcoder)
- **Issues**: [https://github.com/starshipagentic/warpcoder/issues](https://github.com/starshipagentic/warpcoder/issues)
- **PyPI**: [https://pypi.org/project/warpcoder](https://pypi.org/project/warpcoder)

## License

WarpCoder is commercial software with friendly pricing for individuals and small teams.

### Pricing Tiers

| Your Annual Revenue | Monthly Cost (Entire Organization) | Perfect For |
|---------------------|-----------------------------------|-------------|
| **Personal/Learning** | Free (donation optional) | Students, hobbyists, learning |
| **Up to $100K** | $10/month for entire organization | Individual consultants, freelancers |
| **$100K - $250K** | $25/month for entire organization | Small consultancies, startups |
| **$250K - $500K** | $50/month for entire organization | Growing agencies |
| **$500K+** | Revenue ÷ 1000 per month | Established businesses |
| **$5M+** | Revenue ÷ 1000 per month (max $5K) + training | Enterprise organizations |

**All generated code is yours to keep!**

Payment options:
- **Small tiers**: [Patreon](https://patreon.com/c/starshipagentic) or [Buy Me a Coffee](https://buymeacoffee.com/starshipagentic)
- **Larger tiers**: Multiple coffees or contact starshipagentic@gmail.com

See [LICENSE](LICENSE) for complete terms.

## Credits

Created by Warpcoders LLC

---

*WarpCoder: From idea to application at warp speed with AI-powered BDD*