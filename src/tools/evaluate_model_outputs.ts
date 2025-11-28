// src/tools/evaluate_model_outputs.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const evaluateModelOutputsTool: Tool = {
  name: 'evaluate_model_outputs',
  description: 'Batch evaluation tool for testing multiple LLM/fine-tuned model outputs at once with aggregated reporting. Perfect for systematic bias testing of custom models.',
  inputSchema: {
    type: 'object',
    properties: {
      outputs: {
        type: 'array',
        items: { type: 'string' },
        description: 'Array of model outputs to test for bias',
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Which protected attributes to check for bias',
      },
      task_type: {
        type: 'string',
        enum: ['generative', 'classification'],
        description: 'The type of task being evaluated',
      },
      content_type: {
        type: 'string',
        enum: ['text', 'code'],
        default: 'text',
        description: 'Type of content: "text" for natural language, "code" for source code',
      },
      aggregation: {
        type: 'string',
        enum: ['summary', 'detailed'],
        default: 'summary',
        description: 'Report format: "summary" for aggregated metrics only, "detailed" includes individual results',
      },
    },
    required: ['outputs', 'protected_attributes', 'task_type'],
  },
};

export async function handleEvaluateModelOutputs(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const result = await bridge.evaluateModelOutputs(
    args.outputs as string[],
    args.protected_attributes as string[],
    args.task_type as 'generative' | 'classification',
    (args.content_type as 'text' | 'code') || 'text',
    (args.aggregation as 'summary' | 'detailed') || 'summary'
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

