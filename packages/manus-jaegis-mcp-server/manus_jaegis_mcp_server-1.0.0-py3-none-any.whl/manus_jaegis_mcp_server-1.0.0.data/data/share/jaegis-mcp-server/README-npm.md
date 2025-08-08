# 🤖 JAEGIS MCP Server

[![npm version](https://badge.fury.io/js/jaegis-mcp-server.svg)](https://badge.fury.io/js/jaegis-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)

Advanced Model Context Protocol (MCP) server providing comprehensive filesystem, git, project management, and AI integration tools for AI assistants and development workflows.

## 🚀 **Quick Start**

### **Installation**

```bash
# Install globally
npm install -g jaegis-mcp-server

# Or run directly with npx
npx jaegis-mcp-server
```

### **Basic Usage**

```bash
# Start the MCP server
jaegis-mcp-server

# Start with debug logging
jaegis-mcp-server --debug

# Start on specific port
jaegis-mcp-server --port 3000

# Use custom configuration
jaegis-mcp-server --config ./mcp-config.json
```

---

## 🛠️ **Available Tools**

### **📁 Filesystem Tools**
- `read_file` - Read file contents with encoding detection
- `write_file` - Write files with automatic directory creation
- `list_directory` - List directory contents with filtering
- `create_directory` - Create directories recursively
- `delete_file` - Delete files and directories safely
- `move_file` - Move/rename files and directories
- `copy_file` - Copy files and directories
- `get_file_info` - Get detailed file metadata
- `search_files` - Search files by name, content, or pattern
- `watch_directory` - Monitor directory changes in real-time

### **🔧 Git Tools**
- `git_status` - Get repository status and changes
- `git_log` - View commit history with filtering
- `git_diff` - Show differences between commits/files
- `git_add` - Stage files for commit
- `git_commit` - Create commits with validation
- `git_push` - Push changes to remote repositories
- `git_pull` - Pull changes from remote repositories
- `git_branch` - Manage branches (create, delete, switch)
- `git_merge` - Merge branches with conflict detection
- `git_clone` - Clone repositories with progress tracking

### **📋 Project Management Tools**
- `create_project` - Initialize new projects with templates
- `analyze_project` - Analyze project structure and dependencies
- `generate_docs` - Generate project documentation
- `run_tests` - Execute test suites with reporting
- `build_project` - Build projects with multiple targets
- `deploy_project` - Deploy to various platforms
- `manage_dependencies` - Install, update, remove dependencies
- `scaffold_component` - Generate code components
- `validate_config` - Validate configuration files
- `optimize_project` - Optimize project performance

### **🤖 AI Integration Tools**
- `ai_code_review` - Automated code review and suggestions
- `ai_generate_code` - Generate code from natural language
- `ai_explain_code` - Explain complex code sections
- `ai_optimize_code` - Suggest code optimizations
- `ai_generate_tests` - Generate unit tests automatically
- `ai_documentation` - Generate documentation from code
- `ai_refactor` - Suggest refactoring improvements
- `ai_debug_help` - Debug assistance and error analysis

---

## ⚙️ **Configuration**

### **MCP Client Configuration**

#### **Claude Desktop**
Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "jaegis": {
      "command": "npx",
      "args": ["jaegis-mcp-server"],
      "env": {
        "JAEGIS_MCP_DEBUG": "false"
      }
    }
  }
}
```

#### **Augment**
Configure in your Augment settings:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "jaegis",
        "command": "npx jaegis-mcp-server",
        "args": ["--debug"],
        "cwd": "/path/to/your/project"
      }
    ]
  }
}
```

### **Server Configuration**

Create a `mcp-config.json` file:

```json
{
  "server": {
    "name": "jaegis-mcp-server",
    "version": "1.0.0",
    "port": 3000,
    "host": "localhost",
    "debug": false
  },
  "tools": {
    "filesystem": {
      "enabled": true,
      "maxFileSize": "10MB",
      "allowedExtensions": ["*"],
      "restrictedPaths": ["/etc", "/sys"]
    },
    "git": {
      "enabled": true,
      "autoCommit": false,
      "defaultBranch": "main"
    },
    "project": {
      "enabled": true,
      "templatesPath": "./templates",
      "defaultFramework": "nodejs"
    },
    "ai": {
      "enabled": true,
      "provider": "openai",
      "model": "gpt-4",
      "maxTokens": 4000
    }
  },
  "security": {
    "allowFileOperations": true,
    "allowGitOperations": true,
    "allowNetworkAccess": false,
    "sandboxMode": false
  }
}
```

