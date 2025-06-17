# routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app # Importa current_app para acceder a app.logger
from flask_login import login_required, current_user # Importa current_user para el correo
from .forms import EstudianteForm
from .data import LATAM_PAISES_CIUDADES, NOMBRE_DOCUMENTO_POR_PAIS
from .models import db, Estudiante, Inscripcion # Asegúrate de que tu modelo Estudiante esté importado
from .extensions import db # Asegúrate de que db esté importado
from datetime import datetime # <--- ¡Añade esta línea!
import bleach # Para sanear datos
from .decorators import role_required # <-- ¡Añade esta línea para importar tu decorador!
from flask_login import login_required # Asegúrate de que esta también esté
from flask import render_template, current_app, flash, redirect, url_for # Añade redirect y url_for
from flask_login import login_required, current_user
# Asumiendo que Estudiante e Inscripcion están importados de tu models.py
from your_flask_app.models import Estudiante, Inscripcion 
from . import main_bp 

# Crea un Blueprint
main_bp = Blueprint('main', __name__) # 'main' es el nombre del Blueprint



@main_bp.route('/cursos/<string:curso_slug>', methods=['GET'])
def curso_detalle(curso_slug):
    # Aquí es donde simularías obtener la información del curso de una base de datos
    # o de un diccionario predefinido.
    
    # Definimos los detalles de los cursos (puedes mover esto a un archivo de datos si crece mucho)
    cursos_info = {
        'programadores-jr': {
            'titulo': 'Programa de Programadores Jr.',
            'descripcion': 'Este programa intensivo te sumerge en el mundo del desarrollo de software, cubriendo lenguajes como Python y JavaScript, bases de datos y control de versiones. Es ideal para principiantes con ganas de construir una carrera en tecnología.',
            'requisitos': [
                'No se requiere experiencia previa en programación.',
                'Habilidades básicas de lógica y resolución de problemas.',
                'Disponibilidad de 20 horas semanales para estudio y práctica.',
                'Conexión a internet estable y equipo informático adecuado.'
            ],
            'url_formulario': url_for('main.manage_estudiante_add') # Enlace al formulario de estudiante
        },
        'ciberseguridad': {
            'titulo': 'Curso de Ciberseguridad',
            'descripcion': 'Aprende a proteger sistemas y redes de ataques cibernéticos. Cubriremos temas como seguridad de redes, criptografía, análisis de vulnerabilidades y respuesta a incidentes. Fundamental para quienes buscan asegurar la información en el entorno digital.',
            'requisitos': [
                'Conocimientos básicos de redes y sistemas operativos.',
                'Interés en la seguridad informática y la protección de datos.',
                'Disponibilidad de 15 horas semanales para estudio.',
                'Capacidad de análisis y atención al detalle.'
            ],
            'url_formulario': url_for('main.manage_estudiante_add') # Enlace al formulario de estudiante
        }
    }

    curso = cursos_info.get(curso_slug)

    if not curso:
        # Si el slug no coincide con ningún curso, puedes redirigir o mostrar un 404
        flash('El curso solicitado no se encontró.', 'danger')
        return redirect(url_for('main.index')) # O abort(404)

    return render_template('curso_detalle.html', curso=curso, curso_slug=curso_slug)










