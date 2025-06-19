# your_flask_app/blueprints/main.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import Estudiante, Inscripcion, Curso ,User
from ..forms import EstudianteForm, InscripcionApprovalForm
from ..extensions import db
from ..decorators import role_required
from datetime import date
import bleach

# ✅ Importa los diccionarios desde data.py
from ..data import LATAM_PAISES_CIUDADES, NOMBRE_DOCUMENTO_POR_PAIS

main_bp = Blueprint('main', __name__, template_folder='../templates')

@main_bp.route('/')
@main_bp.route('/index')
def index():
    # Obtener solo los cursos activos para mostrar en la página principal
    cursos_activos = Curso.query.filter_by(activo=True).all()
    return render_template('index.html', title='Inicio', cursos=cursos_activos)

#                   DETALLES DEL CURSO
@main_bp.route('/cursos/<slug>')
def curso_detalle(slug):
<<<<<<< HEAD
    # Busca el curso por su slug en la base de datos
    curso = Curso.query.filter_by(slug=slug).first_or_404() # Si no se encuentra, Flask manejará un 404
    
    # El botón de solicitar beca solo aparecerá si el curso está activo
    return render_template('curso_detalle.html', title=curso.nombre, curso=curso)


#                   FORMULARIO DE SOLICITUD DE ADMISIÓN (USUARIO/ADMIN)
#                   FORMULARIO DE SOLICITUD DE ADMISIÓN (USUARIO/ADMIN)
=======
    cursos = {
        'programadores-junior': {
            'nombre': 'PROGRAMADORES JUNIOR',
            'descripcion': 'Impulsa tu futuro. Aprender a Programar con una beca 100% gratuita y adquiere nuevas habilidades digitales',
            
            # Agregué esto ya que el código estaba hardokeado, entonces los requisitos que se editaban aparecían en ambos apartados
            'requisitos': [
                'Tener entre 18 a 35 años',
                'Graduado a Nivel Medio',
                'Disponibilidad de estudiar de Lunes a Viernes'
            ],
            'imagen': 'python.png',
            'slug': 'programacion-python'

        },
        'ciberseguridad': {
            'nombre': 'PROGRAMA DE CERTIFICACIÓN EN CIBERSEGURIDAD',
            'descripcion': 'Conoce todo lo que aprenderás en el programa de certificación en ciberseguridad de IRSI',
            
            # Agregué requitos al igual que arriba
            'requisitos': [
                'Estar cursandp 4to de ingeniería en Sistemas o carrera afín, o ser graduado universitario'
                
                'Excelencia Académica',
                'Disponibilidad de tiempo lunes a viernes 4 horas de clase en línea sincrónica (no se graba), ya sea en horario matutino (7:00 am a 11:00 am), o vespertino (6:00 pm a 10:00pm) hora Guatemala  (GMT-6), durante 9 meses continuos, cada grupo con sus respectivos espacios de descanso.',
                'Autodidacta y ser disciplinado(a).',
                'Inglés técnico intermedio B1 (deseable).',
                'Contar con acceso a internet y computadora.',
                'No tener experiencia en el área de ciberseguridad.',
                'Realizar todos los pasos del proceso de admisión de manera exitosa y en tiempo',
                'La capacidad de programar en varios lenguajes es útil para entender mejor los sistemas y aplicaciones que se deben proteger.',
                'Los conocimientos de redes son esenciales para entender cómo se conectan los sistemas y cómo se pueden proteger las redes contra posibles amenazas.',
                'Es importante tener un conocimiento sólido de sistemas operativos como Windows y Linux para identificar vulnerabilidades en los sistemas y aplicaciones.'
            ],
            'imagen': 'flask.png',
            'slug': 'desarrollo-web-flask'
        }
    }
    curso = cursos.get(slug)
    if not curso:
        flash('El curso solicitado no existe.', 'danger')
        return redirect(url_for('main.index'))
    return render_template(
        'curso_detalle.html',
        title=curso['nombre'],
        curso=curso,
        curso_slug=curso['slug']  # <--- Esta línea es clave
    )



