from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Dict, Any

class BaseRequest(BaseModel):
    command: str

class EvaluateBiasRequest(BaseRequest):
    command: Literal['evaluate_bias']
    content: str
    protected_attribute: Optional[str] = None
    protected_attributes: Optional[List[str]] = None
    task_type: Literal['generative', 'classification']
    content_type: Literal['text', 'code'] = 'text'

class GenerateCounterfactualsRequest(BaseRequest):
    command: Literal['generate_counterfactuals']
    content: str
    sensitive_group: str

class CompareCodeBiasRequest(BaseRequest):
    command: Literal['compare_code_bias']
    code_a: str
    code_b: str
    persona_a: str = "Persona A"
    persona_b: str = "Persona B"
    language_a: Optional[str] = None
    language_b: Optional[str] = None

class EvaluateModelOutputsRequest(BaseRequest):
    command: Literal['evaluate_model_outputs']
    outputs: List[str]
    protected_attributes: List[str]
    task_type: Literal['generative', 'classification']
    content_type: Literal['text', 'code'] = 'text'
    aggregation: Literal['summary', 'detailed'] = 'summary'

class EvaluatePromptSuiteRequest(BaseRequest):
    command: Literal['evaluate_prompt_suite']
    prompts: List[str]
    model_outputs: List[str]
    protected_attributes: List[str]
    suite_name: str = 'default_suite'
    task_type: Literal['generative', 'classification'] = 'generative'
    content_type: Literal['text', 'code'] = 'text'
    previous_results: Optional[Dict[str, Any]] = None

class EvaluateModelResponseRequest(BaseRequest):
    command: Literal['evaluate_model_response']
    prompt: str
    response: str
    protected_attributes: List[str]
    task_type: Literal['generative', 'classification'] = 'generative'
    content_type: Literal['text', 'code'] = 'text'

class EvaluateBiasAdvancedRequest(BaseRequest):
    command: Literal['evaluate_bias_advanced']
    content: str
    protected_attributes: List[str]
    task_type: Literal['generative', 'classification'] = 'generative'
    use_metricframe: bool = True
    use_aif360: bool = False
    metric_names: Optional[List[str]] = None
    content_type: Literal['text', 'code'] = 'text'

class AnalyzeRepositoryBiasRequest(BaseRequest):
    command: Literal['analyze_repository_bias']
    repository_path: str
    protected_attributes: List[str]
    max_commits: int = 0
    min_commits_per_author: int = 5
    file_extensions: List[str] = []
    exclude_paths: List[str] = []

RequestUnion = Union[
    EvaluateBiasRequest,
    GenerateCounterfactualsRequest,
    CompareCodeBiasRequest,
    EvaluateModelOutputsRequest,
    EvaluatePromptSuiteRequest,
    EvaluateModelResponseRequest,
    EvaluateBiasAdvancedRequest,
    AnalyzeRepositoryBiasRequest
]


