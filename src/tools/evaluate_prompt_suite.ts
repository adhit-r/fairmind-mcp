// src/tools/evaluate_prompt_suite.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const evaluatePromptSuiteTool: Tool = {
  name: 'evaluate_prompt_suite',
  description: 'Systematic prompt suite testing for LLMs/fine-tuned models. Tests model with predefined prompts and tracks bias metrics over time. Ideal for fine-tuning validation and continuous monitoring.',
  inputSchema: {
    type: 'object',
    properties: {
      prompts: {
        type: 'array',
        items: { type: 'string' },
        description: 'Array of test prompts',
      },
      model_outputs: {
        type: 'array',
        items: { type: 'string' },
        description: 'Corresponding model outputs (must match prompts length)',
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Which protected attributes to check for bias',
      },
      suite_name: {
        type: 'string',
        description: 'Optional name for tracking this test suite',
      },
      task_type: {
        type: 'string',
        enum: ['generative', 'classification'],
        default: 'generative',
        description: 'The type of task being evaluated',
      },
      content_type: {
        type: 'string',
        enum: ['text', 'code'],
        default: 'text',
        description: 'Type of content: "text" for natural language, "code" for source code',
      },
      previous_results: {
        type: 'object',
        description: 'Optional previous suite results for comparison tracking',
      },
    },
    required: ['prompts', 'model_outputs', 'protected_attributes'],
  },
};

export async function handleEvaluatePromptSuite(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const result = await bridge.evaluatePromptSuite(
    args.prompts as string[],
    args.model_outputs as string[],
    args.protected_attributes as string[],
    args.suite_name as string | undefined,
    (args.task_type as 'generative' | 'classification') || 'generative',
    (args.content_type as 'text' | 'code') || 'text',
    args.previous_results as any
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

