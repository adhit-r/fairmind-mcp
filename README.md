# FairMind MCP

FairMind MCP is a Model Context Protocol server that enables AI agents to mathematically verify and self-correct bias in real-time using Green AI principles.

## Features

- **Token-Optimized**: Uses TOON (Token-Oriented Object Notation) format for efficient LLM context usage
- **High-Performance Inference**: Supports LiteRT for fast on-device inference, with robust fallback to heuristic-based counterfactual generation if models are unavailable
- **Industry-Standard Metrics**: Wraps Fairlearn and AIF360 for rigorous fairness auditing. Clearly distinguishes between:
    - **Statistical Audits**: Rigorous analysis of classification datasets with ground truth
    - **Heuristic Proxies**: Estimated bias metrics for generative content where ground truth is simulated via keyword patterns
- **True Code Analysis**: Detects bias in source code using AST parsing (via `esprima` for JS/TS and `ast` for Python). Detects structural bias, control flow divergence, and variable naming issues with high precision
- **Configurable Detection**: Load custom stereotypes and patterns via `bias_config.json` or environment variables
- **LLM Testing Tools**: Systematic bias testing for custom LLMs and fine-tuned models - batch evaluation, prompt suite testing, and real-time monitoring
- **Agent-Native**: Built for the Model Context Protocol, works with Claude Desktop, Cline, and Cursor

## Architecture

The system follows a Broker Pattern:

- **MCP Server (TypeScript/Bun)**: Handles MCP protocol communication and manages the Python kernel with auto-restart, timeout protection, and automatic warm-up to eliminate first-request penalty
- **Python Analysis Kernel**: Runs fairness auditing using Fairlearn/AIF360 and LiteRT-powered inference
- **TOON Codec**: Optimized serialization format for token-optimized communication, with enhanced support for large payloads and nested structures

## Installation

### Prerequisites

- Bun (latest)
- Python 3.11+ (managed via `uv`)
- `uv` package manager

### Setup

```bash
# Install Bun dependencies
bun install

# Setup Python environment
cd py_engine
uv sync
```

## Configuration

You can customize the bias detection patterns (stereotypes, roles, occupations) by editing `py_engine/bias_config.json`.

To use a custom configuration file without modifying the source, set the `FAIRMIND_BIAS_CONFIG` environment variable:

```bash
export FAIRMIND_BIAS_CONFIG=/path/to/your/custom_bias_config.json
```

## Usage

Start the MCP server:

```bash
bun run src/index.ts
```

The server communicates via stdio and exposes seven tools:

1. **evaluate_bias**: Evaluates text, code, or data for bias against protected attributes
   - Use `content_type="text"` for natural language content
   - Use `content_type="code"` for source code analysis (comments, variable names, algorithmic bias, inclusive terminology)
   - Supports single or multiple attributes (via `protected_attributes` array)

2. **evaluate_bias_advanced**: Advanced evaluation with full Fairlearn MetricFrame and AIF360 support
   - For generative text, this uses Heuristic Proxies to estimate metrics like "Demographic Parity" based on text patterns
   - For classification datasets, it provides rigorous statistical analysis

3. **compare_code_bias**: Compares two code snippets generated for different personas to detect structural bias
   - Uses differential AST analysis to find complexity disparities
   - Alerts if one persona receives significantly more complex code (>1.5x ratio)
   - Detects control flow divergence (extra validation steps)

4. **generate_counterfactuals**: Generates alternative text suggestions to reduce bias
   - Uses LiteRT models when available, falls back to heuristics

5. **evaluate_model_outputs**: Batch evaluation tool for testing multiple LLM/fine-tuned model outputs with aggregated reporting
   - Designed for pre-deployment comprehensive testing
   - Returns overall pass rates, failure patterns, and per-attribute metrics

6. **evaluate_prompt_suite**: Systematic prompt suite testing with tracking over time
   - Ideal for fine-tuning validation and continuous monitoring
   - Compares results across training epochs or model versions

7. **evaluate_model_response**: Real-time single output testing for quick bias checks during inference

## Development

### Project Structure

```
fairmind-mcp/
├── src/
│   ├── index.ts          # MCP Server entry point
│   ├── python_bridge.ts  # Robust Python process manager
│   └── types.ts          # TypeScript type definitions
├── py_engine/
│   ├── main.py           # Python entry point with Pydantic validation
│   ├── models.py         # Pydantic data models
│   ├── core/             # Shared utilities
│   │   ├── auditor.py
│   │   ├── code_auditor.py
│   │   ├── ast_analyzer.py
│   │   └── ...
│   └── tools/            # Tool handlers
│       ├── registry.py
│       └── ...
└── website/
    └── website.html      # Landing page
```

## Documentation

- [Quick Start Guide](./docs/QUICKSTART.md)
- [Testing Guide](./docs/HOW_TO_TEST.md)
- [Bias Parameters Reference](./docs/BIAS_PARAMETERS.md) - All detected patterns and metrics
- [Code Bias Detection](./docs/CODE_BIAS_DETECTION.md) - For code generation tools like Cursor
- [LLM Testing Guide](./docs/LLM_TESTING_GUIDE.md) - Test custom LLMs and fine-tuned models for bias
- [Enhanced Metrics Guide](./docs/ENHANCED_METRICS.md) - Full Fairlearn MetricFrame, AIF360, multi-attribute detection
- [Differential Analysis](./docs/DIFFERENTIAL_ANALYSIS.md) - Compare code for different personas
- [Claude Desktop Setup](./docs/CLAUDE_DESKTOP_SETUP.md) - Start here for integration
- [Cursor Setup](./docs/CURSOR_SETUP.md) - Setup for code generation
- [Integration Examples](./docs/INTEGRATION_EXAMPLES.md) - Real-world use cases
- [Next Steps Roadmap](./docs/NEXT_STEPS.md) - Development roadmap

## Quick Setup

### Option 1: Web UI

```bash
bun run ui
```

Then open http://localhost:3000 in your browser to test tools interactively.

### Option 2: Claude Desktop

```bash
./scripts/setup-claude-desktop.sh
```

### Option 3: Cursor

```bash
./scripts/setup-cursor.sh
```

### Manual Setup

See setup guides in `docs/`:
- [Claude Desktop Setup](./docs/CLAUDE_DESKTOP_SETUP.md)
- [Cursor Setup](./docs/CURSOR_SETUP.md)
- [Testing Guide](./docs/HOW_TO_TEST.md)

## License

MIT
