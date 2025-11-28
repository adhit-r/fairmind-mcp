// src/tools/evaluate_bias.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const evaluateBiasTool: Tool = {
  name: 'evaluate_bias',
  description: 'Evaluates text, code, or data for bias against protected attributes. Use content_type="code" for source code analysis (comments, variable names, algorithmic bias). Use content_type="text" for natural language content. Supports single attribute (backward compatible) or multiple attributes via protected_attributes array.',
  inputSchema: {
    type: 'object',
    properties: {
      content: {
        type: 'string',
        description: 'The text, code, or dataset row to evaluate for bias',
      },
      protected_attribute: {
        type: 'string',
        description: 'The protected attribute to check (e.g., "gender", "race", "age"). Use this for single attribute (backward compatible).',
        enum: ['gender', 'race', 'age', 'disability'],
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Array of protected attributes to check simultaneously. If provided, will check multiple attributes and detect intersectional bias.',
      },
      task_type: {
        type: 'string',
        description: 'The type of task being evaluated',
        enum: ['generative', 'classification'],
      },
      content_type: {
        type: 'string',
        description: 'Type of content: "text" for natural language, "code" for source code',
        enum: ['text', 'code'],
        default: 'text',
      },
    },
    required: ['content', 'task_type'],
  },
};

export async function handleEvaluateBias(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const protectedAttributes = args.protected_attributes as string[] | undefined;
  const protectedAttribute = args.protected_attribute as string | undefined;
  
  let result;
  if (protectedAttributes && Array.isArray(protectedAttributes)) {
    result = await bridge.evaluateBias(
      args.content as string,
      protectedAttribute || '',
      args.task_type as 'generative' | 'classification',
      (args.content_type as 'text' | 'code') || 'text',
      protectedAttributes
    );
  } else {
    result = await bridge.evaluateBias(
      args.content as string,
      protectedAttribute as string,
      args.task_type as 'generative' | 'classification',
      (args.content_type as 'text' | 'code') || 'text'
    );
  }
  
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(result, null, 2),
      },
    ],
  };
}

