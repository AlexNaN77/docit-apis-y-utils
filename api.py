from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import bcrypt

app = Flask(__name__)
CORS(app)

cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]

col_usuarios = db["usuarios"]
col_doctores = db["doctores"]
col_especialidades = db["especialidades"]
col_consultorios = db["consultorios"]
col_servicios = db["servicios"]
col_horarios = db["horarios"]
col_citas = db["citas"]
col_resenas = db["resenas"]


def limpiar(doc):
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d


def limpiarLista(cursor):
    out = []
    for x in cursor:
        out.append(limpiar(x))
    return out


@app.route("/", methods=["GET"])
def home():
    return jsonify({"ok": True, "msg": "DoCit API jalando perron"})


# ---------- LOGIN
@app.route("/login", methods=["POST"])
def login():
    d = request.get_json(silent=True) or {}
    correo = d.get("correo", "").strip().lower()
    contra = d.get("contrasena", "")
    if not correo or not contra:
        return jsonify({"error": "Faltan datos"}), 400
    u = col_usuarios.find_one({"correo": correo})
    if not u:
        return jsonify({"error": "Usuario no existe"}), 404
    try:
        ok = bcrypt.checkpw(contra.encode("utf-8"), u["contrasena"].encode("utf-8"))
    except Exception:
        ok = False
    if not ok:
        return jsonify({"error": "Contraseña incorrecta"}), 401
    u = limpiar(u)
    u["idUsuario"] = u.pop("_id")
    u.pop("contrasena", None)
    return jsonify(u)


