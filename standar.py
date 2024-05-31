import json
import os
from collections import defaultdict
from deepdiff import DeepDiff

def load_json_files(directory):
    json_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                json_files.append(json.load(f))
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
        complete_json[key] = value[:3]
    
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

def main():
    persona_dir = "persona"
    empresa_dir = "empresa"
    
    persona_json_files = load_json_files(persona_dir)
    empresa_json_files = load_json_files(empresa_dir)
    
    complete_persona_json = merge_json_data(persona_json_files)
    complete_empresa_json = merge_json_data(empresa_json_files)
    
    with open('complete_persona.json', 'w') as f:
        json.dump(complete_persona_json, f, indent=4)
        
    with open('complete_empresa.json', 'w') as f:
        json.dump(complete_empresa_json, f, indent=4)
    
    persona_differences = compare_json_structures(persona_json_files)
    empresa_differences = compare_json_structures(empresa_json_files)
    
    with open('persona_structure_differences.json', 'w') as f:
        json.dump(persona_differences, f, indent=4)
        
    with open('empresa_structure_differences.json', 'w') as f:
        json.dump(empresa_differences, f, indent=4)
    
    print("JSON completos y reportes de diferencias de estructura generados exitosamente.")

if __name__ == "__main__":
    main()
