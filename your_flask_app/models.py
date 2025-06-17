from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db # ¡Importa db desde extensions.py!
from datetime import datetime




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True) # email
    password_hash = db.Column(db.String(355), nullable=False)
    role = db.Column(db.String(50), default='user') # 'admin', 'user', 'student'
    two_factor_code = db.Column(db.String(6))
    two_factor_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    grado = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(50), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    anio_solicitud = db.Column(db.Integer, nullable=False, default=lambda: datetime.utcnow().year)
    sexo = db.Column(db.String(20), nullable=False)  # <--- NUEVO
    motivo = db.Column(db.Text, nullable=False)      # <--- NUEVO
    veracidad = db.Column(db.Boolean, nullable=False, default=False)  # <--- NUEVO

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=True)
    user = db.relationship('User', backref=db.backref('estudiante', uselist=False, lazy=True))

    def __repr__(self):
        return f'<Estudiante {self.nombre} {self.apellidos}>'

class Inscripcion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    curso_slug = db.Column(db.String(100), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='pendiente')
    
    # --- NUEVO CAMPO: Para la razón de rechazo ---
    razon_rechazo = db.Column(db.Text, nullable=True) # Usamos Text para más longitud, y Nullable=True porque puede estar vacío

    estudiante = db.relationship('Estudiante', backref=db.backref('inscripciones', lazy=True))

    def __repr__(self):
        return f'<Inscripcion {self.id} - Estudiante: {self.estudiante_id} - Curso: {self.curso_slug}>'

