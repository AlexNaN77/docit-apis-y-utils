# reparar_esp.py
# Borra TODAS las especialidades, crea solo las 8 correctas,
# y re-vincula a todos los doctores con su especialidad correcta.
from pymongo import MongoClient

cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]
col_esp = db["especialidades"]
col_doc = db["doctores"]

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

# 1) guardamos el slug que cada doctor tenia (segun su especialidad actual)
#    para poder re-vincularlo despues
mapa_doc_slug = {}
esp_actuales = {str(e["_id"]): e for e in col_esp.find()}
for d in col_doc.find():
    esp_id = d.get("idEspecialidad")
    slug = None
    if esp_id and esp_id in esp_actuales:
        e = esp_actuales[esp_id]
        slug = e.get("slug")
        if not slug:
            # si no tiene slug, lo deducimos del nombre
            nom = (e.get("nombre") or "").strip().lower()
            for s, n in ESPECIALIDADES.items():
                if n.lower() == nom:
                    slug = s
                    break
    mapa_doc_slug[str(d["_id"])] = slug

# 2) borramos TODAS las especialidades
col_esp.delete_many({})
print("Especialidades viejas borradas.")

# 3) creamos las 8 correctas y guardamos su nuevo _id
nuevos_ids = {}
for slug, nombre in ESPECIALIDADES.items():
    r = col_esp.insert_one({"slug": slug, "nombre": nombre, "icono": "", "descripcion": ""})
    nuevos_ids[slug] = str(r.inserted_id)
print(f"Creadas {len(nuevos_ids)} especialidades limpias.")

# 4) re-vinculamos a cada doctor
revinculados = 0
for doc_id, slug in mapa_doc_slug.items():
    if slug and slug in nuevos_ids:
        from bson import ObjectId
        col_doc.update_one({"_id": ObjectId(doc_id)},
                           {"$set": {"idEspecialidad": nuevos_ids[slug]}})
        revinculados += 1

print(f"Doctores re-vinculados: {revinculados}")
print("LISTO. Ahora deberian quedar solo 8 especialidades.")
