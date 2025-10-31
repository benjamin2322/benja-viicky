# Liceo Connect - MVP WebApp
# Autor: ChatGPT (GPT-5)
# Dependencias: Flask, Flask_SQLAlchemy, Flask_Cors
# Instalación: pip install -r requirements.txt
# Ejecución local: python app.py
# URL local: http://127.0.0.1:5000

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime
import os

# ===========================
# CONFIGURACIÓN
# ===========================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///liceo_connect.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

# ===========================
# MODELOS DE BASE DE DATOS
# ===========================
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.String(20), default=lambda: str(datetime.date.today()))
    presente = db.Column(db.Boolean, default=True)

class Calificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    materia = db.Column(db.String(50))
    nota = db.Column(db.Float)

class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emisor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    receptor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    contenido = db.Column(db.String(500))
    fecha = db.Column(db.String(20), default=lambda: str(datetime.datetime.now()))

with app.app_context():
    db.create_all()

# ===========================
# RUTAS API
# ===========================
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Usuario ya existe'}), 400
    u = Usuario(nombre=data['nombre'], rol=data['rol'], email=data['email'], password=data['password'])
    db.session.add(u)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario registrado exitosamente'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    u = Usuario.query.filter_by(email=data['email'], password=data['password']).first()
    if not u:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    return jsonify({'mensaje': 'Login exitoso', 'usuario': {'id': u.id, 'nombre': u.nombre, 'rol': u.rol}})

@app.route('/asistencia', methods=['POST'])
def marcar_asistencia():
    data = request.get_json()
    a = Asistencia(estudiante_id=data['estudiante_id'], presente=data.get('presente', True))
    db.session.add(a)
    db.session.commit()
    return jsonify({'mensaje': 'Asistencia registrada'})

@app.route('/asistencia/<int:estudiante_id>', methods=['GET'])
def ver_asistencia(estudiante_id):
    registros = Asistencia.query.filter_by(estudiante_id=estudiante_id).all()
    return jsonify([{'fecha': r.fecha, 'presente': r.presente} for r in registros])

@app.route('/calificaciones', methods=['POST'])
def agregar_calificacion():
    data = request.get_json()
    c = Calificacion(estudiante_id=data['estudiante_id'], materia=data['materia'], nota=data['nota'])
    db.session.add(c)
    db.session.commit()
    return jsonify({'mensaje': 'Calificación guardada'})

@app.route('/calificaciones/<int:estudiante_id>', methods=['GET'])
def ver_calificaciones(estudiante_id):
    notas = Calificacion.query.filter_by(estudiante_id=estudiante_id).all()
    return jsonify([{'materia': n.materia, 'nota': n.nota} for n in notas])

@app.route('/mensajes', methods=['POST'])
def enviar_mensaje():
    data = request.get_json()
    m = Mensaje(emisor_id=data['emisor_id'], receptor_id=data['receptor_id'], contenido=data['contenido'])
    db.session.add(m)
    db.session.commit()
    return jsonify({'mensaje': 'Mensaje enviado'})

@app.route('/mensajes/<int:usuario_id>', methods=['GET'])
def ver_mensajes(usuario_id):
    mensajes = Mensaje.query.filter(
        (Mensaje.emisor_id == usuario_id) | (Mensaje.receptor_id == usuario_id)
    ).all()
    return jsonify([{
        'emisor': m.emisor_id,
        'receptor': m.receptor_id,
        'contenido': m.contenido,
        'fecha': m.fecha
    } for m in mensajes])

# ===========================
# FRONTEND
# ===========================
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
