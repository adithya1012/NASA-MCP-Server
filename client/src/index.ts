import { Anthropic } from "@anthropic-ai/sdk";
import {
  MessageParam,
  Tool,
} from "@anthropic-ai/sdk/resources/messages/messages.mjs";
import OpenAI from "openai";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import dotenv from "dotenv";
import path from "path";

// Provider type
type Provider = "claude" | "openai";
dotenv.config();

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

export class MCPClient {
  private mcp: Client;
  private anthropic: Anthropic | null = null;
  private openai: OpenAI | null = null;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];
  private openaiTools: OpenAI.Chat.Completions.ChatCompletionTool[] = [];
  private provider: Provider;

  constructor(provider: Provider = "openai") {
    this.provider = provider;
    if (provider === "claude") {
      if (!ANTHROPIC_API_KEY) {
        throw new Error("ANTHROPIC_API_KEY is not set");
      }
      this.anthropic = new Anthropic({
        apiKey: ANTHROPIC_API_KEY,
      });
    } else if (provider === "openai") {
      if (!OPENAI_API_KEY) {
        throw new Error("OPENAI_API_KEY is not set");
      }
      this.openai = new OpenAI({
        apiKey: OPENAI_API_KEY,
      });
    }

    this.mcp = new Client({ name: "mcp-client-cli", version: "1.0.0" });
  }

  async connectToServer(serverScriptPath: string, venvPath?: string) {
    try {
      console.log(`Attempting to connect to server: ${serverScriptPath}`);

      const isJs = serverScriptPath.endsWith(".js");
      const isPy = serverScriptPath.endsWith(".py");

      if (!isJs && !isPy) {
        throw new Error("Server script must be a .js or .py file");
      }

      let command: string;
      let args: string[];

      if (isPy) {
        if (venvPath) {
          // Use the Python executable from the virtual environment
          const pythonExecutable =
            process.platform === "win32"
              ? path.join(venvPath, "Scripts", "python.exe")
              : path.join(venvPath, "bin", "python");
          command = pythonExecutable;
          args = [serverScriptPath];
          console.log(`Using venv Python: ${command}`);
        } else {
          // Use system Python
          command = process.platform === "win32" ? "python" : "python3";
          args = [serverScriptPath];
        }
      } else {
        command = process.execPath;
        args = [serverScriptPath];
      }

      console.log(`Executing: ${command} ${args.join(" ")}`);

      this.transport = new StdioClientTransport({
        command,
        args,
      });

      console.log("Transport created, attempting to connect...");
      await this.mcp.connect(this.transport);
      console.log("Connected to MCP server!");

      const toolsResult = await this.mcp.listTools();
      console.log(
        "Available tools:",
        toolsResult.tools.map((t) => t.name)
      );

      // Format tools for Claude
      this.tools = toolsResult.tools.map((tool) => {
        return {
          name: tool.name,
          description: tool.description,
          input_schema: tool.inputSchema,
        };
      });

      // Format tools for OpenAI
      this.openaiTools = toolsResult.tools.map((tool) => {
        return {
          type: "function" as const,
          function: {
            name: tool.name,
            description: tool.description,
            parameters: tool.inputSchema,
          },
        };
      });

      console.log(
        `Connected to server with ${this.tools.length} tools (${this.provider}):`,
        this.tools.map(({ name }) => name)
      );
    } catch (e) {
      console.error("Failed to connect to MCP server: ", e);
      throw e;
    }
  }

  async processQueryClaude(query: string): Promise<string> {
    if (!this.anthropic) {
      throw new Error("Anthropic client not initialized");
    }

    const messages: MessageParam[] = [
      {
        role: "user",
        content: query,
      },
    ];

    try {
      const response = await this.anthropic.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 4000,
        messages,
        tools: this.tools,
      });

      const finalText = [];

      for (const content of response.content) {
        if (content.type === "text") {
          finalText.push(content.text);
        } else if (content.type === "tool_use") {
          const toolName = content.name;
          const toolArgs = content.input as
            | { [x: string]: unknown }
            | undefined;

          console.log(`Calling tool: ${toolName} with args:`, toolArgs);

          try {
            const result = await this.mcp.callTool({
              name: toolName,
              arguments: toolArgs,
            });

            console.log(`Tool ${toolName} result:`, result);

            // Create follow-up message with tool result
            messages.push(
              {
                role: "assistant",
                content: [
                  {
                    type: "tool_use",
                    id: content.id,
                    name: toolName,
                    input: toolArgs,
                  },
                ],
              },
              {
                role: "user",
                content: [
                  {
                    type: "tool_result",
                    tool_use_id: content.id,
                    content: JSON.stringify(result.content),
                  },
                ],
              }
            );

            const followUpResponse = await this.anthropic.messages.create({
              model: "claude-3-5-sonnet-20241022",
              max_tokens: 4000,
              messages,
              tools: this.tools,
            });

            // Add the follow-up response
            for (const followUpContent of followUpResponse.content) {
              if (followUpContent.type === "text") {
                finalText.push(followUpContent.text);
              }
            }
          } catch (toolError) {
            console.error(`Error calling tool ${toolName}:`, toolError);
            finalText.push(`[Tool ${toolName} failed: ${toolError}]`);
          }
        }
      }

      return finalText.join("\n");
    } catch (error) {
      console.error("Error in Claude processing:", error);
      throw error;
    }
  }

  async processQueryOpenAI(query: string): Promise<string> {
    if (!this.openai) {
      throw new Error("OpenAI client not initialized");
    }

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      {
        role: "user",
        content: query,
      },
    ];

    try {
      const response = await this.openai.chat.completions.create({
        model: "gpt-4o",
        max_tokens: 4000,
        messages,
        tools: this.openaiTools,
        tool_choice: "auto",
      });

      const finalText = [];
      const message = response.choices[0]?.message;

      if (!message) {
        throw new Error("No response from OpenAI");
      }

      // Add assistant's text response
      if (message.content) {
        finalText.push(message.content);
      }

      // Handle tool calls
      if (message.tool_calls && message.tool_calls.length > 0) {
        // Add assistant message to conversation
        messages.push(message);

        for (const toolCall of message.tool_calls) {
          const toolName = toolCall.function.name;
          const toolArgs = JSON.parse(toolCall.function.arguments);

          console.log(`Calling tool: ${toolName} with args:`, toolArgs);

          try {
            const result = await this.mcp.callTool({
              name: toolName,
              arguments: toolArgs,
            });

            console.log(`Tool ${toolName} result:`, result);

            // Add tool result to messages
            messages.push({
              role: "tool",
              tool_call_id: toolCall.id,
              content: JSON.stringify(result.content),
            });
          } catch (error) {
            console.error(`Error calling tool ${toolName}:`, error);
            messages.push({
              role: "tool",
              tool_call_id: toolCall.id,
              content: `Error: ${error}`,
            });
          }
        }

        // Get final response after tool execution
        const followUpResponse = await this.openai.chat.completions.create({
          model: "gpt-4o",
          max_tokens: 4000,
          messages,
          tools: this.openaiTools,
          tool_choice: "auto",
        });

        const followUpMessage = followUpResponse.choices[0]?.message;
        if (followUpMessage?.content) {
          finalText.push(followUpMessage.content);
        }
      }

      return finalText.join("\n");
    } catch (error) {
      console.error("Error in OpenAI processing:", error);
      throw error;
    }
  }

  async processQuery(query: string): Promise<string> {
    if (this.provider === "claude") {
      return this.processQueryClaude(query);
    } else {
      return this.processQueryOpenAI(query);
    }
  }

  async cleanup() {
    if (this.transport) {
      try {
        await this.mcp.close();
      } catch (error) {
        console.error("Error closing MCP connection:", error);
      }
    }
  }

  getProvider(): Provider {
    return this.provider;
  }

  switchProvider(provider: Provider) {
    if (provider === this.provider) return;

    this.provider = provider;

    if (provider === "claude") {
      if (!ANTHROPIC_API_KEY) {
        throw new Error("ANTHROPIC_API_KEY is not set");
      }
      this.anthropic = new Anthropic({
        apiKey: ANTHROPIC_API_KEY,
      });
      this.openai = null;
    } else if (provider === "openai") {
      if (!OPENAI_API_KEY) {
        throw new Error("OPENAI_API_KEY is not set");
      }
      this.openai = new OpenAI({
        apiKey: OPENAI_API_KEY,
      });
      this.anthropic = null;
    }

    console.log(`Switched to ${provider.toUpperCase()}`);
  }
}
