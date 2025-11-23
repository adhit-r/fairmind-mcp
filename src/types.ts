
// src/types.ts
export interface EvaluationRequest {
  content: string;
  protected_attribute: string;
  task_type: 'generative' | 'classification';
}

export interface CounterfactualRequest {
  content: string;
  sensitive_group: string;
}

export interface FairnessReport {
  status: 'PASS' | 'FAIL';
  metrics: {
    name: string;
    value: number;
    threshold: number;
    result: 'PASS' | 'FAIL';
  }[];
  details?: string;
  counterfactuals?: string[];
}

