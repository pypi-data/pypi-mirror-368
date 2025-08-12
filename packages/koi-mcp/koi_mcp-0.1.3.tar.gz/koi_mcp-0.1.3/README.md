# KOI MCP Server

A Model Context Protocol (MCP) server for KOI Security that connects to the KOI API using environment variables. This server enables Claude Desktop to interact with KOI Security's API for enhanced security analysis and monitoring capabilities.

## Prerequisites

- Python 3.10 or higher
- A KOI API token (obtainable from the KOI Security app)


## Setup Options

### Option 1: Claude Desktop Integration - Using package

1. **Install the package with any package manager**
   ```bash
   pip install koi-mcp
   ```
2. Make sure where the package was installed, you will need the path in the next step.
   ```bash
   which koi-mcp
   ```

2. **Configure Claude Desktop**
   - Use the example in `example_claude_config_package.json` file
    - **IMPORTANT**:
        - Claude Desktop looks for packages in specific paths so make sure you package exists in one of the paths, or symlinked to it:
          - '/usr/local/bin',
          - '/opt/homebrew/bin',
          - '/usr/bin',
          - '/usr/bin',
          - '/bin',
          - '/usr/sbin',
          - '/sbin'
        - Replace `YOUR KOI API TOKEN HERE` with your actual KOI API token
   - Edit your Claude Desktop config file (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json`)
   - Add the KOI MCP server configuration to the `mcpServers` section

   ```json
    {
      "mcpServers": {
        "koi": {
        "command": "uv",
        "args": [
          "run",
          "koi-mcp"
        ],
        "env": {
          "KOI_API_TOKEN": "YOUR KOI API TOKEN HERE"
        }
        }
      }
    }
   ```

   **Note**: You can obtain your KOI API token from the KOI Security app by going to Settings → API Access.

3. **Restart Claude Desktop**
   - Close Claude Desktop completely
   - Reopen the application for the changes to take effect


### Option 2: Claude Desktop Integration - Using local directory

1. **Download or clone this repository**
   ```bash
   git clone https://github.com/koi-sec/koi-mcp-server
   cd koi-mcp
   ```

2. **Configure Claude Desktop**
   - Use the example in `example_claude_config.json` file
    - **IMPORTANT**:
        - Update the path in the `args` array to point to your local repository location
        - Replace `YOUR KOI API TOKEN HERE` with your actual KOI API token
   - Edit your Claude Desktop config file (usually located at `~/Library/Application Support/Claude/claude_desktop_config.json`)
   - Add the KOI MCP server configuration to the `mcpServers` section


   ```json
   {
     "mcpServers": {
       "koi": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/koi-mcp",
           "run",
           "koi_mcp"
         ],
         "env": {
           "KOI_API_TOKEN": "YOUR KOI API TOKEN HERE"
         }
       }
     }
   }
   ```

   **Note**: You can obtain your KOI API token from the KOI Security app by going to Settings → API Access.

3. **Restart Claude Desktop**
   - Close Claude Desktop completely
   - Reopen the application for the changes to take effect

### Option 3: Standalone Server Installation

1. **Install the package via pip**
   ```bash
   pip install koi-mcp
   ```

2. **Run the server**
   ```bash
   koi-mcp
   ```

   The server communicates using stdio and can be integrated with any MCP-compatible client.

## Environment Variables

- `KOI_API_TOKEN`: Your KOI Security API token (required)
