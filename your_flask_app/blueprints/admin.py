# your_flask_app/blueprints/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..decorators import role_required # Importa tu decorador
from ..models import Estudiante, Inscripcion # Importa los modelos necesarios
from ..forms import EstudianteForm, InscripcionApprovalForm # Importa los formularios si es necesario
from ..extensions import db # Necesario para interactuar con la base de datos
import bleach # Para limpiar la entrada del usuario
# Nuevas importaciones para excel
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask import send_file, make_response
from io import BytesIO
import pandas as pd
from datetime import datetime

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
    excel_form = UploadExcelForm()
    return render_template('student_list.html', 
                            title='Lista de Estudiantes',
                            students=students,              # Muestra la página student_list.html y le pasa la lista de estudiantes
                            excel_form=excel_form)

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
    return render_template('manage_inscripcion.html',
                            title='Gestión de Inscripciones',
                            inscripciones=inscripciones)

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

    return render_template('admin/update_inscripcion_status.html',
                            title='Actualizar Inscripción',
                            form=form, inscripcion=inscripcion) # Necesitarás crear esta plantilla



#                   NUEVA FUNCIÓN PARA PROCESAR ARCHIVO EXCEL (G)
@admin_bp.route('/upload_excel', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def upload_excel():
    print("DEBUG: Función upload_excel llamada")
    print(f"DEBUG: Método de request: {request.method}")
    
    form = UploadExcelForm()
    print(f"DEBUG: Formulario válido: {form.validate_on_submit()}")
    
    if form.validate_on_submit():
        try:
            # Obtener el archivo subido
            file = form.excel_file.data
            filename = secure_filename(file.filename)
            
            print(f"DEBUG: Archivo recibido: {filename}")
            
            # Crear directorio temporal si no existe
            upload_folder = 'temp_uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Guardar archivo temporalmente
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            print(f"DEBUG: Archivo guardado en: {file_path}")
            
            # Leer el archivo Excel con pandas
            try:
                df = pd.read_excel(file_path)
                print(f"DEBUG: Excel leído correctamente. Filas: {len(df)}")
            except Exception as e:
                flash(f'Error al leer el archivo Excel: {str(e)}', 'danger')
                os.remove(file_path)  # Limpiar archivo temporal
                return redirect(url_for('admin.student_list'))
            
            # Validar columnas requeridas
            required_columns = ['Nombre', 'Apellidos', 'DNI', 'Correo', 'Telefono', 
                                'Pais', 'Ciudad', 'Direccion', 'Grado', 'Fecha_Nacimiento', 
                                'Sexo', 'Motivo']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'Faltan las siguientes columnas en el Excel: {", ".join(missing_columns)}', 'danger')
                os.remove(file_path)
                return redirect(url_for('admin.student_list'))
            
            # Contadores para el reporte
            estudiantes_agregados = 0
            estudiantes_duplicados = 0
            errores = []
            
            # Procesar cada fila del Excel
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos
                    if pd.isna(row['Nombre']) or pd.isna(row['Apellidos']) or pd.isna(row['DNI']) or pd.isna(row['Correo']):
                        errores.append(f'Fila {index + 2}: Faltan datos obligatorios (Nombre, Apellidos, DNI, Correo)')
                        continue
                    
                    # Limpiar y preparar datos
                    dni = str(row['DNI']).strip()
                    correo = str(row['Correo']).strip().lower()
                    
                    # Verificar si ya existe un estudiante con este DNI o correo
                    existing_student = Estudiante.query.filter(
                        (Estudiante.dni == dni) | (Estudiante.correo == correo)
                    ).first()
                    
                    if existing_student:
                        estudiantes_duplicados += 1
                        continue
                    
                    # Procesar fecha de nacimiento
                    try:
                        if isinstance(row['Fecha_Nacimiento'], str):
                            fecha_nacimiento = datetime.strptime(row['Fecha_Nacimiento'], '%Y-%m-%d').date()
                        else:
                            fecha_nacimiento = row['Fecha_Nacimiento'].date()
                    except:
                        errores.append(f'Fila {index + 2}: Formato de fecha inválido. Use YYYY-MM-DD')
                        continue
                    
                    # Crear nuevo estudiante
                    nuevo_estudiante = Estudiante(
                        nombre=bleach.clean(str(row['Nombre']).strip()),
                        apellidos=bleach.clean(str(row['Apellidos']).strip()),
                        dni=bleach.clean(dni),
                        correo=bleach.clean(correo),
                        telefono=bleach.clean(str(row['Telefono']).strip()) if not pd.isna(row['Telefono']) else '',
                        pais=bleach.clean(str(row['Pais']).strip()) if not pd.isna(row['Pais']) else '',
                        ciudad=bleach.clean(str(row['Ciudad']).strip()) if not pd.isna(row['Ciudad']) else '',
                        direccion=bleach.clean(str(row['Direccion']).strip()) if not pd.isna(row['Direccion']) else '',
                        grado=bleach.clean(str(row['Grado']).strip()) if not pd.isna(row['Grado']) else '',
                        fecha_nacimiento=fecha_nacimiento,
                        sexo=bleach.clean(str(row['Sexo']).strip()) if not pd.isna(row['Sexo']) else 'Otro',
                        motivo=bleach.clean(str(row['Motivo']).strip()) if not pd.isna(row['Motivo']) else 'Cargado desde Excel',
                        veracidad=True,  # Asumimos que los datos del Excel son verídicos
                        anio_solicitud=datetime.now().year,
                        user_id=None  # No se asocia a ningún usuario específico
                    )
                    
                    db.session.add(nuevo_estudiante)
                    estudiantes_agregados += 1
                    
                except Exception as e:
                    errores.append(f'Fila {index + 2}: Error al procesar - {str(e)}')
                    continue
            
            # Confirmar cambios en la base de datos
            try:
                db.session.commit()
                
                # Crear mensaje de éxito
                mensaje = f'Procesamiento completado: {estudiantes_agregados} estudiantes agregados'
                if estudiantes_duplicados > 0:
                    mensaje += f', {estudiantes_duplicados} duplicados omitidos'
                if errores:
                    mensaje += f', {len(errores)} errores encontrados'
                
                flash(mensaje, 'success')
                
                # Mostrar errores si los hay
                if errores:
                    for error in errores[:5]:  # Mostrar solo los primeros 5 errores
                        flash(error, 'warning')
                    if len(errores) > 5:
                        flash(f'... y {len(errores) - 5} errores más', 'warning')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar en la base de datos: {str(e)}', 'danger')
            
            # Limpiar archivo temporal
            os.remove(file_path)
            
        except Exception as e:
            flash(f'Error inesperado al procesar el archivo: {str(e)}', 'danger')
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
    
    else:
        # Si el formulario no es válido, mostrar errores
        print("DEBUG: Errores del formulario:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.student_list'))





#                   EXPORTAR ARCHIVOS DE EXCEL (G)
@admin_bp.route('/export_estudiantes')
@login_required
@role_required(['admin'])
def export_estudiantes():
    """Exportar lista de estudiantes a Excel"""
    try:
        # Obtener todos los estudiantes
        estudiantes = Estudiante.query.all()
        
        # Crear lista de diccionarios con los datos
        data = []
        for estudiante in estudiantes:
            data.append({
                'ID': estudiante.id,
                'Nombre': estudiante.nombre,
                'Apellidos': estudiante.apellidos,
                'DNI': estudiante.dni,
                'Correo': estudiante.correo,
                'Teléfono': estudiante.telefono,
                'País': estudiante.pais,
                'Ciudad': estudiante.ciudad,
                'Dirección': estudiante.direccion,
                'Grado': estudiante.grado,
                'Fecha_Nacimiento': estudiante.fecha_nacimiento.strftime('%Y-%m-%d') if estudiante.fecha_nacimiento else '',
                'Sexo': estudiante.sexo,
                'Motivo': estudiante.motivo,
                'Año_Solicitud': estudiante.anio_solicitud,
                'Veracidad': 'Sí' if estudiante.veracidad else 'No',
                'Rol_Usuario': estudiante.user.role if estudiante.user else 'Sin Usuario'
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Estudiantes', index=False)
            
            # Obtener el workbook y worksheet para formatear
            workbook = writer.book
            worksheet = writer.sheets['Estudiantes']
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Crear nombre de archivo con fecha
        filename = f"estudiantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Enviar archivo
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error al exportar estudiantes: {str(e)}', 'danger')
        return redirect(url_for('admin.student_list'))


@admin_bp.route('/export_inscripciones')
@login_required
@role_required(['admin'])
def export_inscripciones():
    """Exportar lista de inscripciones a Excel"""
    try:
        # Obtener todas las inscripciones con información del estudiante
        inscripciones = Inscripcion.query.join(Estudiante).all()
        
        # Crear lista de diccionarios con los datos
        data = []
        for inscripcion in inscripciones:
            data.append({
                'ID_Inscripción': inscripcion.id,
                'Estudiante_ID': inscripcion.estudiante_id,
                'Nombre_Completo': f"{inscripcion.estudiante.nombre} {inscripcion.estudiante.apellidos}",
                'DNI': inscripcion.estudiante.dni,
                'Correo': inscripcion.estudiante.correo,
                'Teléfono': inscripcion.estudiante.telefono,
                'País': inscripcion.estudiante.pais,
                'Ciudad': inscripcion.estudiante.ciudad,
                'Curso': inscripcion.curso_slug,
                'Fecha_Inscripción': inscripcion.fecha_inscripcion.strftime('%Y-%m-%d %H:%M:%S'),
                'Estado': inscripcion.estado,
                'Razón_Rechazo': inscripcion.razon_rechazo or 'N/A',
                'Grado_Estudios': inscripcion.estudiante.grado,
                'Sexo': inscripcion.estudiante.sexo,
                'Año_Solicitud': inscripcion.estudiante.anio_solicitud
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja principal con todas las inscripciones
            df.to_excel(writer, sheet_name='Todas_Inscripciones', index=False)
            
            # Hojas separadas por estado
            for estado in ['pendiente', 'aceptada', 'rechazada']:
                df_estado = df[df['Estado'] == estado]
                if not df_estado.empty:
                    df_estado.to_excel(writer, sheet_name=f'Estado_{estado.capitalize()}', index=False)
            
            # Hoja de estadísticas
            stats_data = {
                'Estadística': [
                    'Total Inscripciones',
                    'Pendientes',
                    'Aceptadas', 
                    'Rechazadas',
                    'Fecha Generación'
                ],
                'Valor': [
                    len(df),
                    len(df[df['Estado'] == 'pendiente']),
                    len(df[df['Estado'] == 'aceptada']),
                    len(df[df['Estado'] == 'rechazada']),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            # Formatear todas las hojas
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Crear nombre de archivo con fecha
        filename = f"inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Enviar archivo
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error al exportar inscripciones: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_inscripciones'))