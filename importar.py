# importar.py
# Lee el JSON exportado de la app web y lo mete a Mongo en el formato que espera la app Android.
# Correr UNA vez: python importar.py docit-db.json

import sys
import json
from datetime import datetime
from pymongo import MongoClient

# ---- conexion (igual que tu API) ----
cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]
col_doctores = db["doctores"]
col_especialidades = db["especialidades"]
col_servicios = db["servicios"]

# mapa de id de especialidad (web) -> nombre bonito (app)
ESPECIALIDADES = {
    "medicina_general": "Medicina general",
    "cardiologia": "Cardiología",
    "odontologia": "Odontología",
    "ginecologia": "Ginecología",
    "psicologia": "Psicología",
    "nutricion": "Nutrición",
    "oftalmologia": "Oftalmología",
    "traumatologia": "Traumatología",
}


def asegurar_especialidades():
    # crea las especialidades en su coleccion si no existen, y devuelve {idWeb: idMongoString}
    ids = {}
    for id_web, nombre in ESPECIALIDADES.items():
        existente = col_especialidades.find_one({"slug": id_web})
        if existente:
            ids[id_web] = str(existente["_id"])
        else:
            r = col_especialidades.insert_one({
                "slug": id_web,
                "nombre": nombre,
                "icono": "",
                "descripcion": ""
            })
            ids[id_web] = str(r.inserted_id)
    return ids


def main():
    if len(sys.argv) < 2:
        print("Uso: python importar.py <archivo.json>")
        return

    ruta = sys.argv[1]
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    # el export puede venir como {doctors:[...]} o como lista directa
    doctores = datos.get("doctors") if isinstance(datos, dict) else datos
    if not doctores:
        print("No encontre doctores en el JSON.")
        return

    print(f"Encontrados {len(doctores)} doctores en el JSON.")

    ids_esp = asegurar_especialidades()

    nuevos = 0
    actualizados = 0

    for d in doctores:
        id_web = d.get("id") or ("d_" + str(datetime.utcnow().timestamp()))
        nombre_completo = (d.get("name") or "").strip()
        spec = d.get("specialty") or "medicina_general"

        # servicios: la web guarda [{name, price}], la app quiere {nombre, precio, duracion}
        servicios = []
        for s in (d.get("services") or []):
            servicios.append({
                "nombre": s.get("name", ""),
                "descripcion": "",
                "precio": float(s.get("price") or 0),
                "duracion": 30
            })

        # imagenes: la foto base64 la guardamos como una imagen tipo "perfil"
        imagenes = []
        foto = d.get("photo")
        if foto:
            imagenes.append({"urlImagen": foto, "tipoImagen": "perfil"})

        doc_mongo = {
            "idWeb": id_web,                       # para no duplicar al re-importar
            "nombre": nombre_completo,             # OPCION A: nombre completo aqui
            "apellidoPaterno": "",
            "apellidoMaterno": "",
            "correo": d.get("email", ""),
            "telefono": d.get("phone", ""),
            "whatsapp": d.get("phone", ""),
            "cedulaProfesional": d.get("license", ""),
            "fotoPerfil": foto or "",
            "descripcion": d.get("notes", ""),
            "direccion": d.get("address", ""),     # campo nuevo
            "mapsUrl": d.get("mapsUrl", ""),       # campo nuevo
            "horarioTexto": d.get("schedule", ""), # campo nuevo
            "promedioCalificacion": 4.5,
            "estadoCuenta": "activa",
            "fechaRegistro": datetime.utcnow().isoformat(),
            "idEspecialidad": ids_esp.get(spec),
            "imagenes": imagenes,
            "subidoPor": d.get("uploadedBy", "")
        }

        # upsert por idWeb para que puedas re-correr sin duplicar
        existente = col_doctores.find_one({"idWeb": id_web})
        if existente:
            doc_id = existente["_id"]
            col_doctores.update_one({"_id": doc_id}, {"$set": doc_mongo})
            actualizados += 1
        else:
            r = col_doctores.insert_one(doc_mongo)
            doc_id = r.inserted_id
            nuevos += 1

        # servicios: borramos los previos de este doctor y reinsertamos
        col_servicios.delete_many({"idDoctor": str(doc_id)})
        for s in servicios:
            s["idDoctor"] = str(doc_id)
            col_servicios.insert_one(s)

    print(f"Listo. Nuevos: {nuevos}, Actualizados: {actualizados}")
    print("Especialidades aseguradas:", len(ids_esp))


if __name__ == "__main__":
    main()
