# your_flask_app/blueprints/main.py

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import Estudiante, Inscripcion
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
    return render_template('index.html', title='Inicio')

@main_bp.route('/cursos/<slug>')
def curso_detalle(slug):
    cursos = {
        'programacion-python': {
            'nombre': 'Programación con Python para Principiantes',
            'descripcion': 'Aprende los fundamentos de Python.',
            'imagen': 'python.png',
            'slug': 'programacion-python'
        },
        'desarrollo-web-flask': {
            'nombre': 'Desarrollo Web con Flask',
            'descripcion': 'Construye aplicaciones web robustas con Flask.',
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

@main_bp.route('/solicitar_admision', methods=['GET', 'POST'])
@login_required
@role_required(['user', 'admin'])
def solicitar_admision():
    curso_slug = request.args.get('curso_slug')
    if not curso_slug:
        flash('Debes seleccionar un curso para solicitar admisión.', 'danger')
        return redirect(url_for('main.index'))

    estudiante = current_user.estudiante
    inscripcion_existente = None

    # Buscar inscripción existente a ese curso (si hay estudiante)
    if estudiante:
        inscripcion_existente = Inscripcion.query.filter_by(estudiante_id=estudiante.id, curso_slug=curso_slug).first()
        if inscripcion_existente:
            flash('Ya tienes una solicitud para este curso. Puedes editar tus datos.', 'info')

    form = EstudianteForm(obj=estudiante)
    if request.method == 'GET' and not form.correo.data:
        form.correo.data = current_user.username

    form.ciudad.choices = [(c, c) for c in LATAM_PAISES_CIUDADES.get(form.pais.data, [])]
    dni_label = NOMBRE_DOCUMENTO_POR_PAIS.get(form.pais.data, "Documento de Identificación")

    if form.validate_on_submit():
        # Actualizar datos del estudiante (si existe) o crear nuevo
        if estudiante:
            form.populate_obj(estudiante)
        else:
            estudiante = Estudiante(
                nombre=bleach.clean(form.nombre.data),
                apellidos=bleach.clean(form.apellidos.data),
                pais=bleach.clean(form.pais.data),
                ciudad=bleach.clean(form.ciudad.data),
                direccion=bleach.clean(form.direccion.data),
                grado=bleach.clean(form.grado.data),
                dni=bleach.clean(form.dni.data),
                fecha_nacimiento=form.fecha_nacimiento.data,
                correo=bleach.clean(form.correo.data),
                telefono=bleach.clean(form.telefono.data),
                anio_solicitud=form.anio_solicitud.data,
                user_id=current_user.id if current_user.role == 'user' else None,
                sexo=bleach.clean(form.sexo.data),
                motivo=bleach.clean(form.motivo.data),
                veracidad=form.veracidad.data
            )
            db.session.add(estudiante)
            db.session.flush()  # para obtener id

        # Validar duplicados por DNI/correo al crear
        if not inscripcion_existente:
            existing_dni = Estudiante.query.filter(Estudiante.dni == bleach.clean(form.dni.data), Estudiante.id != estudiante.id).first()
            if existing_dni:
                flash('Ya existe un estudiante con ese DNI.', 'danger')
                return render_template(
                    'add_student.html',
                    title='Solicitar Admisión',
                    form=form,
                    LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                    NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                    dni_label=dni_label
                )

            existing_correo = Estudiante.query.filter(Estudiante.correo == bleach.clean(form.correo.data), Estudiante.id != estudiante.id).first()
            if existing_correo:
                flash('Ya existe un estudiante con ese correo electrónico.', 'danger')
                return render_template(
                    'add_student.html',
                    title='Solicitar Admisión',
                    form=form,
                    LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
                    NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
                    dni_label=dni_label
                )

        # Solo crear inscripción nueva si no existe para ese curso
        if not inscripcion_existente:
            nueva_inscripcion = Inscripcion(
                estudiante_id=estudiante.id,
                curso_slug=curso_slug,
                estado='pendiente'
            )
            db.session.add(nueva_inscripcion)
            flash('Solicitud de admisión enviada exitosamente.', 'success')
        else:
            flash('Datos actualizados. Ya tienes una inscripción para este curso.', 'info')

        db.session.commit()
        return redirect(url_for('main.mis_solicitudes'))

    return render_template(
        'add_student.html',
        title='Solicitar Admisión',
        form=form,
        LATAM_PAISES_CIUDADES=LATAM_PAISES_CIUDADES,
        NOMBRE_DOCUMENTO_POR_PAIS=NOMBRE_DOCUMENTO_POR_PAIS,
        dni_label=dni_label
    )


@main_bp.route('/mis_solicitudes')
@login_required
@role_required(['user'])
def mis_solicitudes():
    estudiante = current_user.estudiante
    inscripciones = []
    if estudiante:
        inscripciones = Inscripcion.query.filter_by(estudiante_id=estudiante.id).order_by(Inscripcion.fecha_inscripcion.desc()).all()
    return render_template('mis_solicitudes.html', estudiante=estudiante, inscripciones=inscripciones)