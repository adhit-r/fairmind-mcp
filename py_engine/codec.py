
# py_engine/codec.py
import re
from typing import Any, List, Dict, Union

class ToonCodec:
    """
    A basic implementation of TOON (Token-Oriented Object Notation) for Python.
    Supports encoding simple list of objects and decoding them.
    """
    
    @staticmethod
    def encode(data: Any) -> str:
        """
        Encodes a dictionary or list of dictionaries into TOON format.
        Handles both flat objects and arrays of objects.
        """
        if isinstance(data, dict):
            lines = []
            # Check if this is a flat object (like a request) or has arrays
            has_arrays = any(isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) for v in data.values())
            
            if has_arrays:
                # Array-of-objects pattern: key[count]{cols}: values
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        columns = list(value[0].keys())
                        header = f"{key}[{len(value)}]{{{','.join(columns)}}}:"
                        lines.append(header)
                        for item in value:
                            row = []
                            for col in columns:
                                val = item.get(col, "")
                                str_val = str(val).replace(",", " ").replace("\n", " ") 
                                row.append(str_val)
                            lines.append(f"  {','.join(row)}")
                    elif isinstance(value, list) and len(value) > 0:
                        # Simple list of strings/numbers
                        header = f"{key}[{len(value)}]:"
                        lines.append(header)
                        for item in value:
                            lines.append(f"  {item}")
                    else:
                        # Simple key-value
                        lines.append(f"{key}: {value}")
            else:
                # Flat object - encode as key:value pairs
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        # Nested structure - convert to JSON string for now
                        import json
                        lines.append(f"{key}: {json.dumps(value)}")
                    else:
                        lines.append(f"{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            # List of items
            lines = [f"items[{len(data)}]:"]
            for item in data:
                if isinstance(item, dict):
                    # Convert dict to key:value format
                    item_str = ", ".join(f"{k}:{v}" for k, v in item.items())
                    lines.append(f"  {item_str}")
                else:
                    lines.append(f"  {item}")
            return "\n".join(lines)
        return str(data)

    @staticmethod
    def decode(text: str) -> Dict[str, Any]:
        """
        Decodes a TOON string back into a dictionary.
        Handles both flat objects and arrays of objects.
        """
        result = {}
        lines = text.strip().split('\n')
        current_key = None
        current_cols = []
        current_list = []
        
        # Regex for header: key[count]{col1,col2}: or key[count]:
        header_pattern = re.compile(r'(\w+)\[(\d+)\](?:\{([^}]+)\})?:')
        simple_pattern = re.compile(r'^(\w+):\s*(.+)$')
        
        for line in lines:
            line = line.rstrip()
            if not line: continue
            
            # Check for array header
            match = header_pattern.match(line)
            if match:
                # Save previous if any
                if current_key:
                    result[current_key] = current_list
                
                current_key = match.group(1)
                count = int(match.group(2))
                cols_str = match.group(3)
                
                if cols_str:
                    # Array of objects
                    current_cols = [c.strip() for c in cols_str.split(',')]
                    current_list = []
                else:
                    # Simple array
                    current_cols = []
                    current_list = []
            elif line.startswith('  ') and current_key:
                # Data row
                if current_cols:
                    # Object row
                    values = [v.strip() for v in line.strip().split(',')]
                    obj = {}
                    for i, col in enumerate(current_cols):
                        if i < len(values):
                            val = values[i]
                            # Try to infer type
                            if val.isdigit():
                                val = int(val)
                            elif val.replace('.', '', 1).replace('-', '', 1).isdigit():
                                try:
                                    val = float(val)
                                except ValueError:
                                    pass
                            elif val.lower() in ('true', 'false'):
                                val = val.lower() == 'true'
                            obj[col] = val
                    current_list.append(obj)
                else:
                    # Simple value
                    val = line.strip()
                    # Try to infer type
                    if val.isdigit():
                        val = int(val)
                    elif val.replace('.', '', 1).replace('-', '', 1).isdigit():
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    current_list.append(val)
            else:
                # Simple Key: Value
                simple_match = simple_pattern.match(line)
                if simple_match:
                    k = simple_match.group(1).strip()
                    v = simple_match.group(2).strip()
                    # Try JSON parsing for complex values
                    if v.startswith('{') or v.startswith('['):
                        try:
                            import json
                            v = json.loads(v)
                        except:
                            pass
                    # Try type inference
                    elif v.isdigit():
                        v = int(v)
                    elif v.replace('.', '', 1).replace('-', '', 1).isdigit():
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                    elif v.lower() in ('true', 'false'):
                        v = v.lower() == 'true'
                    result[k] = v
        
        if current_key:
             result[current_key] = current_list
             
        return result

# Example usage/Test
if __name__ == "__main__":
    data = {
        "audit": [
            {"metric": "DPD", "value": 0.02, "status": "PASS"},
            {"metric": "DI", "value": 0.85, "status": "PASS"}
        ]
    }
    encoded = ToonCodec.encode(data)
    print("Encoded:")
    print(encoded)
    decoded = ToonCodec.decode(encoded)
    print("\nDecoded:")
    print(decoded)

