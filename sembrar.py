from pymongo import MongoClient
from datetime import datetime
import bcrypt

cli = MongoClient("mongodb://localhost:27017")
db = cli["docit"]

# limpiamos las colecciones por si las ejecutas varias veces
db.usuarios.delete_many({})
db.doctores.delete_many({})
db.especialidades.delete_many({})
db.consultorios.delete_many({})
db.servicios.delete_many({})
db.horarios.delete_many({})
db.citas.delete_many({})
db.resenas.delete_many({})

# ---------- ESPECIALIDADES
esp_data = [
    {"nombre": "Medicina general", "icono": "ic_medico", "descripcion": "Atención médica general"},
    {"nombre": "Pediatría", "icono": "ic_medico", "descripcion": "Atención para niños"},
    {"nombre": "Dermatología", "icono": "ic_medico", "descripcion": "Piel y cabello"},
    {"nombre": "Cardiología", "icono": "ic_medico", "descripcion": "Corazón"},
    {"nombre": "Odontología", "icono": "ic_medico", "descripcion": "Dientes y encías"},
    {"nombre": "Ginecología", "icono": "ic_medico", "descripcion": "Salud de la mujer"},
    {"nombre": "Psicología", "icono": "ic_medico", "descripcion": "Salud mental"},
    {"nombre": "Nutrición", "icono": "ic_medico", "descripcion": "Alimentación saludable"},
    {"nombre": "Oftalmología", "icono": "ic_medico", "descripcion": "Ojos"},
]
esp_ids = []
for e in esp_data:
    r = db.especialidades.insert_one(e)
    esp_ids.append(str(r.inserted_id))

# ---------- CONSULTORIOS
cons_data = [
    {"nombre": "Clínica Centro", "planta": "Planta baja", "salon": "101",
     "estado": "Veracruz", "codigoPostal": "94500",
     "referencias": "Frente al parque", "latitud": 18.8442, "longitud": -97.1015},
    {"nombre": "Centro Médico DoCit", "planta": "Piso 2", "salon": "204",
     "estado": "Veracruz", "codigoPostal": "94500",
     "referencias": "A un lado del CBTIS 226", "latitud": 18.8445, "longitud": -97.1023},
    {"nombre": "Consultorios del Valle", "planta": "Piso 1", "salon": "112",
     "estado": "Veracruz", "codigoPostal": "94530",
     "referencias": "Cerca de la presidencia", "latitud": 18.8401, "longitud": -97.1080},
]
cons_ids = []
for c in cons_data:
    r = db.consultorios.insert_one(c)
    cons_ids.append(str(r.inserted_id))

# ---------- DOCTORES
docs_data = [
    {"nombre": "Roberto", "apellidoPaterno": "Mendoza", "apellidoMaterno": "Luna",
     "correo": "rmendoza@docit.com", "telefono": "2281234567",
     "cedulaProfesional": "5847291", "whatsapp": "5212281234567",
     "descripcion": "Médico cirujano egresado de la UNAM con 12 años de experiencia.",
     "promedioCalificacion": 4.7, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[0], "idConsultorio": cons_ids[0]},
    {"nombre": "Lupita", "apellidoPaterno": "García", "apellidoMaterno": "Ramírez",
     "correo": "lgarcia@docit.com", "telefono": "2289876543",
     "cedulaProfesional": "5847292", "whatsapp": "5212289876543",
     "descripcion": "Pediatra con 8 años de experiencia, especialista en lactantes.",
     "promedioCalificacion": 4.9, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[1], "idConsultorio": cons_ids[1]},
    {"nombre": "Carlos", "apellidoPaterno": "Sánchez", "apellidoMaterno": "Pérez",
     "correo": "csanchez@docit.com", "telefono": "2285555444",
     "cedulaProfesional": "5847293", "whatsapp": "5212285555444",
     "descripcion": "Dermatólogo certificado con especialidad en acné y dermatitis.",
     "promedioCalificacion": 4.6, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[2], "idConsultorio": cons_ids[0]},
    {"nombre": "Andrea", "apellidoPaterno": "Hernández", "apellidoMaterno": "Cruz",
     "correo": "ahernandez@docit.com", "telefono": "2287778888",
     "cedulaProfesional": "5847294", "whatsapp": "5212287778888",
     "descripcion": "Cardióloga con 15 años de experiencia. Atiende emergencias.",
     "promedioCalificacion": 4.8, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[3], "idConsultorio": cons_ids[2]},
    {"nombre": "Juan", "apellidoPaterno": "López", "apellidoMaterno": "Hernández",
     "correo": "jlopez@docit.com", "telefono": "2283334444",
     "cedulaProfesional": "5847295", "whatsapp": "5212283334444",
     "descripcion": "Odontólogo general y especialista en ortodoncia.",
     "promedioCalificacion": 4.5, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[4], "idConsultorio": cons_ids[1]},
    {"nombre": "Mariana", "apellidoPaterno": "Torres", "apellidoMaterno": "Vega",
     "correo": "mtorres@docit.com", "telefono": "2281112222",
     "cedulaProfesional": "5847296", "whatsapp": "5212281112222",
     "descripcion": "Ginecóloga obstetra con 10 años de experiencia.",
     "promedioCalificacion": 4.9, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[5], "idConsultorio": cons_ids[0]},
    {"nombre": "Sergio", "apellidoPaterno": "Morales", "apellidoMaterno": "Castro",
     "correo": "smorales@docit.com", "telefono": "2289990000",
     "cedulaProfesional": "5847297", "whatsapp": "5212289990000",
     "descripcion": "Psicólogo clínico, terapia cognitivo conductual.",
     "promedioCalificacion": 4.7, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[6], "idConsultorio": cons_ids[2]},
    {"nombre": "Patricia", "apellidoPaterno": "Ruiz", "apellidoMaterno": "Soto",
     "correo": "pruiz@docit.com", "telefono": "2284445555",
     "cedulaProfesional": "5847298", "whatsapp": "5212284445555",
     "descripcion": "Nutrióloga, planes de alimentación personalizados.",
     "promedioCalificacion": 4.8, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[7], "idConsultorio": cons_ids[1]},
    {"nombre": "Daniel", "apellidoPaterno": "Flores", "apellidoMaterno": "Reyes",
     "correo": "dflores@docit.com", "telefono": "2286667777",
     "cedulaProfesional": "5847299", "whatsapp": "5212286667777",
     "descripcion": "Oftalmólogo, cirugías refractivas y de cataratas.",
     "promedioCalificacion": 4.6, "estadoCuenta": "activa",
     "idEspecialidad": esp_ids[8], "idConsultorio": cons_ids[0]},
]
doc_ids = []
for d in docs_data:
    d["fechaRegistro"] = datetime.utcnow().isoformat()
    d["imagenes"] = []
    r = db.doctores.insert_one(d)
    doc_ids.append(str(r.inserted_id))

