#!/usr/bin/env python3
# py_engine/main.py
import sys
import json
from codec import ToonCodec
from auditor import evaluate_bias_audit
from inference import generate_counterfactuals_nlp

def main():
    codec = ToonCodec()
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            # Try JSON first (from TypeScript), fallback to TOON
            try:
                import json
                request = json.loads(line)
            except json.JSONDecodeError:
                # Fallback to TOON decode
                request = codec.decode(line)
            
            command = request.get('command', '')
            
            if command == 'evaluate_bias':
                content = request.get('content', '')
                protected_attribute = request.get('protected_attribute', '')
                task_type = request.get('task_type', 'generative')
                
                result = evaluate_bias_audit(content, protected_attribute, task_type)
                
                # Encode response as JSON for now (more reliable)
                # TOON encoding can be added later for final agent responses
                import json
                response = {'result': result}
                print(json.dumps(response), flush=True)
                
            elif command == 'generate_counterfactuals':
                content = request.get('content', '')
                sensitive_group = request.get('sensitive_group', '')
                
                result = generate_counterfactuals_nlp(content, sensitive_group)
                
                # Encode response as JSON for now
                import json
                response = {'counterfactuals': result}
                print(json.dumps(response), flush=True)
                
            else:
                error_response = {'error': f'Unknown command: {command}'}
                print(codec.encode(error_response), flush=True)
                
        except Exception as e:
            error_response = {'error': str(e)}
            print(codec.encode(error_response), flush=True)

if __name__ == '__main__':
    main()
