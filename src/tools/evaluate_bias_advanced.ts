// src/tools/evaluate_bias_advanced.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const evaluateBiasAdvancedTool: Tool = {
  name: 'evaluate_bias_advanced',
  description: 'Advanced bias evaluation with full Fairlearn MetricFrame and AIF360 support. Provides statistical rigor beyond heuristic-based detection. Supports multi-attribute detection and intersectional bias analysis.',
  inputSchema: {
    type: 'object',
    properties: {
      content: {
        type: 'string',
        description: 'The text or code to evaluate for bias',
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Array of protected attributes to check simultaneously',
      },
      task_type: {
        type: 'string',
        enum: ['generative', 'classification'],
        default: 'generative',
        description: 'The type of task being evaluated',
      },
      use_metricframe: {
        type: 'boolean',
        default: true,
        description: 'Use Fairlearn MetricFrame for statistical metrics (default: true)',
      },
      use_aif360: {
        type: 'boolean',
        default: false,
        description: 'Use AIF360 ClassificationMetric for additional fairness metrics (requires classification data)',
      },
      metric_names: {
        type: 'array',
        items: { type: 'string' },
        description: 'Custom metrics to compute (e.g., ["selection_rate", "true_positive_rate"])',
      },
      content_type: {
        type: 'string',
        enum: ['text', 'code'],
        default: 'text',
        description: 'Type of content: "text" for natural language, "code" for source code',
      },
    },
    required: ['content', 'protected_attributes', 'task_type'],
  },
};

export async function handleEvaluateBiasAdvanced(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const result = await bridge.evaluateBiasAdvanced(
    args.content as string,
    args.protected_attributes as string[],
    args.task_type as 'generative' | 'classification',
    args.use_metricframe as boolean ?? true,
    args.use_aif360 as boolean ?? false,
    args.metric_names as string[] | undefined,
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

