
# py_engine/codec.py
import re
from typing import Any, List, Dict, Union

class ToonCodec:
    """
    Optimized TOON (Token-Oriented Object Notation) encoder for Python.
    Supports encoding nested structures, arrays, and large payloads efficiently.
    """
    
    @staticmethod
    def _escape_value(val: Any) -> str:
        """Escape special characters in values."""
        if val is None:
            return ""
        str_val = str(val)
        # Replace problematic characters
        str_val = str_val.replace(",", " ").replace("\n", " ").replace("\r", " ")
        # Truncate very long values (keep first 200 chars)
        if len(str_val) > 200:
            str_val = str_val[:200] + "..."
        return str_val
    
    @staticmethod
    def _encode_value(value: Any, indent: int = 0) -> List[str]:
        """
        Recursively encode a value (handles nested structures).
        Returns list of lines for the encoded value.
        """
        lines = []
        prefix = "  " * indent
        
        if isinstance(value, dict):
            # Check if this dict contains arrays of objects (most efficient pattern)
            has_object_arrays = any(
                isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict)
                for v in value.values()
            )
            
            if has_object_arrays:
                # Optimize: encode arrays of objects with column headers
                for key, val in value.items():
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                        # Array of objects - use column format
                        columns = list(val[0].keys())
                        header = f"{prefix}{key}[{len(val)}]{{{','.join(columns)}}}:"
                        lines.append(header)
                        for item in val:
                            row = []
                            for col in columns:
                                row.append(ToonCodec._escape_value(item.get(col)))
                            lines.append(f"{prefix}  {','.join(row)}")
                    elif isinstance(val, list) and len(val) > 0:
                        # Simple array
                        header = f"{prefix}{key}[{len(val)}]:"
                        lines.append(header)
                        for item in val:
                            if isinstance(item, dict):
                                # Nested dict in array - encode inline
                                item_lines = ToonCodec._encode_value(item, indent + 1)
                                lines.extend(item_lines)
                            else:
                                lines.append(f"{prefix}  {ToonCodec._escape_value(item)}")
                    elif isinstance(val, dict):
                        # Nested dict - recurse
                        lines.append(f"{prefix}{key}:")
                        nested_lines = ToonCodec._encode_value(val, indent + 1)
                        lines.extend(nested_lines)
                    else:
                        # Simple value
                        if val is not None:
                            lines.append(f"{prefix}{key}: {ToonCodec._escape_value(val)}")
            else:
                # Flat or nested dict without arrays - encode key:value pairs
                for key, val in value.items():
                    if isinstance(val, dict):
                        lines.append(f"{prefix}{key}:")
                        nested_lines = ToonCodec._encode_value(val, indent + 1)
                        lines.extend(nested_lines)
                    elif isinstance(val, list):
                        if len(val) > 0 and isinstance(val[0], dict):
                            # Array of objects
                            columns = list(val[0].keys())
                            header = f"{prefix}{key}[{len(val)}]{{{','.join(columns)}}}:"
                            lines.append(header)
                            for item in val:
                                row = []
                                for col in columns:
                                    row.append(ToonCodec._escape_value(item.get(col)))
                                lines.append(f"{prefix}  {','.join(row)}")
                        else:
                            # Simple array
                            header = f"{prefix}{key}[{len(val)}]:"
                            lines.append(header)
                            for item in val:
                                lines.append(f"{prefix}  {ToonCodec._escape_value(item)}")
                    else:
                        if val is not None:
                            lines.append(f"{prefix}{key}: {ToonCodec._escape_value(val)}")
        elif isinstance(value, list):
            # Top-level list
            lines.append(f"{prefix}items[{len(value)}]:")
            for item in value:
                if isinstance(item, dict):
                    item_lines = ToonCodec._encode_value(item, indent + 1)
                    lines.extend(item_lines)
                else:
                    lines.append(f"{prefix}  {ToonCodec._escape_value(item)}")
        else:
            # Primitive value
            lines.append(f"{prefix}{ToonCodec._escape_value(value)}")
        
        return lines
    
    @staticmethod
    def encode(data: Any) -> str:
        """
        Encodes data into TOON format.
        Optimized for large payloads with nested structures and arrays.
        """
        if data is None:
            return ""
        
        lines = ToonCodec._encode_value(data, indent=0)
        return "\n".join(lines)

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

