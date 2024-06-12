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

def clean_data(data):
    if isinstance(data, dict):
        clean_dict = {}
        for k, v in data.items():
            if isinstance(v, dict):
                if "xsi:nil" in v and v["xsi:nil"]:
                    clean_dict[k] = "sin data"
                else:
                    clean_dict[k] = clean_data(v)
            else:
                clean_dict[k] = clean_data(v)
        return clean_dict
    elif isinstance(data, list):
        return [clean_data(item) for item in data[:2]]
    else:
        return data

def get_most_complete_module(modules):
    max_keys = 0
    most_complete_module = {}
    for module in modules:
        cleaned_module = clean_data(module)
        num_keys = len(json.dumps(cleaned_module))
        if num_keys > max_keys:
            max_keys = num_keys
            most_complete_module = cleaned_module
    # Limitar a los primeros 2 elementos si es una lista
    for key, value in most_complete_module.items():
        if isinstance(value, list):
            most_complete_module[key] = value[:2]
    return most_complete_module

def process_json_data(data_list):
    report_dict = defaultdict(list)
    for data in data_list:
        if 'dataSourceResponse' in data:
            response = data['dataSourceResponse']
            if 'GetReporteOnlineResponse' in response:
                report = response['GetReporteOnlineResponse']
                if 'ReporteCrediticio' in report:
                    credit_report = report['ReporteCrediticio']
                    if 'Modulos' in credit_report:
                        modules = credit_report['Modulos']
                        for module in modules['Modulo']:
                            report_code = module['Codigo']
                            report_dict[report_code].append(module)
                            print(f"Processed module: {module['Nombre']} with code: {report_code}")

    most_complete_reports = {}
    for report_code, modules in report_dict.items():
        most_complete_module_data = get_most_complete_module([module['Data'] for module in modules])
        for module in modules:
            if module['Data'] == most_complete_module_data:
                most_complete_reports[report_code] = module
                print(f"Selected most complete module for code {report_code}: {module['Nombre']}")
                break
        if report_code not in most_complete_reports:
            # Add the least complete module if none is selected
            least_complete_module_data = clean_data(modules[0]['Data'])
            most_complete_reports[report_code] = modules[0]
            most_complete_reports[report_code]['Data'] = least_complete_module_data
            print(f"Added least complete module for code {report_code}: {modules[0]['Nombre']}")

    return most_complete_reports

def main():
    persona_dir = 'Persona'
    empresa_dir = 'Empresa'
    
    persona_data_list = load_json_files(persona_dir)
    empresa_data_list = load_json_files(empresa_dir)

    persona_reports = process_json_data(persona_data_list)
    empresa_reports = process_json_data(empresa_data_list)

    # Combinar módulos de persona y empresa
    combined_reports = {**persona_reports, **empresa_reports}

    # Guardar cada reporte en un archivo separado
    for report_code, report in combined_reports.items():
        filename = f'Reporte_{report_code}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        print(f'Saved report {report_code} to {filename}')

if __name__ == '__main__':
    main()
