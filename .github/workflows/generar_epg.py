import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

URL_XML = "https://raw.githubusercontent.com/Puticastillo/EPGCL/main/smithers/guia-de-programacion.xml"

print("Descargando XML...")
xml_content = requests.get(URL_XML).content

print("Parseando XML...")
root = ET.fromstring(xml_content)

# Crear carpeta epg
os.makedirs("epg", exist_ok=True)

ahora = datetime.utcnow()
limite = ahora + timedelta(hours=24)

canales = {}

for programme in root.findall("programme"):

    canal = programme.attrib["channel"]

    inicio_str = programme.attrib["start"][:14]
    fin_str = programme.attrib["stop"][:14]

    inicio = datetime.strptime(inicio_str, "%Y%m%d%H%M%S")
    fin = datetime.strptime(fin_str, "%Y%m%d%H%M%S")

    # Solo próximas 24 horas
    if fin < ahora or inicio > limite:
        continue

    titulo = programme.findtext("title", "")
    descripcion = programme.findtext("desc", "")
    icono = ""

    icon = programme.find("icon")
    if icon is not None:
        icono = icon.attrib.get("src", "")

    item = {
        "titulo": titulo,
        "descripcion": descripcion,
        "inicio": inicio.isoformat(),
        "fin": fin.isoformat(),
        "icono": icono
    }

    canales.setdefault(canal, []).append(item)

print("Generando JSON...")

for canal, programas in canales.items():

    programas.sort(key=lambda x: x["inicio"])

    salida = {
        "actual": programas[0] if len(programas) > 0 else None,
        "siguiente": programas[1] if len(programas) > 1 else None,
        "lista": programas
    }

    with open(f"epg/{canal}.json", "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

print("Finalizado")
