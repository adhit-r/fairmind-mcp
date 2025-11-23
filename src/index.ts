// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from './python_bridge.js';

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

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'evaluate_bias',
      description: 'Evaluates text or data for bias against protected attributes using Fairlearn metrics. Returns a token-optimized TOON-formatted report.',
      inputSchema: {
        type: 'object',
        properties: {
          content: {
            type: 'string',
            description: 'The text or dataset row to evaluate for bias',
          },
          protected_attribute: {
            type: 'string',
            description: 'The protected attribute to check (e.g., "gender", "race", "age")',
            enum: ['gender', 'race', 'age', 'disability'],
          },
          task_type: {
            type: 'string',
            description: 'The type of task being evaluated',
            enum: ['generative', 'classification'],
          },
        },
        required: ['content', 'protected_attribute', 'task_type'],
      },
    },
    {
      name: 'generate_counterfactuals',
      description: 'Generates alternative text suggestions to reduce bias using LiteRT-powered inference. Returns a list of counterfactual alternatives.',
      inputSchema: {
        type: 'object',
        properties: {
          content: {
            type: 'string',
            description: 'The text to generate counterfactuals for',
          },
          sensitive_group: {
            type: 'string',
            description: 'The sensitive group to focus on (e.g., "gender", "race")',
            enum: ['gender', 'race', 'age'],
          },
        },
        required: ['content', 'sensitive_group'],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'evaluate_bias': {
        const result = await bridge.evaluateBias(
          args.content as string,
          args.protected_attribute as string,
          args.task_type as 'generative' | 'classification'
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'generate_counterfactuals': {
        const result = await bridge.generateCounterfactuals(
          args.content as string,
          args.sensitive_group as string
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
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
