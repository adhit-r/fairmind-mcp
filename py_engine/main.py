#!/usr/bin/env python3
# py_engine/main.py
"""
Main entry point for FairMind MCP Python engine.
Routes requests to appropriate tool handlers via the registry pattern.
"""
import sys
import json
from pydantic import ValidationError, TypeAdapter
from models import RequestUnion
from core.codec import ToonCodec
from tools.registry import dispatch_tool


def process_request(request_data: dict) -> dict:
    """
    Process a single request: validate, route, and return response.
    
    Args:
        request_data: Raw request dictionary from JSON/TOON
        
    Returns:
        Response dictionary
    """
    try:
        # Validate request using Pydantic adapter
        # This automatically selects the correct model based on 'command' discriminator
        adapter = TypeAdapter(RequestUnion)
        req = adapter.validate_python(request_data)
        
        # Dispatch to appropriate tool handler
        return dispatch_tool(req)
        
    except ValidationError as e:
        return {'error': f'Validation Error: {e}'}
    except Exception as e:
        return {'error': str(e)}


def main():
    """
    Main event loop: read from stdin, process requests, write to stdout.
    """
    codec = ToonCodec()
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            # Try JSON first (from TypeScript), fallback to TOON
            try:
                request_data = json.loads(line)
            except json.JSONDecodeError:
                # Fallback to TOON decode
                request_data = codec.decode(line)
            
            response = process_request(request_data)
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {'error': f'Protocol Error: {str(e)}'}
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    main()
