import json
import os

# Definir el JSON perfecto para persona y empresa
json_perfecto_persona = {
    "Nombre": "",
    "NumeroOperacion": "",
    "DatosPrincipales": {},
    "Modulos": []
}

json_perfecto_empresa = {
    "Nombre": "",
    "NumeroOperacion": "",
    "DatosPrincipales": {},
    "Modulos": []
}

def estandarizar_json(data, tipo):
    json_estandarizado = json_perfecto_persona.copy() if tipo == "persona" else json_perfecto_empresa.copy()
    json_estandarizado["Nombre"] = data.get("ReporteCrediticio", {}).get("Nombre", "")
    json_estandarizado["NumeroOperacion"] = data.get("ReporteCrediticio", {}).get("NumeroOperacion", "")
    json_estandarizado["DatosPrincipales"] = data.get("ReporteCrediticio", {}).get("DatosPrincipales", {})
    
    modulos = data.get("ReporteCrediticio", {}).get("Modulos", {}).get("Modulo", [])
    for modulo in modulos:
        mod = {
            "Nombre": modulo.get("Nombre", ""),
            "Codigo": modulo.get("Codigo", ""),
            "Data": modulo.get("Data", {})
        }
        json_estandarizado["Modulos"].append(mod)
    
    return json_estandarizado

def procesar_archivos(carpeta, tipo):
    archivos = [f for f in os.listdir(carpeta) if f.endswith('.json')]
    json_estandarizados = []

    for archivo in archivos:
        with open(os.path.join(carpeta, archivo), 'r') as f:
            data = json.load(f)
            json_estandarizado = estandarizar_json(data["dataSourceResponse"]["GetReporteOnlineResponse"], tipo)
            json_estandarizados.append(json_estandarizado)
    
    return json_estandarizados

def guardar_json_estandarizados(json_estandarizados, tipo):
    with open(f'{tipo}_json_estandarizados.json', 'w') as f:
        json.dump(json_estandarizados, f, indent=4)

# Procesar JSON de personas y empresas
json_estandarizados_persona = procesar_archivos('Persona', 'persona')
guardar_json_estandarizados(json_estandarizados_persona, 'persona')

json_estandarizados_empresa = procesar_archivos('Empresa', 'empresa')
guardar_json_estandarizados(json_estandarizados_empresa, 'empresa')
