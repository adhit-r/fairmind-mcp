// src/tools/analyze_repository_bias.ts
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { PythonBridge } from '../python_bridge.js';

export const analyzeRepositoryBiasTool: Tool = {
  name: 'analyze_repository_bias',
  description: 'Analyzes a git repository to detect bias patterns across all commits and authors. Maps how each code author is biased, explains why, and provides scorecards. Handles repositories with 1000s of commits and 100s of users.',
  inputSchema: {
    type: 'object',
    properties: {
      repository_path: {
        type: 'string',
        description: 'Path to the git repository to analyze. Can be absolute or relative.',
      },
      protected_attributes: {
        type: 'array',
        items: { type: 'string', enum: ['gender', 'race', 'age', 'disability'] },
        description: 'Array of protected attributes to analyze (e.g., ["gender", "race"])',
        default: ['gender', 'race', 'age', 'disability'],
      },
      max_commits: {
        type: 'number',
        description: 'Maximum number of commits to analyze (for performance). 0 means analyze all commits.',
        default: 0,
      },
      min_commits_per_author: {
        type: 'number',
        description: 'Minimum number of commits required for an author to be included in the scorecard',
        default: 5,
      },
      file_extensions: {
        type: 'array',
        items: { type: 'string' },
        description: 'File extensions to analyze (e.g., [".js", ".py", ".ts"]). Empty array means analyze all files.',
        default: [],
      },
      exclude_paths: {
        type: 'array',
        items: { type: 'string' },
        description: 'Paths to exclude from analysis (e.g., ["node_modules/", "vendor/", ".git/"])',
        default: ['node_modules/', 'vendor/', '.git/', 'dist/', 'build/'],
      },
      anonymize_authors: {
        type: 'boolean',
        description: 'If true, replace author emails with hashed IDs and use generic names (e.g., "Author-abc123"). Protects privacy while maintaining analysis capability.',
        default: false,
      },
      exclude_author_names: {
        type: 'boolean',
        description: 'If true, replace all author names with "Anonymous". Use with anonymize_authors for maximum privacy.',
        default: false,
      },
      pattern_only_mode: {
        type: 'boolean',
        description: 'If true, focus analysis on bias patterns only, minimizing author-specific information. Useful for team-wide analysis without individual attribution.',
        default: false,
      },
    },
    required: ['repository_path', 'protected_attributes'],
  },
};

export async function handleAnalyzeRepositoryBias(
  bridge: PythonBridge,
  args: any
): Promise<any> {
  return bridge.analyzeRepositoryBias(
    args.repository_path,
    args.protected_attributes || ['gender', 'race', 'age', 'disability'],
    args.max_commits || 0,
    args.min_commits_per_author || 5,
    args.file_extensions || [],
    args.exclude_paths || ['node_modules/', 'vendor/', '.git/', 'dist/', 'build/'],
    args.anonymize_authors || false,
    args.exclude_author_names || false,
    args.pattern_only_mode || false
  );
}

