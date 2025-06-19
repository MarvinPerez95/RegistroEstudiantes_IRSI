from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..models import Estudiante, Inscripcion, Curso, User
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
    cursos_activos = Curso.query.filter_by(activo=True).all()
    return render_template('index.html', title='Inicio', cursos=cursos_activos)

#                   DETALLES DEL CURSO
@main_bp.route('/cursos/<slug>')
def curso_detalle(slug):
    # Busca el curso por su slug en la base de datos
    curso = Curso.query.filter_by(slug=slug).first_or_404()  # Si no se encuentra, Flask manejará un 404
    
    # El botón de solicitar beca solo aparecerá si el curso está activo
    return render_template('curso_detalle.html', title=curso.nombre, curso=curso)


@main_bp.route('/solicitar_admision', methods=['GET', 'POST'])
@main_bp.route('/solicitar_admision/<string:curso_slug_param>', methods=['GET', 'POST'])
@login_required
@role_required(['user', 'admin'])
def solicitar_admision(curso_slug_param=None):
    estudiante_a_modificar = None
    estudiante_id_param = request.args.get('estudiante_id', type=int)
    
    if current_user.role == 'admin' and estudiante_id_param:
        estudiante_a_modificar = Estudiante.query.get(estudiante_id_param)
        if not estudiante_a_modificar:
            flash('Estudiante no encontrado.', 'danger')
            return redirect(url_for('admin.student_list'))
    else:
        estudiante_a_modificar = current_user.estudiante

    form = EstudianteForm(obj=estudiante_a_modificar)

    if request.method == 'GET':
        if estudiante_a_modificar:
            if estudiante_a_modificar.user:
                form.correo.data = estudiante_a_modificar.user.username 
            
            if current_user.role == 'admin' and estudiante_id_param and \
               estudiante_a_modificar.user_id != current_user.id:
                 form.correo.render_kw = {'readonly': True}
        else:
            form.correo.data = current_user.username
    
    if form.pais.data:
        form.ciudad.choices = [(c, c) for c in LATAM_PAISES_CIUDADES.get(form.pais.data, [])]
    else:
        form.ciudad.choices = [('', 'Selecciona primero un país')]
        
    cursos_activos = Curso.query.filter_by(activo=True).all()
    form.curso_a_inscribir.choices = [('', 'Selecciona un curso (opcional)')] + \
                                      [(c.slug, c.nombre) for c in cursos_activos]

    if request.method == 'GET':
        if curso_slug_param:
            if curso_slug_param in [c[0] for c in form.curso_a_inscribir.choices]:
                form.curso_a_inscribir.data = curso_slug_param
            else:
                flash('El curso especificado en la URL no está disponible.', 'warning')

    dni_label = NOMBRE_DOCUMENTO_POR_PAIS.get(form.pais.data or '', 'Documento de Identificación')

    if form.validate_on_submit():
        print(f"DEBUG: Formulario validado. Datos recibidos: {form.data}")
        
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
                        cursos=cursos_activos,
                        selected_curso_slug=form.curso_a_inscribir.data
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
                    cursos=cursos_activos,
                    selected_curso_slug=form.curso_a_inscribir.data
                )

        if estudiante_a_modificar:
            form.populate_obj(estudiante_a_modificar)
            if estudiante_a_modificar.user_id:
                estudiante_a_modificar.correo = User.query.get(estudiante_a_modificar.user_id).username
            flash('Datos del estudiante actualizados exitosamente.', 'success')
        else:
            estudiante_a_modificar = Estudiante(user_id=current_user.id)
            form.populate_obj(estudiante_a_modificar)
            estudiante_a_modificar.correo = current_user.username
            db.session.add(estudiante_a_modificar)
            flash('Perfil de estudiante creado exitosamente.', 'success')
        
        db.session.commit()

        curso_slug_seleccionado_form = form.curso_a_inscribir.data
        if curso_slug_seleccionado_form:
            curso_a_inscribir = Curso.query.filter_by(slug=curso_slug_seleccionado_form, activo=True).first()
            if not curso_a_inscribir:
                flash('El curso seleccionado no es válido o no está activo. Por favor, revisa tu selección.', 'warning')
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
            
            db.session.commit()

        if current_user.role == 'admin' and estudiante_id_param:
            return redirect(url_for('admin.student_list'))
        else:
            return redirect(url_for('main.mis_solicitudes'))

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


@main_bp.route('/mis_solicitudes')
@login_required
@role_required(['user'])
def mis_solicitudes():
    estudiante = current_user.estudiante
    inscripciones = []
    if estudiante:
        inscripciones = Inscripcion.query.filter_by(estudiante_id=estudiante.id)\
                                     .order_by(Inscripcion.fecha_inscripcion.desc()).all()
    else:
        flash('Necesitas completar tu perfil de estudiante primero.', 'info')
        return redirect(url_for('main.solicitar_admision'))

    return render_template('mis_solicitudes.html',
                           estudiante=estudiante,
                           inscripciones=inscripciones)
