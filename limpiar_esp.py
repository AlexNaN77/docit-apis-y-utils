# limpiar_esp.py
# Borra duplicados de especialidades dejando solo una por slug.
from pymongo import MongoClient

cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]
col = db["especialidades"]

vistos = set()
borrados = 0
for e in list(col.find()):
    slug = e.get("slug") or (e.get("nombre") or "").strip().lower()
    if slug in vistos:
        col.delete_one({"_id": e["_id"]})
        borrados += 1
    else:
        vistos.add(slug)

print(f"Listo. Especialidades únicas: {len(vistos)}, duplicados borrados: {borrados}")
