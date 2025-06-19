# your_flask_app/blueprints/admin.py - COMPLETO Y CORREGIDO

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..decorators import role_required
from ..models import Estudiante, Inscripcion
from ..forms import EstudianteForm, InscripcionApprovalForm, UploadExcelForm
from ..extensions import db
import bleach
# NUEVAS IMPORTACIONES PARA EXCEL
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask import send_file, make_response
from io import BytesIO

# Crea una instancia de Blueprint
admin_bp = Blueprint('admin', __name__, 
                    template_folder='../templates/admin',
                    url_prefix='/admin')

#                   DASHBOARD PRINCIPAL
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@role_required(['admin'])
def dashboard():
    total_estudiantes = Estudiante.query.count()
    inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()
    return render_template('dashboard.html',
                        title='Panel de Administrador',
                        total_estudiantes=total_estudiantes,
                        inscripciones_pendientes=inscripciones_pendientes)

#                   VER LISTA DE ESTUDIANTES
@admin_bp.route('/students')
@login_required
@role_required(['admin'])
def student_list():
    students = Estudiante.query.all()
    excel_form = UploadExcelForm()
    return render_template('admin/student_list.html', 
                            title='Lista de Estudiantes',
                            students=students, 
                            excel_form=excel_form)

#                   ELIMINAR ESTUDIANTE
@admin_bp.route('/delete_student/<int:id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_student(id):
    student = Estudiante.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Estudiante eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estudiante: {e}', 'danger')
    return redirect(url_for('admin.student_list'))

#                   VER TODAS LAS SOLICITUDES
@admin_bp.route('/manage_inscripciones')
@login_required
@role_required(['admin'])
def manage_inscripciones():
    inscripciones = Inscripcion.query.all()
    excel_form = UploadExcelForm()
    return render_template('manage_inscripcion.html',
                            title='Gestión de Inscripciones',
                            inscripciones=inscripciones,
                            excel_form=excel_form)

#                   APROBAR O RECHAZAR UNA SOLICITUD
@admin_bp.route('/inscripcion/<int:inscripcion_id>/update_status', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def update_inscripcion_status(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    form = InscripcionApprovalForm(obj=inscripcion)

    if form.validate_on_submit(): 
        inscripcion.estado = form.estado.data
        inscripcion.razon_rechazo = bleach.clean(form.razon_rechazo.data) if form.razon_rechazo.data else None
        
        try:
            db.session.commit()
            flash(f'Estado de inscripción {inscripcion.id} actualizado a {inscripcion.estado}.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la inscripción: {e}', 'danger')
        return redirect(url_for('admin.manage_inscripciones'))

    return render_template('admin/update_inscripcion_status.html',
                            title='Actualizar Inscripción',
                            form=form, inscripcion=inscripcion)

#                   PROCESAR ARCHIVO EXCEL DE ESTUDIANTES
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
            file = form.excel_file.data
            filename = secure_filename(file.filename)
            
            print(f"DEBUG: Archivo recibido: {filename}")
            
            upload_folder = 'temp_uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            print(f"DEBUG: Archivo guardado en: {file_path}")
            
            try:
                df = pd.read_excel(file_path)
                print(f"DEBUG: Excel leído correctamente. Filas: {len(df)}")
            except Exception as e:
                flash(f'Error al leer el archivo Excel: {str(e)}', 'danger')
                os.remove(file_path)
                return redirect(url_for('admin.student_list'))
            
            required_columns = ['Nombre', 'Apellidos', 'DNI', 'Correo', 'Telefono', 
                                'Pais', 'Ciudad', 'Direccion', 'Grado', 'Fecha_Nacimiento', 
                                'Sexo', 'Motivo']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'Faltan las siguientes columnas en el Excel: {", ".join(missing_columns)}', 'danger')
                os.remove(file_path)
                return redirect(url_for('admin.student_list'))
            
            estudiantes_agregados = 0
            estudiantes_duplicados = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    if pd.isna(row['Nombre']) or pd.isna(row['Apellidos']) or pd.isna(row['DNI']) or pd.isna(row['Correo']):
                        errores.append(f'Fila {index + 2}: Faltan datos obligatorios (Nombre, Apellidos, DNI, Correo)')
                        continue
                    
                    dni = str(row['DNI']).strip()
                    correo = str(row['Correo']).strip().lower()
                    
                    existing_student = Estudiante.query.filter(
                        (Estudiante.dni == dni) | (Estudiante.correo == correo)
                    ).first()
                    
                    if existing_student:
                        estudiantes_duplicados += 1
                        continue
                    
                    try:
                        if isinstance(row['Fecha_Nacimiento'], str):
                            fecha_nacimiento = datetime.strptime(row['Fecha_Nacimiento'], '%Y-%m-%d').date()
                        else:
                            fecha_nacimiento = row['Fecha_Nacimiento'].date()
                    except:
                        errores.append(f'Fila {index + 2}: Formato de fecha inválido. Use YYYY-MM-DD')
                        continue
                    
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
                        veracidad=True,
                        anio_solicitud=datetime.now().year,
                        user_id=None
                    )
                    
                    db.session.add(nuevo_estudiante)
                    estudiantes_agregados += 1
                    
                except Exception as e:
                    errores.append(f'Fila {index + 2}: Error al procesar - {str(e)}')
                    continue
            
            try:
                db.session.commit()
                
                mensaje = f'Procesamiento completado: {estudiantes_agregados} estudiantes agregados'
                if estudiantes_duplicados > 0:
                    mensaje += f', {estudiantes_duplicados} duplicados omitidos'
                if errores:
                    mensaje += f', {len(errores)} errores encontrados'
                
                flash(mensaje, 'success')
                
                if errores:
                    for error in errores[:5]:
                        flash(error, 'warning')
                    if len(errores) > 5:
                        flash(f'... y {len(errores) - 5} errores más', 'warning')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar en la base de datos: {str(e)}', 'danger')
            
            os.remove(file_path)
            
        except Exception as e:
            flash(f'Error inesperado al procesar el archivo: {str(e)}', 'danger')
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
    
    else:
        print("DEBUG: Errores del formulario:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.student_list'))

#                   EXPORTAR ESTUDIANTES A EXCEL
@admin_bp.route('/export_estudiantes')
@login_required
@role_required(['admin'])
def export_estudiantes():
    try:
        estudiantes = Estudiante.query.all()
        
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
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Estudiantes', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Estudiantes']
            
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
        
        filename = f"estudiantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error al exportar estudiantes: {str(e)}', 'danger')
        return redirect(url_for('admin.student_list'))

#                   EXPORTAR INSCRIPCIONES A EXCEL
@admin_bp.route('/export_inscripciones')
@login_required
@role_required(['admin'])
def export_inscripciones():
    try:
        inscripciones = Inscripcion.query.join(Estudiante).all()
        
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
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Todas_Inscripciones', index=False)
            
            for estado in ['pendiente', 'aceptada', 'rechazada']:
                df_estado = df[df['Estado'] == estado]
                if not df_estado.empty:
                    df_estado.to_excel(writer, sheet_name=f'Estado_{estado.capitalize()}', index=False)
            
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
        
        filename = f"inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'Error al exportar inscripciones: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_inscripciones'))

#                   PROCESAR ARCHIVO EXCEL DE INSCRIPCIONE
#                   PROCESAR ARCHIVO EXCEL DE INSCRIPCIONES - VERSIÓN FINAL CORRECTA
@admin_bp.route('/upload_excel_inscripciones', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def upload_excel_inscripciones():
    print("DEBUG: Función upload_excel_inscripciones llamada")
    print(f"DEBUG: Método de request: {request.method}")
    
    form = UploadExcelForm()
    print(f"DEBUG: Formulario válido: {form.validate_on_submit()}")
    
    if form.validate_on_submit():
        try:
            file = form.excel_file.data
            filename = secure_filename(file.filename)
            
            print(f"DEBUG: Archivo recibido: {filename}")
            
            upload_folder = 'temp_uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            print(f"DEBUG: Archivo guardado en: {file_path}")
            
            try:
                df = pd.read_excel(file_path)
                print(f"DEBUG: Excel leído correctamente. Filas: {len(df)}")
            except Exception as e:
                flash(f'Error al leer el archivo Excel: {str(e)}', 'danger')
                os.remove(file_path)
                return redirect(url_for('admin.manage_inscripciones'))
            
            # Validar columnas requeridas (solo DNI y curso)
            required_columns = ['estudiante_dni', 'curso_slug']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f'Faltan las siguientes columnas en el Excel: {", ".join(missing_columns)}', 'danger')
                os.remove(file_path)
                return redirect(url_for('admin.manage_inscripciones'))
            
            # Contadores para el reporte
            inscripciones_agregadas = 0
            inscripciones_duplicadas = 0
            errores = []
            
            # Procesar cada fila del Excel
            for index, row in df.iterrows():
                try:
                    # Validar datos básicos obligatorios
                    if pd.isna(row['estudiante_dni']) or pd.isna(row['curso_slug']):
                        errores.append(f'Fila {index + 2}: Faltan datos obligatorios (estudiante_dni, curso_slug)')
                        continue
                    
                    # Limpiar y preparar datos
                    estudiante_dni = str(row['estudiante_dni']).strip()
                    curso_slug = str(row['curso_slug']).strip()
                    
                    # Buscar el estudiante registrado por DNI
                    estudiante = Estudiante.query.filter_by(dni=estudiante_dni).first()
                    if not estudiante:
                        errores.append(f'Fila {index + 2}: No se encontró estudiante registrado con DNI {estudiante_dni}')
                        continue
                    
                    # Verificar si ya existe una inscripción para este estudiante y curso
                    existing_inscripcion = Inscripcion.query.filter_by(
                        estudiante_id=estudiante.id, 
                        curso_slug=curso_slug
                    ).first()
                    
                    if existing_inscripcion:
                        inscripciones_duplicadas += 1
                        continue
                    
                    # Crear nueva inscripción para el estudiante registrado
                    nueva_inscripcion = Inscripcion(
                        estudiante_id=estudiante.id,  # Vincular al estudiante existente
                        curso_slug=bleach.clean(curso_slug),
                        estado='pendiente',  # Siempre pendiente al crear solicitud
                        razon_rechazo=None,
                        fecha_inscripcion=datetime.now()
                    )
                    
                    db.session.add(nueva_inscripcion)
                    inscripciones_agregadas += 1
                    
                except Exception as e:
                    errores.append(f'Fila {index + 2}: Error al procesar - {str(e)}')
                    continue
            
            # Confirmar cambios en la base de datos
            try:
                db.session.commit()
                
                # Crear mensaje de éxito
                mensaje = f'Procesamiento completado: {inscripciones_agregadas} solicitudes de beca agregadas'
                if inscripciones_duplicadas > 0:
                    mensaje += f', {inscripciones_duplicadas} duplicadas omitidas'
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
    
    return redirect(url_for('admin.manage_inscripciones'))