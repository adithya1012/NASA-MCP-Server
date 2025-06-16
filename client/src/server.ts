import { WebSocketServer, WebSocket } from "ws";
import express from "express";
import cors from "cors";
import { MCPClientManager, MCPClientConfig } from "./mcpClientManager.js";

const app = express();
const port: number = 8090;
const httpPort: number = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// MCP Client configuration
const mcpConfig: MCPClientConfig = {
  scriptPath: "../server/mcp-python/tools/index.py",
  pythonPath: "../server/mcp-python/.venv",
  venvPath: "../server/mcp-python/.venv",
  provider: "openai",
};

// Initialize MCP Client Manager
const mcpManager = MCPClientManager.getInstance();

// Task Handler Class
class TaskHandler {
  async handleTask(
    data: Buffer | string,
    callback: (response: string) => void
  ) {
    try {
      const message = data.toString();
      console.log("Received message:", message);

      let parsedMessage;
      try {
        parsedMessage = JSON.parse(message);
      } catch {
        // If not JSON, treat as plain text query
        parsedMessage = { query: message };
      }

      // Check if MCP client is ready
      if (!mcpManager.isReady()) {
        callback(
          JSON.stringify({
            error: "MCP Client not ready",
            status: "initializing",
          })
        );
        return;
      }

      // Send query to MCP client for processing
      const response = await mcpManager.processQuery(
        parsedMessage.query || parsedMessage
      );
      callback(
        JSON.stringify({
          success: true,
          data: response,
          timestamp: new Date().toISOString(),
        })
      );
    } catch (error) {
      console.error("Task handling error:", error);
      callback(
        JSON.stringify({
          error: error instanceof Error ? error.message : "Unknown error",
          timestamp: new Date().toISOString(),
        })
      );
    }
  }
}

const taskHandler = new TaskHandler();

// Initialize WebSocket Server
const wss = new WebSocketServer({ port }, () => {
  console.log(`WebSocket server is listening on ws://localhost:${port}`);
});

wss.on("connection", (ws: WebSocket) => {
  console.log("Client connected to WebSocket");

  ws.send(
    JSON.stringify({
      type: "connection",
      message: "Welcome to the MCP WebSocket server!",
      mcpReady: mcpManager.isReady(),
    })
  );

  ws.on("message", async (data: Buffer) => {
    await taskHandler.handleTask(data, (response) => {
      ws.send(response);
    });
  });

  ws.on("close", () => {
    console.log("WebSocket client disconnected");
  });

  ws.on("error", (error) => {
    console.error("WebSocket error:", error);
  });
});

// HTTP REST API endpoints
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    mcpReady: mcpManager.isReady(),
    timestamp: new Date().toISOString(),
  });
});

app.post("/mcp/execute", async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    if (!mcpManager.isReady()) {
      return res.status(503).json({
        error: "MCP Client not ready",
        status: "initializing",
      });
    }

    const response = await mcpManager.processQuery(message);
    res.json({
      success: true,
      data: response,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("HTTP API error:", error);
    res.status(500).json({
      error: error instanceof Error ? error.message : "Unknown error",
      timestamp: new Date().toISOString(),
    });
  }
});

app.get("/mcp/status", (req, res) => {
  res.json({
    ready: mcpManager.isReady(),
    config: mcpManager.getConfig(),
    timestamp: new Date().toISOString(),
  });
});

// Start HTTP server
app.listen(httpPort, () => {
  console.log(`HTTP server is listening on http://localhost:${httpPort}`);
});

// Initialize MCP Client on server start
async function initializeServer() {
  try {
    console.log("Initializing MCP Client...");
    await mcpManager.initialize(mcpConfig);
    console.log("Server fully initialized and ready to accept connections");
  } catch (error) {
    console.error("Failed to initialize MCP Client:", error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on("SIGINT", async () => {
  console.log("Shutting down server...");
  await mcpManager.shutdown();
  process.exit(0);
});

process.on("SIGTERM", async () => {
  console.log("Shutting down server...");
  await mcpManager.shutdown();
  process.exit(0);
});

// Start the server
initializeServer();
