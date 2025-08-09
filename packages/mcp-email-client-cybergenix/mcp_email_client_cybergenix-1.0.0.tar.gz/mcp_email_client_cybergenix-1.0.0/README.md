# MCP Email Client

[![PyPI version](https://badge.fury.io/py/mcp-email-client.svg)](https://badge.fury.io/py/mcp-email-client)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MCP Email Client is a Python-based email management tool that implements the Model Context Protocol (MCP) for seamless integration with Claude Desktop. It provides comprehensive email functionality including configuration management, sending emails, and reading messages with semantic search capabilities.

## Features

- 📧 **Email Configuration Management**: List, add, update, and delete email configurations
- 📨 **Send Emails**: Send emails using specified configurations
- 📖 **Read Emails**: Access and read the latest unread emails
- 🔍 **Semantic Search**: Advanced email search with AI-powered semantic understanding
- 🗃️ **Database Storage**: Efficient email storage using DuckDB
- 🔌 **MCP Integration**: Native support for Claude Desktop integration

## Installation

### From PyPI (Recommended)

```bash
pip install mcp-email-client
```

### From Source

1. Clone the repository:
    ```bash
    git clone https://github.com/gamalan/mcp-email-client.git
    cd mcp-email-client
    ```

2. Install uv (if not already installed):
    
    **Linux/MacOS:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    
    **Windows:**
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

3. Install dependencies:
    ```bash
    uv sync
    ```

## Quick Start

After installation, you can run the MCP email client directly:

```bash
mcp-email-client
```

## Configuration

Configuration example using Claude Desktop
```json
{
  "mcpServers": {
    "mcp_email_client": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "D:\\Project\\RepoPath", 
        "mcp_email_client"
      ]
    }
  }
}
```

**For VS Code:**

```json
{
    "servers": {
        "mcp-email-client": {
            "type": "stdio",
            "command": "mcp-email-client",
            "args": []
        }
    }
}
```

**For development/local installation:**

```json
{
    "servers": {
        "mcp-email-client": {
            "type": "stdio",
            "command": "/path/to/uv",
            "args": [
                "run",
                "--directory",
                "/path/to/repo",
                "run_mcp_server.py"
            ]
        }
    }
}
```

## Usage

The MCP Email Client provides several tools that can be used through Claude Desktop:

- **List Configurations**: View all configured email accounts
- **Add Configuration**: Add new email account settings
- **Update Configuration**: Modify existing email configurations
- **Delete Configuration**: Remove email configurations
- **Send Email**: Send emails through configured accounts
- **Read Emails**: Access latest unread emails
- **Search Emails**: Semantic search through email content

## Requirements

- Python 3.12 or higher
- DuckDB for local email storage
- Internet connection for email operations
- Valid email account credentials (IMAP/SMTP)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub repository](https://github.com/gamalan/mcp-email-client/issues).

## Changelog

### v0.1.0
- Initial release
- Basic email configuration management
- Email sending and reading functionality
- MCP integration for Claude Desktop
- Semantic search capabilities