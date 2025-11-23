# FairMind MCP - Quick Start Guide

## Prerequisites

- **Bun**: Latest version ([install](https://bun.sh))
- **Python 3.11+**: Managed via `uv`
- **uv**: Python package manager ([install](https://github.com/astral-sh/uv))

## Installation

```bash
# Install Bun dependencies
bun install

# Setup Python environment
cd py_engine
uv sync
cd ..
```

## Running the Server

```bash
# Start the MCP server (communicates via stdio)
bun run start
```

## Testing Components

```bash
# Test TOON codec
bun run test:codec

# Test bias auditor
bun run test:auditor

# Test counterfactual generation
bun run test:inference
```

## MCP Integration

The server exposes two tools via the Model Context Protocol:

### 1. `evaluate_bias`

Evaluates text for bias against protected attributes.

**Input:**
```json
{
  "content": "Nurses are gentle women who care for patients",
  "protected_attribute": "gender",
  "task_type": "generative"
}
```

**Output:** TOON-formatted fairness report with metrics and status.

### 2. `generate_counterfactuals`

Generates alternative text suggestions to reduce bias.

**Input:**
```json
{
  "content": "The nurse was gentle",
  "sensitive_group": "gender"
}
```

**Output:** List of counterfactual alternatives.

## Architecture

- **MCP Server** (`src/index.ts`): TypeScript/Bun server handling MCP protocol
- **Python Bridge** (`src/python_bridge.ts`): Manages Python subprocess and TOON communication
- **Analysis Kernel** (`py_engine/`): Python modules for fairness auditing
  - `auditor.py`: Fairlearn-based statistical metrics
  - `inference.py`: LiteRT-powered counterfactual generation
  - `codec.py`: TOON encoder/decoder

## Development

The project uses:
- **Bun** for TypeScript runtime
- **uv** for Python dependency management
- **TOON** format for token-efficient data exchange
- **LiteRT** for high-performance on-device inference

## Notes

- LiteRT models are optional - the system falls back to heuristic-based counterfactuals if models aren't available
- The TOON codec is a custom implementation optimized for this use case
- All communication between TS and Python uses TOON format over stdio