# ---------- SERVICIOS (varios por doctor)
servicios_template = [
    ("Consulta general", 350, 30, "Consulta médica con diagnóstico"),
    ("Receta médica", 200, 15, "Renovación de receta o consulta corta"),
    ("Chequeo anual", 800, 60, "Revisión completa con estudios básicos")
]
for didx, did in enumerate(doc_ids):
    for s in servicios_template:
        db.servicios.insert_one({
            "idDoctor": did,
            "nombre": s[0],
            "precio": s[1],
            "duracion": s[2],
            "descripcion": s[3]
        })

# ---------- HORARIOS (lunes a viernes 9 a 14, sabado 9 a 13)
dias_semana = ["lunes", "martes", "miercoles", "jueves", "viernes"]
for did in doc_ids:
    for dia in dias_semana:
        db.horarios.insert_one({
            "idDoctor": did,
            "diaSemana": dia,
            "horaInicio": "09:00",
            "horaFin": "14:00",
            "duracionCita": 30,
            "disponible": True
        })
    db.horarios.insert_one({
        "idDoctor": did,
        "diaSemana": "sabado",
        "horaInicio": "09:00",
        "horaFin": "13:00",
        "duracionCita": 30,
        "disponible": True
    })

# ---------- USUARIO DE PRUEBA
contra = bcrypt.hashpw("test123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
db.usuarios.insert_one({
    "nombre": "Demo",
    "apellidoPaterno": "Usuario",
    "apellidoMaterno": "Prueba",
    "correo": "test@docit.com",
    "telefono": "2281111111",
    "curp": "DEMO010101HVZRRR01",
    "contrasena": contra,
    "fechaNacimiento": "01/01/2001",
    "altura": 1.70,
    "peso": 70,
    "fechaRegistro": datetime.utcnow().isoformat(),
    "estadoCuenta": "activa"
})

# ---------- ALGUNAS RESEÑAS DE EJEMPLO
db.resenas.insert_one({
    "idDoctor": doc_ids[0],
    "idUsuario": "demo",
    "calificacion": 5,
    "comentario": "Excelente atención, muy profesional.",
    "fechaCreacion": datetime.utcnow().isoformat()
})
db.resenas.insert_one({
    "idDoctor": doc_ids[0],
    "idUsuario": "demo",
    "calificacion": 4,
    "comentario": "Muy bueno aunque tuve que esperar un poco.",
    "fechaCreacion": datetime.utcnow().isoformat()
})

print("Listo. Datos sembrados:")
print("- Especialidades:", len(esp_ids))
print("- Consultorios:", len(cons_ids))
print("- Doctores:", len(doc_ids))
print("- Usuario de prueba: test@docit.com / test123")
