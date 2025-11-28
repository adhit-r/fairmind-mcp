// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from './python_bridge.js';
import { getAllTools, handleTool } from './tools/registry.js';

const server = new Server(
  {
    name: 'fairmind-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const bridge = new PythonBridge();

// Register all tools from registry
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: getAllTools(),
}));

// Route tool calls to appropriate handlers
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const result = await handleTool(name, bridge, args);
    return result;
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('FairMind MCP server running on stdio');
}

main().catch(console.error);

// Cleanup on exit
process.on('SIGINT', () => {
  bridge.destroy();
  process.exit(0);
});

process.on('SIGTERM', () => {
  bridge.destroy();
  process.exit(0);
});
