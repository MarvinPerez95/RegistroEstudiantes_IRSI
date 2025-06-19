#                   Define TODOS los formularios del sistema (login, registro, solicitud de beca) y sus validacione.
#                   


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed                                                                                                                 # Importa la clase base para crear formularios seguros con Flask
from wtforms import StringField, SelectField, DateField, TextAreaField, BooleanField, SubmitField, HiddenField,PasswordField, IntegerField      # Omporta todos los tipos de campos que pueden tener un formunlario
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, Regexp                                          # Importa los validadores (reglas de validación)
from .models import User, Estudiante # Importa Estudiante para validación si es necesario                                                       # Importa los modelos para hcer validaciones con la base de datos
from datetime import date                                                                                                                       # Pata trabajar con fechas
from .data import LATAM_PAISES_CIUDADES # Importa tu diccionario de datos      
from flask_wtf.file import FileField, FileRequired, FileAllowed                                                                 # Importa el diccionario de países y cidudades


#                   FORMULARIO DE LOGIN
class LoginForm(FlaskForm):
    username = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


#                   FORMULARIO DE CÓDIGO 2FA
class TwoFactorForm(FlaskForm):
    code = StringField('Código 2FA', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verificar')


#                   FORMULARIO DE REGISTRO
class RegistrationForm(FlaskForm):
    username = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Ese correo electrónico ya está registrado.')


#                   FORMULARIO DE ESTUDIANTE (M.C)
# Definición CORRECTA Y ÚNICA del EstudianteForm
class EstudianteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=100)])
    
    pais = SelectField('País', choices=[('', 'Seleccione un país')] + [(p, p) for p in sorted(LATAM_PAISES_CIUDADES.keys())], validators=[DataRequired()])
    ciudad = SelectField('Ciudad', choices=[], validators=[DataRequired()])
    
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=200)])
    grado = SelectField('Último Grado de Estudios', choices=[
        ('', 'Seleccione uno'),
        ('Primaria', 'Primaria'),
        ('Secundaria', 'Secundaria'),
        ('Bachiller/Preparatoria', 'Bachiller/Preparatoria'),
        ('Técnico', 'Técnico'),
        ('Universitario Incompleto', 'Universitario Incompleto'),
        ('Universitario Completo', 'Universitario Completo'),
        ('Posgrado', 'Posgrado')
    ], validators=[DataRequired()])
    institucion_educativa = StringField('Institución Educativa', validators=[DataRequired(), Length(max=100)]) # O ajusta el validador a Optional() si no es obligatorio

    dni = StringField('Documento de Identificación', validators=[DataRequired(), Length(max=50)])
    fecha_nacimiento = DateField('Fecha de Nacimiento (YYYY-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])

    # NUEVO CAMPO: Sexo
    sexo = SelectField('Sexo', choices=[
        ('', 'Seleccione sexo'),
        ('Hombre', 'Hombre'),
        ('Mujer', 'Mujer'),
        ('Otro', 'Otro')
    ], validators=[DataRequired()])

    correo = StringField('Correo Electrónico Personal', validators=[DataRequired(), Email(), Length(max=120)], render_kw={"readonly": True})
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20), Regexp(r'^\+?[0-9\s\-\(\)]{8,20}$', message="Formato de teléfono inválido.")])
    
    # ANIO DE SOLICITUD oculto, se maneja con HiddenField para que no sea visible
    anio_solicitud = HiddenField(default=str(date.today().year))

    curso_a_inscribir = SelectField('Curso al que desea aplicar', validators=[Optional()])


    # NUEVO CAMPO: Motivo para solicitar la beca
    motivo = TextAreaField('¿Por qué desea obtener esta beca?', validators=[DataRequired(), Length(min=10, max=500)])

    # NUEVO CAMPO: Declaración de veracidad (checkbox)
    veracidad = BooleanField('Confirmo que la información proporcionada es verídica y verificable', validators=[DataRequired(message="Debes confirmar que la información es verídica.")])

    submit = SubmitField('Enviar Solicitud')

    def validate_fecha_nacimiento(self, field):
        if field.data > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser en el futuro.')


#                   FORMULARIO DE APROBACIÓN/RECHAZO (para Admin)
# Nuevo formulario para la aprobación/rechazo de inscripciones (para el admin)
class InscripcionApprovalForm(FlaskForm):
    estado = SelectField('Estado', choices=[
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada')
    ], validators=[DataRequired()])
    razon_rechazo = TextAreaField('Razón de Rechazo (Opcional)', validators=[Optional()])
    submit = SubmitField('Actualizar Estado')

    def validate(self, *args, **kwargs):
        if not super().validate(*args, **kwargs):
            return False
        
        # Si el estado es 'rechazada' y no hay razón de rechazo, añadir error
        if self.estado.data == 'rechazada' and not self.razon_rechazo.data:
            self.razon_rechazo.errors.append('Debes proporcionar una razón si el estado es "Rechazada".')
            return False
        return True
    

# NUEVO FORMULARIO PARA SUBIR ARCHIVOS EXCEL (G)
class UploadExcelForm(FlaskForm):
    excel_file = FileField('Archivo Excel', validators=[
        FileRequired(message='Debes seleccionar un archivo.'),
        FileAllowed(['xlsx', 'xls'], message='Solo se permiten archivos Excel (.xlsx, .xls)')
    ])
    submit = SubmitField('Subir y Procesar')