from datetime import datetime                                                   # Importa herramientas para trabajar con fechas y horas
from werkzeug.security import generate_password_hash, check_password_hash       # Importa funcione para Encriptar contraseñas y Verificar si una contraseña es correcta
from flask_login import UserMixin                                               # Es como un "kit de herramientas" que le da "superpoderes" a la clase User para manejar sesiones de Login
from .extensions import db # ¡Importa db desde extensions.py!                   # Importa db que es el "traductor" para hablar con la base de datos



#                   MODELO USER (USUARIOS DEL SISTEMA)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True) # email
    password_hash = db.Column(db.String(355), nullable=False)
    role = db.Column(db.String(50), default='user') # 'admin', 'user', 'student'
    two_factor_code = db.Column(db.String(6))
    two_factor_expiry = db.Column(db.DateTime)

#               Métodos de la Clase User
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# --- NUEVO MODELO CURSO ---
class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True) # e.g., 'programadores-junior'
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    requisitos = db.Column(db.Text, nullable=False) # Guardaremos como texto, podrías usar JSON para más estructura
    activo = db.Column(db.Boolean, default=True, nullable=False) # Para habilitar/deshabilitar solicitudes
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Puedes omitir la línea de relación 'inscripciones' en Curso si quieres,
    # pero no causa problema si está ahí. La necesidad se verá más adelante.
    # inscripciones = db.relationship('Inscripcion', backref='curso_obj', lazy=True)

    def __repr__(self):
        return f'<Curso {self.nombre} ({self.slug})>'






#                   MODELO ESTUDIANTE (INFORMACIÓN DE ESTUDIANTES)
class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    grado = db.Column(db.String(100), nullable=False)
    institucion_educativa = db.Column(db.String(255), nullable=True) # O nullable=False si es obligatorio
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
    



#                   MODELO INSCRIPCIÓN (SOLICITUDES DE BECAS)
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