# ---------- REGISTRAR USUARIO
@app.route("/usuarios", methods=["POST"])
def registrar():
    d = request.get_json(silent=True) or {}
    correo = (d.get("correo") or "").strip().lower()
    contra = d.get("contrasena") or ""
    nombre = d.get("nombre") or ""
    if not correo or not contra or not nombre:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    if col_usuarios.find_one({"correo": correo}):
        return jsonify({"error": "Ya existe un usuario con ese correo"}), 409
    hashed = bcrypt.hashpw(contra.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    nuevo = {
        "nombre": nombre,
        "apellidoPaterno": d.get("apellidoPaterno", ""),
        "apellidoMaterno": d.get("apellidoMaterno", ""),
        "correo": correo,
        "telefono": d.get("telefono", ""),
        "curp": d.get("curp", ""),
        "contrasena": hashed,
        "fechaNacimiento": d.get("fechaNacimiento", ""),
        "altura": d.get("altura"),
        "peso": d.get("peso"),
        "fotoPerfil": d.get("fotoPerfil", ""),
        "fechaRegistro": datetime.utcnow().isoformat(),
        "estadoCuenta": "activa"
    }
    r = col_usuarios.insert_one(nuevo)
    nuevo = limpiar(nuevo)
    nuevo["idUsuario"] = str(r.inserted_id)
    nuevo.pop("_id", None)
    nuevo.pop("contrasena", None)
    return jsonify(nuevo), 201


# ---------- ACTUALIZAR USUARIO
@app.route("/usuarios/<id>", methods=["PUT"])
def actualizar_usuario(id):
    d = request.get_json(silent=True) or {}
    d.pop("contrasena", None)
    d.pop("_id", None)
    d.pop("idUsuario", None)
    try:
        col_usuarios.update_one({"_id": ObjectId(id)}, {"$set": d})
    except Exception:
        return jsonify({"error": "id invalido"}), 400
    u = col_usuarios.find_one({"_id": ObjectId(id)})
    u = limpiar(u)
    if u:
        u["idUsuario"] = u.pop("_id")
        u.pop("contrasena", None)
    return jsonify(u)


# ---------- ESPECIALIDADES
@app.route("/especialidades", methods=["GET"])
def especialidades():
    data = limpiarLista(col_especialidades.find())
    for e in data:
        e["idEspecialidad"] = e.pop("_id")
    return jsonify(data)


# ---------- DOCTORES (lista con filtros)
@app.route("/doctores", methods=["GET"])
def doctores():
    q = {}
    esp = request.args.get("especialidad")
    nombre = request.args.get("nombre")
    consul = request.args.get("consultorio")
    if esp:
        q["idEspecialidad"] = esp
    if nombre:
        q["$or"] = [
            {"nombre": {"$regex": nombre, "$options": "i"}},
            {"apellidoPaterno": {"$regex": nombre, "$options": "i"}}
        ]
    if consul:
        q["idConsultorio"] = consul
    data = []
    for doc in col_doctores.find(q):
        data.append(armar_doctor(doc))
    return jsonify(data)


# ---------- DETALLE DE UN DOCTOR
@app.route("/doctores/<id>", methods=["GET"])
def doctor(id):
    try:
        doc = col_doctores.find_one({"_id": ObjectId(id)})
    except Exception:
        doc = col_doctores.find_one({"idDoctor": id})
    if not doc:
        return jsonify({"error": "no encontrado"}), 404
    return jsonify(armar_doctor(doc, full=True))


def armar_doctor(doc, full=False):
    out = limpiar(doc)
    out["idDoctor"] = out.pop("_id")

    # especialidad
    esp_id = out.get("idEspecialidad")
    if esp_id:
        try:
            esp = col_especialidades.find_one({"_id": ObjectId(esp_id)})
        except Exception:
            esp = None
        if esp:
            esp = limpiar(esp)
            esp["idEspecialidad"] = esp.pop("_id")
            out["especialidad"] = esp

    # consultorio
    cons_id = out.get("idConsultorio")
    if cons_id:
        try:
            cons = col_consultorios.find_one({"_id": ObjectId(cons_id)})
        except Exception:
            cons = None
        if cons:
            cons = limpiar(cons)
            cons["idConsultorio"] = cons.pop("_id")
            out["consultorio"] = cons

    # servicios SIEMPRE (no solo en full) para que se vean en la lista tambien
    servs = limpiarLista(col_servicios.find({"idDoctor": out["idDoctor"]}))
    for s in servs:
        s["idServicio"] = s.pop("_id")
    out["servicios"] = servs

    if full:
        out["imagenes"] = out.get("imagenes", [])
        res = limpiarLista(col_resenas.find({"idDoctor": out["idDoctor"]}))
        for r in res:
            r["idResena"] = r.pop("_id")
        out["resenas"] = res
    return out


# ---------- HORARIOS DEL DOCTOR EN UNA FECHA
@app.route("/doctores/<id>/horarios", methods=["GET"])
def horarios_doc(id):
    fecha = request.args.get("fecha", "")
    dia_nombre = ""
    if fecha:
        try:
            f = datetime.strptime(fecha, "%Y-%m-%d")
            dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
            dia_nombre = dias[f.weekday()]
        except Exception:
            pass

    base = list(col_horarios.find({"idDoctor": id}))
    if dia_nombre:
        base = [h for h in base if (h.get("diaSemana") or "").lower() == dia_nombre]

    ocupadas = set()
    if fecha:
        for c in col_citas.find({"idDoctor": id, "fecha": fecha,
                                 "estado": {"$in": ["pendiente", "confirmada"]}}):
            ocupadas.add(c.get("horaInicio"))

    out = []
    for h in base:
        slots = generar_slots(h.get("horaInicio"), h.get("horaFin"),
                              h.get("duracionCita", 30))
        for s in slots:
            if s["horaInicio"] in ocupadas:
                continue
            out.append({
                "idHorario": str(h["_id"]) + "_" + s["horaInicio"],
                "diaSemana": h.get("diaSemana"),
                "horaInicio": s["horaInicio"],
                "horaFin": s["horaFin"],
                "duracionCita": h.get("duracionCita", 30),
                "disponible": True
            })
    return jsonify(out)


def generar_slots(hi, hf, dur):
    if not hi or not hf:
        return []
    a = int(hi[:2]) * 60 + int(hi[3:5])
    b = int(hf[:2]) * 60 + int(hf[3:5])
    out = []
    while a + dur <= b:
        h1 = "%02d:%02d" % (a // 60, a % 60)
        a2 = a + dur
        h2 = "%02d:%02d" % (a2 // 60, a2 % 60)
        out.append({"horaInicio": h1, "horaFin": h2})
        a = a2
    return out


# ---------- RESEÑAS
@app.route("/doctores/<id>/resenas", methods=["GET"])
def resenas_doc(id):
    res = limpiarLista(col_resenas.find({"idDoctor": id}))
    for r in res:
        r["idResena"] = r.pop("_id")
        try:
            u = col_usuarios.find_one({"_id": ObjectId(r.get("idUsuario", ""))})
            if u:
                r["usuario"] = {
                    "nombre": u.get("nombre", ""),
                    "apellidoPaterno": u.get("apellidoPaterno", ""),
                    "apellidoMaterno": u.get("apellidoMaterno", "")
                }
        except Exception:
            pass
    return jsonify(res)


@app.route("/resenas", methods=["POST"])
def crear_resena():
    d = request.get_json(silent=True) or {}
    if not d.get("calificacion") or not d.get("idDoctor") or not d.get("idUsuario"):
        return jsonify({"error": "faltan datos"}), 400
    d["fechaCreacion"] = datetime.utcnow().isoformat()
    r = col_resenas.insert_one(d)
    actualizar_promedio(d["idDoctor"])
    d = limpiar(d)
    d["idResena"] = str(r.inserted_id)
    d.pop("_id", None)
    return jsonify(d), 201


def actualizar_promedio(idDoc):
    todas = list(col_resenas.find({"idDoctor": idDoc}))
    if not todas:
        return
    suma = sum([float(r.get("calificacion", 0)) for r in todas])
    prom = suma / len(todas)
    try:
        col_doctores.update_one({"_id": ObjectId(idDoc)},
                                {"$set": {"promedioCalificacion": round(prom, 2)}})
    except Exception:
        pass


# ---------- CITAS
@app.route("/citas/usuario/<id>", methods=["GET"])
def citas_usuario(id):
    citas = list(col_citas.find({"idUsuario": id}).sort("fecha", -1))
    out = []
    for c in citas:
        out.append(armar_cita(c))
    return jsonify(out)


def armar_cita(c):
    out = limpiar(c)
    out["idCita"] = out.pop("_id")
    try:
        d = col_doctores.find_one({"_id": ObjectId(out.get("idDoctor", ""))})
        if d:
            out["doctor"] = armar_doctor(d)
    except Exception:
        pass
    return out


@app.route("/citas", methods=["POST"])
def crear_cita():
    d = request.get_json(silent=True) or {}
    user = d.get("usuario") or {}
    doc = d.get("doctor") or {}
    idUsuario = d.get("idUsuario") or user.get("idUsuario")
    idDoctor = d.get("idDoctor") or doc.get("idDoctor")
    if not idUsuario or not idDoctor or not d.get("fecha"):
        return jsonify({"error": "datos incompletos"}), 400

    nueva = {
        "idUsuario": idUsuario,
        "idDoctor": idDoctor,
        "fecha": d.get("fecha"),
        "horaInicio": d.get("horaInicio"),
        "horaFin": d.get("horaFin"),
        "estado": d.get("estado", "pendiente"),
        "motivoConsulta": d.get("motivoConsulta", ""),
        "notas": d.get("notas", ""),
        "fechaCreacion": datetime.utcnow().isoformat()
    }
    r = col_citas.insert_one(nueva)
    nueva = limpiar(nueva)
    nueva["idCita"] = str(r.inserted_id)
    nueva.pop("_id", None)
    return jsonify(nueva), 201


@app.route("/citas/<id>", methods=["PUT"])
def update_cita(id):
    d = request.get_json(silent=True) or {}
    d.pop("_id", None)
    d.pop("idCita", None)
    try:
        col_citas.update_one({"_id": ObjectId(id)}, {"$set": d})
    except Exception:
        return jsonify({"error": "id invalido"}), 400
    c = col_citas.find_one({"_id": ObjectId(id)})
    return jsonify(armar_cita(c))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
