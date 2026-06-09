# ver_esp.py - solo muestra que hay, no borra nada
from pymongo import MongoClient

cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]
col = db["especialidades"]

todas = list(col.find())
print(f"TOTAL especialidades en Mongo: {len(todas)}\n")
for e in todas:
    print(f"  _id={e['_id']}  slug={e.get('slug', '(SIN SLUG)')}  nombre={e.get('nombre', '(sin nombre)')}")
