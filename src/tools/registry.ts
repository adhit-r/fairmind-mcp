// src/tools/registry.ts
/**
 * Tool registry for MCP server.
 * Centralizes tool definitions and handlers for maintainability.
 */
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

// Import all tool definitions
import { evaluateBiasTool, handleEvaluateBias } from './evaluate_bias.js';
import { evaluateBiasAdvancedTool, handleEvaluateBiasAdvanced } from './evaluate_bias_advanced.js';
import { generateCounterfactualsTool, handleGenerateCounterfactuals } from './generate_counterfactuals.js';
import { compareCodeBiasTool, handleCompareCodeBias } from './compare_code_bias.js';
import { evaluateModelOutputsTool, handleEvaluateModelOutputs } from './evaluate_model_outputs.js';
import { evaluatePromptSuiteTool, handleEvaluatePromptSuite } from './evaluate_prompt_suite.js';
import { evaluateModelResponseTool, handleEvaluateModelResponse } from './evaluate_model_response.js';

export interface ToolHandler {
  tool: Tool;
  handler: (bridge: PythonBridge, args: any) => Promise<any>;
}

export const TOOLS: ToolHandler[] = [
  { tool: evaluateBiasTool, handler: handleEvaluateBias },
  { tool: evaluateBiasAdvancedTool, handler: handleEvaluateBiasAdvanced },
  { tool: generateCounterfactualsTool, handler: handleGenerateCounterfactuals },
  { tool: compareCodeBiasTool, handler: handleCompareCodeBias },
  { tool: evaluateModelOutputsTool, handler: handleEvaluateModelOutputs },
  { tool: evaluatePromptSuiteTool, handler: handleEvaluatePromptSuite },
  { tool: evaluateModelResponseTool, handler: handleEvaluateModelResponse },
];

export function getAllTools(): Tool[] {
  return TOOLS.map(t => t.tool);
}

export async function handleTool(
  name: string,
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const toolHandler = TOOLS.find(t => t.tool.name === name);
  
  if (!toolHandler) {
    throw new Error(`Unknown tool: ${name}`);
  }
  
  return toolHandler.handler(bridge, args);
}

