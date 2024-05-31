import json
import os
from collections import defaultdict
from deepdiff import DeepDiff

def load_json_files(directory):
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                try:
                    json_files.append(json.load(f))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {filename}: {e}")
    return json_files

def merge_json_data(json_files):
    merged_data = defaultdict(list)
    
    for data in json_files:
        for key, value in data.items():
            if isinstance(value, list):
                merged_data[key].extend(value)
            else:
                merged_data[key].append(value)
                
    complete_json = {}
    for key, value in merged_data.items():
        complete_json[key] = value[:3]  # Limiting to 3 items for each list
    
    return complete_json

def compare_json_structures(json_files):
    base_structure = None
    differences = []
    
    for i, data in enumerate(json_files):
        if base_structure is None:
            base_structure = data
        else:
            diff = DeepDiff(base_structure, data, ignore_order=True)
            if diff:
                differences.append((i, diff))
                
    return differences

def make_serializable(obj):
    if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    return str(obj)

def recursive_make_serializable(data):
    if isinstance(data, dict):
        return {key: recursive_make_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [recursive_make_serializable(element) for element in data]
    else:
        return make_serializable(data)

def main():
    persona_dir = "persona"
    empresa_dir = "empresa"
    
    persona_json_files = load_json_files(persona_dir)
    empresa_json_files = load_json_files(empresa_dir)
    
    complete_persona_json = merge_json_data(persona_json_files)
    complete_empresa_json = merge_json_data(empresa_json_files)
    
    with open('complete_persona.json', 'w') as f:
        json.dump(recursive_make_serializable(complete_persona_json), f, indent=4)
        
    with open('complete_empresa.json', 'w') as f:
        json.dump(recursive_make_serializable(complete_empresa_json), f, indent=4)
    
    persona_differences = compare_json_structures(persona_json_files)
    empresa_differences = compare_json_structures(empresa_json_files)
    
    persona_differences_serializable = [(i, recursive_make_serializable(diff)) for i, diff in persona_differences]
    empresa_differences_serializable = [(i, recursive_make_serializable(diff)) for i, diff in empresa_differences]
    
    with open('persona_structure_differences.json', 'w') as f:
        json.dump(persona_differences_serializable, f, indent=4)
        
    with open('empresa_structure_differences.json', 'w') as f:
        json.dump(empresa_differences_serializable, f, indent=4)
    
    print("JSON completos y reportes de diferencias de estructura generados exitosamente.")

if __name__ == "__main__":
    main()
