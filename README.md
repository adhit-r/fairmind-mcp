# FairMind MCP

FairMind MCP is a Model Context Protocol server that enables AI agents to mathematically verify and self-correct bias in real-time using "Green AI" principles.

## Features

- **Token-Optimized**: Uses TOON (Token-Oriented Object Notation) format for efficient LLM context usage
- **High-Performance**: Leverages LiteRT for fast on-device inference
- **Industry-Standard Metrics**: Wraps Fairlearn and AIF360 for rigorous fairness auditing
- **Agent-Native**: Built for the Model Context Protocol, works with Claude Desktop, Cline, and Cursor

## Architecture

The system follows a Broker Pattern:

- **MCP Server (TypeScript/Bun)**: Handles MCP protocol communication and manages the Python kernel
- **Python Analysis Kernel**: Runs fairness auditing using Fairlearn/AIF360 and LiteRT-powered inference
- **TOON Codec**: Efficient serialization format for token-optimized communication

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

## Usage

Start the MCP server:

```bash
bun run src/index.ts
```

The server communicates via stdio and exposes two tools:

1. **evaluate_bias**: Evaluates text or data for bias against protected attributes
2. **generate_counterfactuals**: Generates alternative text suggestions to reduce bias

## Development

### Project Structure

```
fairmind-mcp/
├── src/
│   ├── index.ts          # MCP Server entry point
│   ├── python_bridge.ts  # Python process manager
│   └── types.ts          # TypeScript type definitions
├── py_engine/
│   ├── main.py           # Python entry point
│   ├── codec.py          # TOON encoder/decoder
│   ├── auditor.py        # Fairlearn wrapper
│   └── inference.py      # LiteRT wrapper
└── website/
    └── website.html      # Landing page
```

## License

MIT