>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db
@main_bp.route('/solicitar_admision', methods=['GET', 'POST'])
@main_bp.route('/solicitar_admision/<string:curso_slug_param>', methods=['GET', 'POST'])
@login_required
@role_required(['user', 'admin'])
def solicitar_admision(curso_slug_param=None):
    estudiante_a_modificar = None
    
    # 1. Determinar el estudiante a modificar/crear
    estudiante_id_param = request.args.get('estudiante_id', type=int)
    
    if current_user.role == 'admin' and estudiante_id_param:
        estudiante_a_modificar = Estudiante.query.get(estudiante_id_param)
        if not estudiante_a_modificar:
            flash('Estudiante no encontrado.', 'danger')
            return redirect(url_for('admin.student_list'))
    else:
        estudiante_a_modificar = current_user.estudiante

    form = EstudianteForm(obj=estudiante_a_modificar)

    # 2. Manejar el campo 'correo' (pre-llenado y solo lectura si aplica)
    if request.method == 'GET':
        if estudiante_a_modificar:
            if estudiante_a_modificar.user:
                form.correo.data = estudiante_a_modificar.user.username 
            
            if current_user.role == 'admin' and estudiante_id_param and \
               estudiante_a_modificar.user_id != current_user.id:
                 form.correo.render_kw = {'readonly': True}
        else:
            form.correo.data = current_user.username
    
    # 3. Poblar dinámicamente las opciones de ciudad
    if form.pais.data:
        form.ciudad.choices = [(c, c) for c in LATAM_PAISES_CIUDADES.get(form.pais.data, [])]
    else:
        form.ciudad.choices = [('', 'Selecciona primero un país')]
        
    # 4. Poblar dinámicamente las opciones de cursos y manejar la pre-selección
    cursos_activos = Curso.query.filter_by(activo=True).all()
    # Las opciones del SelectField deben ser tuplas (valor, etiqueta)
    form.curso_a_inscribir.choices = [('', 'Selecciona un curso (opcional)')] + \
                                      [(c.slug, c.nombre) for c in cursos_activos]

    # Pre-seleccionar el curso si viene en la URL o si ya hay una inscripción previa para un curso específico
    if request.method == 'GET':
        if curso_slug_param: # Si el slug viene en la URL
            # Asegúrate de que el slug exista en las opciones del formulario
            if curso_slug_param in [c[0] for c in form.curso_a_inscribir.choices]:
                form.curso_a_inscribir.data = curso_slug_param
            else:
                flash('El curso especificado en la URL no está disponible.', 'warning')
        elif estudiante_a_modificar:
            # Si el estudiante ya tiene una inscripción a un curso, pre-seleccionar ese curso
            # Esto es más complejo si un estudiante puede tener múltiples inscripciones.
            # Por simplicidad, si ya tiene una inscripción, no pre-seleccionamos para evitar confusiones.
            # La idea de este formulario es para CREAR nuevas solicitudes O ACTUALIZAR DATOS.
            # Si es solo para actualizar datos, el campo curso_a_inscribir debería ser opcionalmente vacío.
            pass # No pre-seleccionar nada si no hay slug en URL para evitar sobrescribir intención.

    # Determinar el label del DNI
    dni_label = NOMBRE_DOCUMENTO_POR_PAIS.get(form.pais.data or '', 'Documento de Identificación')

    if form.validate_on_submit():
        print(f"DEBUG: Formulario validado. Datos recibidos: {form.data}")
        
        # Validación del campo 'correo'
        if current_user.role == 'admin' and estudiante_id_param and \
           estudiante_a_modificar and estudiante_a_modificar.user_id != current_user.id:
            if estudiante_a_modificar.user:
                expected_correo = estudiante_a_modificar.user.username
                if form.correo.data != expected_correo:
                    flash(f'Error: No se puede cambiar el correo de un estudiante asociado a otra cuenta ({expected_correo}).', 'danger')
                    form.correo.data = expected_correo
                    return render_template(
                        'add_student.html',
                        title='Solicitar Admisión',
                        form=form,
                        LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                        NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                        dni_label=dni_label,
                        cursos=cursos_activos, # Pasa los cursos activos al template
                        selected_curso_slug=form.curso_a_inscribir.data # Pasa el curso seleccionado del formulario
                    )
        elif not estudiante_a_modificar or (estudiante_a_modificar and estudiante_a_modificar.user_id == current_user.id):
            if form.correo.data != current_user.username:
                flash('Error: El correo debe ser tu nombre de usuario de inicio de sesión.', 'danger')
                return render_template(
                    'add_student.html',
                    title='Solicitar Admisión',
                    form=form,
                    LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                    NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                    dni_label=dni_label,
                    cursos=cursos_activos, # Pasa los cursos activos al template
                    selected_curso_slug=form.curso_a_inscribir.data # Pasa el curso seleccionado del formulario
                )

        # Crear o actualizar el estudiante
        if estudiante_a_modificar:
            form.populate_obj(estudiante_a_modificar)
            if estudiante_a_modificar.user_id:
                estudiante_a_modificar.correo = User.query.get(estudiante_a_modificar.user_id).username
            flash('Datos del estudiante actualizados exitosamente.', 'success') # Mensaje más específico
        else:
            estudiante_a_modificar = Estudiante(user_id=current_user.id)
            form.populate_obj(estudiante_a_modificar)
            estudiante_a_modificar.correo = current_user.username
            db.session.add(estudiante_a_modificar)
            flash('Perfil de estudiante creado exitosamente.', 'success') # Mensaje más específico
        
        db.session.commit() # Guarda el estudiante para asegurar que tiene un ID si es nuevo

        # Lógica para la inscripción al curso (AHORA CONDICIONAL)
        curso_slug_seleccionado_form = form.curso_a_inscribir.data
        if curso_slug_seleccionado_form: # Solo procede si se ha seleccionado un curso en el formulario
            curso_a_inscribir = Curso.query.filter_by(slug=curso_slug_seleccionado_form, activo=True).first()
            if not curso_a_inscribir:
                flash('El curso seleccionado no es válido o no está activo. Por favor, revisa tu selección.', 'warning')
                # Renderiza el formulario de nuevo para que el usuario corrija
                return render_template(
                    'add_student.html',
                    title='Solicitar Admisión',
                    form=form,
                    LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                    NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                    dni_label=dni_label,
                    cursos=cursos_activos,
                    selected_curso_slug=form.curso_a_inscribir.data
                )

            # Verificar si ya existe una inscripción para este estudiante y este curso
            inscripcion_existente = Inscripcion.query.filter_by(
                estudiante_id=estudiante_a_modificar.id,
                curso_slug=curso_a_inscribir.slug
            ).first()

            if not inscripcion_existente:
                nueva_inscripcion = Inscripcion(
                    estudiante_id=estudiante_a_modificar.id,
                    curso_slug=curso_a_inscribir.slug,
                    estado='pendiente'
                )
                db.session.add(nueva_inscripcion)
                flash(f'Solicitud de inscripción para "{curso_a_inscribir.nombre}" enviada exitosamente.', 'success')
            else:
                flash(f'Ya tienes una inscripción pendiente para el curso "{curso_a_inscribir.nombre}".', 'info')
            
            db.session.commit() # Guarda la nueva inscripción

        # Redirección final. Decide si redirigir a 'mis_solicitudes' o a 'admin.student_list'
        # Esto depende de si el admin quiere seguir editando, o volver a la lista.
        # Por ahora, volvamos a la lista si un admin estaba editando a otro estudiante.
        if current_user.role == 'admin' and estudiante_id_param:
            return redirect(url_for('admin.student_list')) # O a student_detail si existe
        else:
            return redirect(url_for('main.mis_solicitudes'))

    # Si GET request o form validation failed
    return render_template(
        'add_student.html',
        title='Solicitar Admisión',
        form=form,
        LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
        NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
        dni_label=dni_label,
        cursos=cursos_activos, # Pasa los cursos activos al template
        selected_curso_slug=form.curso_a_inscribir.data # Pasa el curso seleccionado por URL o data
    )

@main_bp.route('/mis_solicitudes')
@login_required
@role_required(['user'])
def mis_solicitudes():
    estudiante = current_user.estudiante
    inscripciones = []
    if estudiante:
        # Ahora, inscripcion.curso_obj estará disponible debido a la relación en models.py
        inscripciones = Inscripcion.query.filter_by(estudiante_id=estudiante.id)\
                                     .order_by(Inscripcion.fecha_inscripcion.desc()).all()
    else:
        flash('Necesitas completar tu perfil de estudiante primero.', 'info')
        return redirect(url_for('main.solicitar_admision'))

    return render_template('mis_solicitudes.html',
                           estudiante=estudiante,
                           inscripciones=inscripciones)