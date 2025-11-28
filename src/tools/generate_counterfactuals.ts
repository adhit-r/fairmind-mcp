// src/tools/generate_counterfactuals.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const generateCounterfactualsTool: Tool = {
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
};

export async function handleGenerateCounterfactuals(
  bridge: PythonBridge,
  args: any
): Promise<any> {
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