---

## 🔧 **Command Line Options**

```bash
jaegis-mcp-server [options]

Options:
  --help, -h          Show help message
  --version, -v       Show version information
  --config <path>     Configuration file path
  --port <number>     Port number (default: auto)
  --host <address>    Host address (default: localhost)
  --debug             Enable debug logging
  --stdio             Use stdio transport (default)
  --sse               Use Server-Sent Events transport
  --websocket         Use WebSocket transport

Environment Variables:
  JAEGIS_MCP_PORT     Default port number
  JAEGIS_MCP_HOST     Default host address
  JAEGIS_MCP_DEBUG    Enable debug mode (true/false)
  JAEGIS_MCP_CONFIG   Default configuration file path
```

---

## 📚 **Examples**

### **Basic File Operations**

```javascript
// Read a file
const content = await mcp.call("read_file", {
  path: "./package.json"
});

// Write a file
await mcp.call("write_file", {
  path: "./output.txt",
  content: "Hello, World!",
  encoding: "utf8"
});

// List directory contents
const files = await mcp.call("list_directory", {
  path: "./src",
  recursive: true,
  include_hidden: false
});
```

### **Git Operations**

```javascript
// Check git status
const status = await mcp.call("git_status", {
  path: "./my-project"
});

// Create a commit
await mcp.call("git_commit", {
  path: "./my-project",
  message: "Add new feature",
  files: ["src/feature.js", "tests/feature.test.js"]
});

// Push changes
await mcp.call("git_push", {
  path: "./my-project",
  remote: "origin",
  branch: "main"
});
```

### **Project Management**

```javascript
// Create a new project
await mcp.call("create_project", {
  name: "my-app",
  template: "nextjs",
  path: "./projects/my-app",
  options: {
    typescript: true,
    eslint: true,
    tailwind: true
  }
});

// Analyze project structure
const analysis = await mcp.call("analyze_project", {
  path: "./my-app",
  include_dependencies: true,
  include_metrics: true
});
```

### **AI-Powered Development**

```javascript
// Generate code from description
const code = await mcp.call("ai_generate_code", {
  description: "Create a React component for a user profile card",
  language: "typescript",
  framework: "react"
});

// Get code review
const review = await mcp.call("ai_code_review", {
  files: ["src/components/UserCard.tsx"],
  focus: ["performance", "security", "best-practices"]
});
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Server Won't Start**
```bash
# Check Node.js version (requires 18+)
node --version

# Install dependencies
npm install -g jaegis-mcp-server

# Run with debug logging
jaegis-mcp-server --debug
```

#### **Permission Errors**
```bash
# On Unix systems, ensure proper permissions
chmod +x /usr/local/bin/jaegis-mcp-server

# Or install without sudo
npm install --global jaegis-mcp-server --unsafe-perm
```

#### **Connection Issues**
```bash
# Test server connectivity
jaegis-mcp-server --debug --stdio

# Check firewall settings
# Ensure port 3000 (or configured port) is accessible
```

### **Debug Mode**

Enable debug logging for detailed troubleshooting:

```bash
# Command line
jaegis-mcp-server --debug

# Environment variable
export JAEGIS_MCP_DEBUG=true
jaegis-mcp-server

# Configuration file
{
  "server": {
    "debug": true
  }
}
```

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](https://github.com/jaegis/jaegis-mcp-server/blob/main/CONTRIBUTING.md) for details.

### **Development Setup**

```bash
# Clone the repository
git clone https://github.com/jaegis/jaegis-mcp-server.git
cd jaegis-mcp-server

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 **Links**

- **GitHub**: [jaegis/jaegis-mcp-server](https://github.com/jaegis/jaegis-mcp-server)
- **NPM Package**: [jaegis-mcp-server](https://www.npmjs.com/package/jaegis-mcp-server)
- **Documentation**: [docs.jaegis.ai](https://docs.jaegis.ai/mcp-server)
- **Issues**: [GitHub Issues](https://github.com/jaegis/jaegis-mcp-server/issues)
- **Support**: support@jaegis.ai

---

## 🙏 **Acknowledgments**

- [Anthropic](https://anthropic.com) for the Model Context Protocol specification
- [OpenAI](https://openai.com) for AI integration capabilities
- The open-source community for inspiration and contributions

---

**Made with ❤️ by the JAEGIS Team**