# --- FUNCIÓN MANAGE_ESTUDIANTE ACTUALIZADA ---
@main_bp.route('/estudiantes/nuevo', methods=['GET', 'POST'], endpoint='manage_estudiante_add')
@main_bp.route('/estudiantes/editar/<int:estudiante_id>', methods=['GET', 'POST'], endpoint='manage_estudiante_edit') # <-- ¡MANTENEMOS ESTA LÍNEA!
@login_required 
@role_required(['admin', 'user']) 
def manage_estudiante(estudiante_id=None): # <-- ¡MANTENEMOS estudiante_id=None aquí!
    estudiante = None
    curso_slug = None # Inicializa curso_slug a None

    # Lógica para manejar si es una edición (estudiante_id presente) o una creación (estudiante_id es None)
    if estudiante_id:
        estudiante = Estudiante.query.get_or_404(estudiante_id)
        form = EstudianteForm(obj=estudiante)
        title_text = "Editar Estudiante"
        # Si el usuario actual no es admin y no es el dueño del estudiante, no debería editar
        if current_user.role != 'admin' and estudiante.user_id != current_user.id:
            flash('No tienes permiso para editar este perfil de estudiante.', 'danger')
            return redirect(url_for('main.mis_solicitudes')) # O a donde sea apropiado

    else: # Esto es para AÑADIR nuevo estudiante
        form = EstudianteForm()
        if request.method == 'GET' and not form.correo.data:
         form.correo.data = current_user.username
        title_text = "Solicitar Beca - Nuevo Estudiante"
        
        # --- NUEVA LÓGICA DE VALIDACIÓN PARA USUARIO-ESTUDIANTE ---
        # Si el usuario es 'user' y ya tiene un perfil de estudiante, redirigirlo.
        if current_user.role == 'user':
            estudiante_existente_para_usuario = Estudiante.query.filter_by(user_id=current_user.id).first()
            if estudiante_existente_para_usuario:
                flash('Ya tienes un perfil de estudiante asociado a tu cuenta. Puedes ver el estado de tu solicitud aquí.', 'info')
                return redirect(url_for('main.mis_solicitudes'))
        # ---------------------------------------------------------

        if current_user.is_authenticated and not form.correo.data:
            form.correo.data = current_user.username
        
        # OBTENER el curso_slug de la URL para el modo 'añadir'
        curso_slug = request.args.get('curso_slug') 

    # Lógica para cargar opciones de ciudad (antes de validate_on_submit)
    selected_pais = None
    if request.method == 'POST':
        selected_pais = request.form.get('pais')
    elif estudiante and estudiante.pais:
        selected_pais = estudiante.pais
    elif form.pais.data: # Esto es para el GET inicial o si ya había datos en el formulario
        selected_pais = form.pais.data
        
    if selected_pais and selected_pais in LATAM_PAISES_CIUDADES:
        form.ciudad.choices = [(ciudad, ciudad) for ciudad in LATAM_PAISES_CIUDADES[selected_pais]]
    else:
        form.ciudad.choices = [('', 'Seleccione un país primero')]

    initial_dni_label = "Documento de Identificación" 
    if form.pais.data and form.pais.data in NOMBRE_DOCUMENTO_POR_PAIS:
        initial_dni_label = NOMBRE_DOCUMENTO_POR_PAIS[form.pais.data]

    # --- LÓGICA PRINCIPAL DEL FORMULARIO ---
    if form.validate_on_submit():
        try:
            # Saneamiento de datos (mantener como lo tienes)
            nombre = bleach.clean(form.nombre.data)
            apellidos = bleach.clean(form.apellidos.data)
            pais = bleach.clean(form.pais.data)
            ciudad = bleach.clean(form.ciudad.data)
            direccion = bleach.clean(form.direccion.data)
            grado = bleach.clean(form.grado.data)
            dni = bleach.clean(form.dni.data)
            correo = bleach.clean(form.correo.data)
            telefono = bleach.clean(form.telefono.data)
            sexo = bleach.clean(form.sexo.data)
            motivo = bleach.clean(form.motivo.data)
            veracidad = form.veracidad.data


            # Validar si el DNI ya existe para CUALQUIER otro estudiante (no el que se está editando, si aplica)
            existing_dni_estudiante = Estudiante.query.filter_by(dni=dni).first()
            if existing_dni_estudiante and (not estudiante_id or existing_dni_estudiante.id != estudiante_id):
                flash('Ya existe una solicitud con este DNI. Cada persona solo puede hacer una solicitud.', 'danger')
                return render_template('add_student.html',
                                       title=title_text, form=form,
                                       LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                                       NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                                       dni_label=initial_dni_label,
                                       curso_slug=curso_slug 
                                       )
            
            if estudiante_id:
                # Actualizar estudiante existente
                form.populate_obj(estudiante)
                message = 'Estudiante actualizado exitosamente.'
                log_message = f'Estudiante actualizado: {estudiante.nombre} {estudiante.apellidos} (ID: {estudiante_id})'
                # Si se está editando, no se crea una nueva inscripción.
                # Se podría añadir lógica aquí si, por ejemplo, el admin quiere crear una nueva inscripción para un estudiante existente.
            else:
                # Añadir nuevo estudiante (si no se redirigió antes)
                estudiante = Estudiante(
                    nombre=nombre,
                    apellidos=apellidos,
                    pais=pais,
                    ciudad=ciudad,
                    direccion=direccion,
                    grado=grado,
                    dni=dni,
                    fecha_nacimiento=form.fecha_nacimiento.data,
                    correo=correo,
                    telefono=telefono,
                    anio_solicitud=form.anio_solicitud.data,
                    sexo=sexo,
                    motivo=motivo,
                    veracidad=veracidad,
                    user_id=current_user.id
                )
                db.session.add(estudiante)

                # Crear la Inscripción DESPUÉS de añadir el estudiante
                if curso_slug: 
                    inscripcion = Inscripcion(
                        estudiante=estudiante, 
                        curso_slug=curso_slug,
                        fecha_inscripcion=datetime.utcnow(),
                        estado='pendiente',
                        razon_rechazo=None 
                    )
                    db.session.add(inscripcion) 
                    current_app.logger.info(f'Nueva inscripción para {estudiante.correo} al curso {curso_slug}.')
                else:
                    flash('No se especificó el curso para la solicitud. Por favor, selecciona un curso desde la página principal.', 'danger')
                    current_app.logger.warning(f'Intento de añadir estudiante sin curso_slug especificado para inscripción: {estudiante.correo}')
                    db.session.rollback() 
                    return render_template('add_student.html',
                                           title=title_text, form=form,
                                           LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                                           NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                                           dni_label=initial_dni_label,
                                           curso_slug=curso_slug
                                           )
                
                message = 'Estudiante y solicitud de beca procesados exitosamente.'
                log_message = f'Estudiante añadido: {estudiante.nombre} {estudiante.apellidos}'
            
            db.session.commit() 
            
            flash(message, 'success_redirect') 
            current_app.logger.info(log_message)
            
            # Redirección basada en si es adición o edición y el rol del usuario
            if estudiante_id: # Si fue una edición
                if current_user.role == 'admin':
                    return redirect(url_for('main.lista_estudiantes')) # O a la vista de gestión de admins
                else: # Si un usuario edita su propio perfil
                    return redirect(url_for('main.mis_solicitudes'))
            else: # Si fue una adición
                return redirect(url_for('main.mis_solicitudes')) # Siempre redirige a ver el estado de la solicitud
                

        except Exception as e:
            db.session.rollback() 
            flash(f'Error al procesar tu solicitud: {e}', 'danger') 
            current_app.logger.error(f'Error al procesar solicitud: {e}', exc_info=True)
    
    return render_template('add_student.html',
                           title=title_text,
                           form=form, 
                           LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES, 
                           NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS, 
                           dni_label=initial_dni_label,
                           curso_slug=curso_slug 
                           )



