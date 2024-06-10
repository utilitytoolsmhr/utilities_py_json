import os
import json
from collections import defaultdict

def load_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    data_list = []
    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_list.append(data)
    return data_list

def merge_dicts(dict_list):
    merged_dict = defaultdict(lambda: defaultdict(list))
    for d in dict_list:
        for key, value in d.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list):
                        merged_dict[key][sub_key].extend(sub_value)
                    else:
                        merged_dict[key][sub_key] = sub_value
            else:
                merged_dict[key] = value
    return dict(merged_dict)

def compare_and_merge(json_data_list):
    final_data = {}
    for data in json_data_list:
        for key, value in data.items():
            if key not in final_data:
                final_data[key] = value
            elif final_data[key] != value:
                print(f"Difference found in key '{key}':")
                print(f"Value in final_data: {final_data[key]}")
                print(f"Value in current data: {value}")
                final_data[key] = value
    return final_data

def main():
    persona_dir = 'Persona'
    empresa_dir = 'Empresa'
    
    persona_data_list = load_json_files(persona_dir)
    empresa_data_list = load_json_files(empresa_dir)

    merged_persona = merge_dicts(persona_data_list)
    merged_empresa = merge_dicts(empresa_data_list)

    combined_structure = compare_and_merge([merged_persona, merged_empresa])

    with open('Persona_completo.json', 'w', encoding='utf-8') as f:
        json.dump(merged_persona, f, ensure_ascii=False, indent=4)

    with open('Empresa_completo.json', 'w', encoding='utf-8') as f:
        json.dump(merged_empresa, f, ensure_ascii=False, indent=4)

    with open('Estructura_completa.json', 'w', encoding='utf-8') as f:
        json.dump(combined_structure, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
