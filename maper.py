import json
import os

# Ajustamos la función `text_fix` y `traceback` en cada script generado
text_fix = lambda x: x.strip() if isinstance(x, str) else x

def generar_scripts_por_modulo(json_perfecto, tipo):
    modulos = json_perfecto.get('ReporteCrediticio', {}).get('Modulos', {}).get('Modulo', [])
    for modulo in modulos:
        nombre_modulo = modulo['Nombre'].replace(' ', '_').lower()
        codigo_modulo = modulo['Codigo']
        nombre_archivo = f"{tipo}_modulo_{codigo_modulo}_{nombre_modulo}.py"
        
        with open(nombre_archivo, 'w') as f:
            f.write("import os\n")
            f.write("import sys\n")
            f.write("import traceback\n")
            f.write("import json\n")
            f.write("from pe_utils import text_fix\n\n")

            f.write("def main(payload):\n\n")
            f.write("    try:\n")
            f.write(f"        nombre  = '{modulo['Nombre']}'\n")
            f.write(f"        target  = '{nombre_modulo}'\n")
            f.write(f"        codigo  = {codigo_modulo}\n")
            f.write("        modulos = payload.get('dataSourceResponse').get('GetReporteOnlineResponse').get('ReporteCrediticio').get('Modulos').get('Modulo')\n")
            f.write(f"        modulo  = [modulo for modulo in modulos if modulo.get('Data') is not None and nombre in modulo.get('Nombre')]\n\n")
            f.write("        if len(modulo) > 1:\n")
            f.write("            modulo_filtrado = [modulo_filtrado for modulo_filtrado in modulo if modulo_filtrado.get('Data').get(target)]\n")
            f.write("            modulo = modulo_filtrado if len(modulo_filtrado) == 1 else modulo\n\n")
            f.write("        nodo = modulo[0].get('Data').get(target)\n")
            f.write("        data_list = nodo.get('Data') if nodo else None\n")
            f.write("    except:\n")
            f.write("        traceback.print_exc()\n")
            f.write("        data_list = None\n\n")

            f.write("    def process_item(data):\n")
            f.write("        return {key: text_fix(value) for key, value in data.items()}\n\n")

            f.write("    try:\n")
            f.write("        final_out = {\n")
            f.write(f"                '{nombre_modulo}': {{\n")
            f.write("                    'Codigo': modulo[0].get('Codigo'),\n")
            f.write("                    'Nombre': modulo[0].get('Nombre'),\n")
            f.write("                    'Data': modulo[0].get('Data').get('flag'),\n")
            f.write("                    'Items': [process_item(data) for data in data_list] if data_list else None\n")
            f.write("                }\n")
            f.write("            }\n")
            f.write("    except:\n")
            f.write("        final_out = {\n")
            f.write(f"                '{nombre_modulo}': {{\n")
            f.write("                    'Codigo': codigo,\n")
            f.write("                    'Nombre': nombre,\n")
            f.write("                    'Data': False\n")
            f.write("                }\n")
            f.write("            }\n")
            f.write("    return final_out\n\n")

            f.write("if __name__ == '__main__':\n")
            f.write(f"    with open('response-dss1.json', 'r', encoding='UTF-8') as file:\n")
            f.write("        request = json.load(file)\n")
            f.write(f"        out = json.dumps(main(request), indent=4)\n\n")
            f.write("    with open('respond.json', 'w') as file:\n")
            f.write("        file.write(out)\n")

def main():
    with open('persona.json', 'r') as f:
        json_perfecto_persona = json.load(f).get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {})
    generar_scripts_por_modulo(json_perfecto_persona, 'persona')
    
    with open('empresa.json', 'r') as f:
        json_perfecto_empresa = json.load(f).get('dataSourceResponse', {}).get('GetReporteOnlineResponse', {})
    generar_scripts_por_modulo(json_perfecto_empresa, 'empresa')

if __name__ == '__main__':
    main()
