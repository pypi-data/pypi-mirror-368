# Gira - Git-based Issue Tracking and Project Management

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-88%25-green.svg)]()
[![Documentation](https://github.com/goatbytes/gira/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/goatbytes/gira/actions/workflows/deploy-docs.yml)
[![MCP Tests](https://github.com/goatbytes/gira/actions/workflows/mcp-tests.yml/badge.svg)](https://github.com/goatbytes/gira/actions/workflows/mcp-tests.yml)
[![Style Guide-Python](https://img.shields.io/badge/Style%20Guide-Python-7F52FF.svg?style=flat&labelColor=black&color=7F52FF&logo=python)](https://styles.goatbytes.io/lang/python)
![License](https://img.shields.io/badge/License-MIT-blue)

**Gira** is a lightweight, Git-friendly project management tool designed for developers and AI agents. It stores all project data in plain JSON files within your repository, making it perfect for version control and collaboration.

## ✨ Features

- **Git-Native**: All data stored as JSON files in `.gira/` directory
- **Offline-First**: Works completely offline, no external dependencies
- **AI-Friendly**: MCP server for AI agents (Claude, Gemini) with 30+ tools
- **Kanban Board**: Visual project management with customizable swimlanes
- **Rich CLI**: Beautiful terminal UI with colors and tables
- **Advanced Search**: Powerful query language with filters and full-text search
- **Shell Completion**: Tab completion for all commands and dynamic ID completion
- **Fast**: Lightweight and responsive, perfect for large projects
- **Extensible**: Hook system, webhooks, and custom fields support
- **Import/Export**: JSON, CSV, and Markdown format support

## 🚀 Quick Start

```bash
# Install Gira
pip install gira  # Available on PyPI

# Or install from source
pip install -e .

# Install with optional features
pip install "gira[mcp]"    # For AI agent integration (Claude, etc.)
pip install "gira[s3]"     # For AWS S3, Cloudflare R2, Backblaze B2
pip install "gira[gcs]"    # For Google Cloud Storage
pip install "gira[azure]"  # For Azure Blob Storage
pip install "gira[all]"    # All features (MCP + all storage backends)

# Initialize a new project
gira init "My Project"

# Create your first ticket
gira ticket create "Set up project structure"

# View the kanban board
gira board

# List all tickets
gira ticket list
```

## 📋 Core Commands

### Project Management
- `gira init <name>` - Initialize a new Gira project
- `gira --version` - Show version information

### Ticket Operations
- `gira ticket create <title>` - Create a new ticket
- `gira ticket list` - List tickets with filtering (`--search`, `--labels`, `--assignee`)
- `gira ticket show <id>` - Display ticket details  
- `gira ticket update <id>` - Update ticket fields
- `gira ticket move <id> <status>` - Move ticket between statuses

### Epic Management
- `gira epic create <title>` - Create a new epic
- `gira epic list` - List all epics
- `gira epic show <id>` - Display epic details
- `gira epic update <id>` - Update epic fields (`--add-tickets`)

### Sprint Management  
- `gira sprint create <name>` - Create a new sprint (`--duration`, `--end-date`)
- `gira sprint list` - List sprints (`--format json`)
- `gira sprint show <id>` - Display sprint details
- `gira sprint update <id>` - Update sprint fields

### Comments & Search
- `gira comment add <ticket-id>` - Add comment to ticket
- `gira comment list <ticket-id>` - List ticket comments
- `gira query <expression>` - Advanced search with filters

### Export & Integration
- `gira export json` - Export project data to JSON
- `gira export csv` - Export to CSV format  
- `gira export md` - Export to Markdown format
- `gira webhook add <url>` - Add webhook integration

### AI Integration
- **MCP Server**: 30+ tools for AI agents (Claude Desktop, etc.)
- **Natural Language**: AI agents can manage tickets through conversation
- Install: `pip install "gira[mcp]"` and configure Claude Desktop

### Shell Completion
- `gira --install-completion` - Install tab completion (recommended)
- `gira completion install <shell>` - Legacy completion system (deprecated)

### Board Visualization
- `gira board` - Display kanban board
- `gira board --compact` - Compact board view
- `gira board --assignee <email>` - Filter by assignee

### Backlog Management
- `gira backlog` - View backlog tickets with smart filters
- `gira backlog --ready` - Show tickets ready to work on
- `gira backlog --unassigned` - Show unassigned tickets
- `gira backlog --priority high` - Filter by priority
- `gira backlog --counts` - Show summary counts

## 🏗️ Project Structure

```
.gira/
├── config.json          # Project configuration
├── .state.json         # Internal state (next ticket ID, etc.)
├── backlog/            # Tickets in backlog
├── board/              # Active tickets by status
│   ├── todo/
│   ├── in_progress/
│   ├── review/
│   └── done/
├── epics/              # Epic definitions and management
├── sprints/            # Sprint data and tracking
├── comments/           # Ticket comments and discussions
└── archive/            # Completed tickets
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start Guide](docs/quickstart.md)
- [User Guide](docs/02-user-guide/README.md)
- [Architecture Overview](docs/00-overview/architecture.md)
- [CLI Reference](docs/05-reference/cli-reference.md)

## 🛠️ Advanced Features

### Custom Git Merge Driver

Gira includes an intelligent Git merge driver that automatically resolves conflicts in JSON files:

- **Smart Conflict Resolution**: Uses "latest-write-wins" strategy based on timestamps
- **Semantic Merging**: Understands ticket structure and merges fields intelligently
- **File Movement Handling**: Correctly handles tickets moved to different statuses
- **Audit Trail**: Adds merge notes to track automatic resolutions

To enable the merge driver:
```bash
.gira/scripts/setup-merge-driver.sh
```

See [merge driver documentation](docs/03-integrations/git-merge-driver.md) for details.


## Contributing

Contributions are welcome! Please read our [contributing guide](CONTRIBUTING.md) and submit pull requests to our repository.

## 📚 Documentation

Comprehensive documentation is available at **[goatbytes.github.io/gira](https://goatbytes.github.io/gira/)**

- **[📖 Installation](https://goatbytes.github.io/gira/installation/)** - Installation guide
- **[🚀 Quick Start](https://goatbytes.github.io/gira/quickstart/)** - Get started in minutes
- **[📋 User Guide](https://goatbytes.github.io/gira/02-user-guide/)** - Complete feature documentation  
- **[🔧 CLI Reference](https://goatbytes.github.io/gira/05-reference/cli-reference/)** - All commands and options
- **[📝 Commands](https://goatbytes.github.io/gira/05-reference/commands/)** - Individual command documentation
- **[🤖 AI Agents](https://goatbytes.github.io/gira/10-ai-agents/)** - AI integration documentation
- **[🔗 MCP Server](https://goatbytes.github.io/gira/09-mcp/)** - Model Context Protocol integration

> 📡 Documentation is automatically updated on every release using our automated generation system.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/goatbytes/gira.git
cd gira

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

## 📊 Testing

Gira maintains high test coverage (88%+) with comprehensive unit and integration tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gira --cov-report=html

# Run specific test file
pytest tests/integration/test_cli_ticket.py
```

## 🔧 Requirements

- Python 3.8 or higher
- Git (for version control integration)
- Terminal with Unicode support (for rich output)

## 🎯 Design Philosophy

Gira follows these core principles:

1. **Simplicity**: Plain JSON files, no database required
2. **Transparency**: All data is human-readable and Git-friendly
3. **Flexibility**: Extensible design for custom workflows
4. **Performance**: Fast operations even with thousands of tickets
5. **AI-First**: Structured data optimized for AI agent interaction


## 🔧 Troubleshooting

### Unicode Display Issues

If you see garbled characters (like `â`) instead of box-drawing characters in the board view:

```bash
# Set environment variable to force ASCII-only output
export GIRA_ASCII_ONLY=1
gira board

# Or force Unicode if your terminal supports it
export GIRA_FORCE_UNICODE=1
gira board
```

For container environments, Gira automatically detects and adjusts output. If auto-detection fails, use the environment variables above.

---

## 📄 License

Gira is released under the MIT License. See [LICENSE](LICENSE) file for details.

---

## About GoatBytes.IO

![GoatBytesLogo](.art/banner.webp)

At **[GoatBytes.IO](https://goatbytes.io)**, our mission is to develop secure software solutions that empower businesses to
transform the world. With a focus on innovation and excellence, we strive to deliver cutting-edge
products that meet the evolving needs of businesses across various industries.

[![GitHub](https://img.shields.io/badge/GitHub-GoatBytes-181717?logo=github)](https://github.com/goatbytes)
[![Twitter](https://img.shields.io/badge/Twitter-GoatBytes-1DA1F2?logo=twitter)](https://twitter.com/goatbytes)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-GoatBytes-0077B5?logo=linkedin)](https://www.linkedin.com/company/goatbytes)
[![Instagram](https://img.shields.io/badge/Instagram-GoatBytes.io-E4405F?logo=instagram)](https://www.instagram.com/goatbytes.io/)
