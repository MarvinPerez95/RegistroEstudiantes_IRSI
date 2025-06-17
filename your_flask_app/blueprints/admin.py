# your_flask_app/blueprints/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..decorators import role_required # Importa tu decorador
from ..models import Estudiante, Inscripcion # Importa los modelos necesarios
from ..forms import EstudianteForm, InscripcionApprovalForm # Importa los formularios si es necesario
from ..extensions import db # Necesario para interactuar con la base de datos
import bleach # Para limpiar la entrada del usuario

# Crea una instancia de Blueprint. Usamos 'admin' como nombre.
admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin', url_prefix='/admin') # Puedes definir el prefijo aquí o en app.py

# Ruta para el panel de administrador
@admin_bp.route('/') # Esta ruta se accederá como /admin/
@admin_bp.route('/dashboard') # Esta ruta se accederá como /admin/dashboard
@login_required
@role_required(['admin'])
def dashboard():
    # Puedes añadir datos relevantes para el dashboard aquí, como estadísticas, etc.
    total_estudiantes = Estudiante.query.count()
    inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()
    return render_template('dashboard.html', title='Panel de Administrador', 
                           total_estudiantes=total_estudiantes, 
                           inscripciones_pendientes=inscripciones_pendientes)

# Ruta para listar estudiantes
@admin_bp.route('/students')
@login_required
@role_required(['admin']) # Solo administradores
def student_list():
    students = Estudiante.query.all()
    return render_template('student_list.html', title='Lista de Estudiantes', students=students)

# Ruta para eliminar estudiante (solo admin)
@admin_bp.route('/delete_student/<int:id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_student(id):
    student = Estudiante.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Estudiante eliminado exitosamente.', 'success')
        # current_app.logger.info(f'Estudiante eliminado: {student.nombre} {student.apellidos}')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estudiante: {e}', 'danger')
        # current_app.logger.error(f'Error al eliminar estudiante: {e}')
    return redirect(url_for('admin.student_list')) # Redirige a la lista de estudiantes del blueprint 'admin'

# Ruta para gestionar inscripciones (aprobar/rechazar)
@admin_bp.route('/manage_inscripciones')
@login_required
@role_required(['admin'])
def manage_inscripciones():
    # Obtener todas las inscripciones o filtrarlas
    inscripciones = Inscripcion.query.all()
    return render_template('manage_inscripcion.html', title='Gestión de Inscripciones', inscripciones=inscripciones)

# Ruta para cambiar el estado de una inscripción
@admin_bp.route('/inscripcion/<int:inscripcion_id>/update_status', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def update_inscripcion_status(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    form = InscripcionApprovalForm(obj=inscripcion) # Pre-rellena el formulario con el estado actual

    if form.validate_on_submit():
        inscripcion.estado = form.estado.data
        inscripcion.razon_rechazo = bleach.clean(form.razon_rechazo.data) if form.razon_rechazo.data else None
        
        try:
            db.session.commit()
            flash(f'Estado de inscripción {inscripcion.id} actualizado a {inscripcion.estado}.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la inscripción: {e}', 'danger')
            # current_app.logger.error(f'Error al actualizar inscripción {inscripcion.id}: {e}')
        return redirect(url_for('admin.manage_inscripciones'))

    return render_template('admin/update_inscripcion_status.html', title='Actualizar Inscripción', form=form, inscripcion=inscripcion) # Necesitarás crear esta plantilla