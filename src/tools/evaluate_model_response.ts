// src/tools/evaluate_model_response.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const evaluateModelResponseTool: Tool = {
  name: 'evaluate_model_response',
  description: 'Real-time single output testing for LLM responses. Quick bias check during inference/generation. Returns pass/fail status and key issues.',
  inputSchema: {
    type: 'object',
    properties: {
      prompt: {
        type: 'string',
        description: 'The prompt that generated the response',
      },
      response: {
        type: 'string',
        description: 'The model response to evaluate',
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Which protected attributes to check for bias',
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
    },
    required: ['prompt', 'response', 'protected_attributes'],
  },
};

export async function handleEvaluateModelResponse(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const result = await bridge.evaluateModelResponse(
    args.prompt as string,
    args.response as string,
    args.protected_attributes as string[],
    (args.task_type as 'generative' | 'classification') || 'generative',
    (args.content_type as 'text' | 'code') || 'text'
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

