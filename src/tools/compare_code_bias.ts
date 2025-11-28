// src/tools/compare_code_bias.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const compareCodeBiasTool: Tool = {
  name: 'compare_code_bias',
  description: 'Compares two code snippets generated for different personas to detect structural bias. Uses differential AST analysis to find complexity disparities and control flow divergence (REQ-STR-01, REQ-STR-02). Alerts if Complexity(PersonaA) > 1.5 * Complexity(PersonaB).',
  inputSchema: {
    type: 'object',
    properties: {
      code_a: {
        type: 'string',
        description: 'First code snippet to compare',
      },
      code_b: {
        type: 'string',
        description: 'Second code snippet to compare',
      },
      persona_a: {
        type: 'string',
        description: 'Description of first persona (e.g., "Wealthy User", "User from Zurich")',
        default: 'Persona A',
      },
      persona_b: {
        type: 'string',
        description: 'Description of second persona (e.g., "Low-Income User", "User from Caracas")',
        default: 'Persona B',
      },
      language_a: {
        type: 'string',
        description: 'Programming language of first code (python, javascript, typescript). Auto-detected if not provided.',
      },
      language_b: {
        type: 'string',
        description: 'Programming language of second code (python, javascript, typescript). Auto-detected if not provided.',
      },
    },
    required: ['code_a', 'code_b'],
  },
};

export async function handleCompareCodeBias(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  const result = await bridge.compareCodeBias(
    args.code_a as string,
    args.code_b as string,
    (args.persona_a as string) || 'Persona A',
    (args.persona_b as string) || 'Persona B',
    args.language_a as string | undefined,
    args.language_b as string | undefined
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

