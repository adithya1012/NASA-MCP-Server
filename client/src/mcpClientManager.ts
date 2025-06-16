import { spawn, ChildProcess } from "child_process";
import { EventEmitter } from "events";
import { MCPClient } from "./index.js";

export interface MCPClientConfig {
  scriptPath: string;
  pythonPath: string;
  venvPath: string;
  provider: string;
}

export class MCPClientManager extends EventEmitter {
  private static instance: MCPClientManager | null = null;
  private mcpClient: MCPClient | null = null;
  private config: MCPClientConfig | null = null;
  private isInitialized: boolean = false;
  private messageQueue: Array<{
    query: string;
    resolve: (response: any) => void;
    reject: (error: any) => void;
  }> = [];

  private constructor() {
    super();
  }

  public static getInstance(): MCPClientManager {
    if (!MCPClientManager.instance) {
      MCPClientManager.instance = new MCPClientManager();
    }
    return MCPClientManager.instance;
  }

  public async initialize(config: MCPClientConfig): Promise<void> {
    if (this.isInitialized) {
      console.log("MCP Client already initialized");
      return;
    }

    this.config = config;

    try {
      console.log("Creating MCP Client instance...");

      // Create MCP client with specified provider
      this.mcpClient = new MCPClient(config.provider as "claude" | "openai");

      console.log(`Connecting to MCP server: ${config.scriptPath}`);

      // Connect to the MCP server
      await this.mcpClient.connectToServer(config.scriptPath, config.venvPath);

      this.isInitialized = true;

      // Process any queued messages
      this.processMessageQueue();

      console.log("MCP Client initialized successfully");
      this.emit("ready");
    } catch (error) {
      console.error("Failed to initialize MCP Client:", error);
      this.isInitialized = false;
      throw error;
    }
  }

  public async processQuery(query: string): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.isInitialized || !this.mcpClient) {
        // Queue the message if not initialized
        this.messageQueue.push({ query, resolve, reject });
        return;
      }

      // Process query through MCP client
      this.mcpClient.processQuery(query).then(resolve).catch(reject);
    });
  }

  public async sendMessage(message: any): Promise<any> {
    // Maintain backward compatibility
    const query =
      typeof message === "string" ? message : JSON.stringify(message);
    return this.processQuery(query);
  }

  private async processMessageQueue() {
    console.log(`Processing ${this.messageQueue.length} queued messages`);

    while (this.messageQueue.length > 0) {
      const { query, resolve, reject } = this.messageQueue.shift()!;

      try {
        const response = await this.processQuery(query);
        resolve(response);
      } catch (error) {
        reject(error);
      }
    }
  }

  public isReady(): boolean {
    return this.isInitialized && this.mcpClient !== null;
  }

  public async shutdown(): Promise<void> {
    if (this.mcpClient) {
      try {
        await this.mcpClient.cleanup();
      } catch (error) {
        console.error("Error during MCP client cleanup:", error);
      }
      this.mcpClient = null;
      this.isInitialized = false;
    }
  }

  public getConfig(): MCPClientConfig | null {
    return this.config;
  }

  public switchProvider(provider: "claude" | "openai"): void {
    if (this.config) {
      this.config.provider = provider;
      // Note: You might want to reinitialize the client here
      console.log(`Provider switched to: ${provider}`);
    }
  }
}