main_bp.route('/mis_solicitudes', methods=['GET'])
@login_required 
@role_required(['user', 'admin']) # ¡Comenta esta línea!
def mis_solicitudes():
    print("DEBUG: Entrando a la función mis_solicitudes.")
    print(f"DEBUG: current_user ID: {current_user.id}")
    print(f"DEBUG: current_user es_authenticated: {current_user.is_authenticated}")

    try:
        estudiante = Estudiante.query.filter_by(user_id=current_user.id).first()
        print(f"DEBUG: Estudiante encontrado: {estudiante is not None}")
        if estudiante:
            print(f"DEBUG: ID del estudiante: {estudiante.id}")

        inscripciones = [] 
        if estudiante: # Si el usuario tiene un perfil de estudiante asociado
            inscripciones = Inscripcion.query.filter_by(estudiante_id=estudiante.id).order_by(Inscripcion.fecha_inscripcion.desc()).all()
            print(f"DEBUG: Número de inscripciones encontradas: {len(inscripciones)}")
        else:
            print("DEBUG: No se encontró un perfil de estudiante para el usuario actual.")
            flash('Necesitas completar tu perfil de estudiante primero.', 'info')
            return redirect(url_for('main.solicitar_admision')) # Asegúrate de que esta URL exista

        cursos_info = {
            'programadores-jr': {'titulo': 'Programa de Programadores Jr.'},
            'ciberseguridad': {'titulo': 'Curso de Ciberseguridad'}
        }
        print("DEBUG: Preparando para renderizar el template.")
        return render_template('mis_solicitudes.html', 
                               estudiante=estudiante, 
                               inscripciones=inscripciones, 
                               cursos_info=cursos_info)
    except Exception as e:
        print(f"ERROR: Se produjo una excepción en mis_solicitudes: {e}")
        flash(f'Ocurrió un error al cargar tus solicitudes: {e}', 'danger')
        # Es crucial que esta rama también devuelva una respuesta válida
        return redirect(url_for('main.index')) # Redirige al index o a una página de error genérica