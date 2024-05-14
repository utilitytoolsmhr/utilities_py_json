import json
import os
import openpyxl
from openpyxl.utils import get_column_letter

def get_json_files(directory):
    """Obtiene todos los archivos JSON en el directorio especificado."""
    return [f for f in os.listdir(directory) if f.endswith('.json')]

def get_defaults_structure(json_data):
    """Genera la estructura de valores por defecto según el tipo de dato."""
    def process_dict(data):
        if isinstance(data, dict):
            return {k: process_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [process_dict(data[0])] if data else []
        elif isinstance(data, str):
            return ""
        elif isinstance(data, int):
            return 0
        elif isinstance(data, float):
            return 0.0
        else:
            return None
    return process_dict(json_data)

def write_to_excel(headers, sheet):
    """Escribe las cabeceras en una hoja de Excel."""
    sheet["A1"] = "Campo"
    col = 1
    for header in headers:
        sheet[f"{get_column_letter(col)}2"] = header
        col += 1

def write_defaults_to_json(defaults, output_path):
    """Escribe los valores por defecto en un archivo JSON."""
    with open(output_path, 'w') as f:
        json.dump(defaults, f, indent=4)

def format_value(value):
    """Devuelve el valor predeterminado según el tipo de dato."""
    if isinstance(value, str):
        return '""'
    elif isinstance(value, int):
        return '0'
    elif isinstance(value, float):
        return '0.0'
    return 'None'

def format_json(json_obj, path='', lines=None):
    """Transforma recursivamente el JSON y acumula las líneas de código en 'lines'."""
    if lines is None:
        lines = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            new_path = f"{path}['{k}']" if path else f"['{k}']"
            format_json(v, new_path, lines)
    elif isinstance(json_obj, list):
        if len(json_obj) > 0:
            new_path = f"{path}[0]"
            format_json(json_obj[0], new_path, lines)
    else:
        lines.append(f"    json_return{path} = None")
    return lines

def process_json_file(json_path):
    """Procesa un archivo JSON y genera un archivo Python con las cabeceras formateadas."""
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Nombre base del archivo sin extensión
    base_name = 'json_return_' + os.path.splitext(os.path.basename(json_path))[0]

    # Lista para acumular el contenido del archivo Python
    lines = []
    formatted_json = json.dumps(data)
    lines.append(f"{base_name} = {formatted_json}")
    lines.append(f"json_return = json.loads({base_name})")
    lines.append("")
    lines.append("def tfn(fna, fti):")
    lines.append("    pass  # Aquí va la lógica de transformación")
    lines.append("")
    lines.append("def main(p):")
    lines.append("    # Aquí va la lógica principal")
    lines.append("")

    # Aplicar la formateación inicial al JSON entero
    replacement_lines = format_json(data)
    lines.extend(replacement_lines)

    lines.append("    return json_return")
    lines.append("")

    # Guardar el nuevo archivo Python
    new_file_path = f"{os.path.splitext(os.path.basename(json_path))[0]}.py"
    with open(new_file_path, 'w') as new_file:
        new_file.write('\n'.join(lines))

    # Generar el archivo JSON con valores por defecto
    defaults = get_defaults_structure(data)
    write_defaults_to_json(defaults, os.path.join(os.path.dirname(json_path), f"cr_{os.path.basename(json_path)}"))

def write_data_to_excel(json_data, sheet):
    """Escribe datos JSON en una hoja de Excel."""
    current_row = 2
    sheet["A1"] = "Campo"
    sheet["B1"] = "Tipo de Dato"
    sheet["C1"] = "Ejemplo Valor"
    
    def process_dict(data, col, row):
        for key, value in data.items():
            sheet[f"{get_column_letter(col)}{row}"] = key
            if isinstance(value, dict):
                row = process_dict(value, col + 1, row + 1)
            else:
                if isinstance(value, int):
                    data_type = "Integer"
                elif isinstance(value, float):
                    data_type = "Float"
                elif isinstance(value, str):
                    data_type = "String"
                elif isinstance(value, list):
                    data_type = "List"
                    value = ', '.join(map(str, value))
                else:
                    data_type = "Unknown"
                    value = str(value)
                sheet[f"{get_column_letter(col + 1)}{row}"] = value
                sheet[f"{get_column_letter(col + 2)}{row}"] = data_type
                row += 1
        return row
    
    process_dict(json_data, 1, current_row)

def main(P):
    """Función principal que procesa todos los archivos JSON en el directorio actual."""
    headers = set()
    workbook = openpyxl.Workbook()
    
    for filename in os.listdir(P):
        if filename.endswith('.json'):
            json_path = os.path.join(P, filename)
            with open(json_path, 'r') as f:
                json_data = json.load(f)
                sheet = workbook.create_sheet(title=os.path.splitext(filename)[0])
                headers.update(json_data.keys())
                write_data_to_excel(json_data, sheet)
                process_json_file(json_path)
    
    if 'Sheet' in workbook.sheetnames:
        workbook.remove(workbook['Sheet'])
    
    # Guardar cabeceras en una hoja de Excel
    headers_sheet = workbook.create_sheet(title="Cabeceras")
    write_to_excel(headers, headers_sheet)
    workbook.save(os.path.join(P, "headers.xlsx"))

if __name__ == "__main__":
    main(".")
