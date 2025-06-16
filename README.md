# MCP WebSocket Server

A WebSocket server that integrates with Model Context Protocol (MCP) clients to provide tool-enabled AI conversations.

## Project Structure

```
project-root/
├── src/
│   ├── server.ts              # Main WebSocket server
│   ├── mcpClientManager.ts    # MCP client manager
│   └── index.ts               # MCP client implementation
├── package.json
├── tsconfig.json
├── .env                       # Your environment variables
└── .env.example              # Environment template
```

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. File Organization

Create the `src` folder and move your files:

```bash
mkdir -p src
# Move your files to src/ directory:
# - server.ts → src/server.ts
# - mcpClientManager.ts → src/mcpClientManager.ts
# - index.ts → src/index.ts
```

### 4. Update MCP Configuration

In `src/server.ts`, update the `mcpConfig` object to point to your actual MCP server:

```typescript
const mcpConfig: MCPClientConfig = {
  scriptPath: "../path/to/your/mcp-server.py", // Update this path
  pythonPath: "../path/to/your/venv", // Update this path
  venvPath: "../path/to/your/venv", // Update this path
  provider: "openai", // or "claude"
};
```

## Running the Server

### Development Mode

```bash
npm run dev
```

### Production Mode

```bash
npm run build
npm start
```

## Usage

### WebSocket Connection

Connect to the WebSocket server at:

```
ws://localhost:8090
```

Send messages as JSON:

```json
{
  "query": "What is the weather like today?"
}
```

Or send plain text messages directly.

### HTTP API

#### Health Check

```bash
GET http://localhost:3000/health
```

#### Execute Query

```bash
POST http://localhost:3000/mcp/execute
Content-Type: application/json

{
  "message": "Your question here"
}
```

#### Check MCP Status

```bash
GET http://localhost:3000/mcp/status
```

## Features

- **WebSocket Server**: Real-time communication on port 8090
- **HTTP REST API**: HTTP endpoints on port 3000
- **MCP Integration**: Seamless tool calling through MCP protocol
- **Multi-Provider Support**: Both OpenAI and Claude support
- **Error Handling**: Comprehensive error handling and logging
- **Message Queuing**: Queues messages when MCP client is initializing

## Architecture

1. **Client** connects via WebSocket or HTTP
2. **Server** receives messages and forwards to **MCP Client Manager**
3. **MCP Client Manager** processes queries through **MCP Client**
4. **MCP Client** communicates with **MCP Server** and **LLM Provider**
5. **Tools** are executed as needed
6. **Response** flows back through the chain to the client

## Troubleshooting

### Common Issues

1. **MCP Client not ready**: Ensure your MCP server path is correct and the Python environment is set up properly.

2. **API Key errors**: Make sure your `.env` file contains valid API keys for your chosen provider.

3. **Connection errors**: Check that your MCP server script exists and is executable.

4. **Port conflicts**: Ensure ports 8090 and 3000 are available.

### Debug Logs

The server provides comprehensive logging. Check the console output for detailed error messages and connection status.
