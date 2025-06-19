# your_flask_app/blueprints/admin.py - COMPLETO Y CORREGIDO

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required
from datetime import datetime, date, timedelta
import os
import bleach
import pandas as pd
from werkzeug.utils import secure_filename
from io import BytesIO
from sqlalchemy import or_, func
import plotly.express as px
import json
import base64

# Importa tus modelos y extensiones
from ..decorators import role_required
from ..models import Estudiante, Inscripcion, Curso, User
from ..extensions import db
from ..forms import EstudianteForm, InscripcionApprovalForm, UploadExcelForm


# Crea una instancia de Blueprint
admin_bp = Blueprint('admin', __name__, 
                     template_folder='../templates/admin',
                     url_prefix='/admin')

@admin_bp.route('/update_inscripcion_status/<int:inscripcion_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def update_inscripcion_status(inscripcion_id):
    """
    Permite a un administrador actualizar el estado de una inscripción.
    Por ejemplo, de 'pendiente' a 'aprobado' o 'rechazado'.
    """
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)

    # Lógica de actualización de estado
    # Esto es solo un ejemplo, ajústalo a cómo manejas los estados en tu modelo Inscripcion
    # Podrías pasar el nuevo estado como un parámetro de formulario si necesitas más flexibilidad.
    if inscripcion.estado == 'pendiente': # Asumiendo que tienes un campo 'estado'
        inscripcion.estado = 'aprobado'
        flash(f'La inscripción de {inscripcion.estudiante.nombre} ha sido aprobada.', 'success')
    elif inscripcion.estado == 'aprobado':
        inscripcion.estado = 'rechazado'
        flash(f'La inscripción de {inscripcion.estudiante.nombre} ha sido rechazada.', 'warning')
    else:
        # Si ya está en otro estado o quieres un toggle diferente
        inscripcion.estado = 'pendiente' # O el estado que desees para revertir/cambiar
        flash(f'El estado de la inscripción de {inscripcion.estudiante.nombre} se ha actualizado a {inscripcion.estado}.', 'info')

    db.session.commit()
    return redirect(url_for('admin.manage_inscripciones'))




@admin_bp.route('/statistics')
@login_required
@role_required(['admin'])
def admin_statistics():
    # --- CÓDIGO EXISTENTE PARA LAS ESTADÍSTICAS GENERALES ---
    total_estudiantes = Estudiante.query.count()
    total_inscripciones = Inscripcion.query.count()
    total_cursos = Curso.query.count()

    # Contar inscripciones por estado
    inscripciones_pendientes = Inscripcion.query.filter_by(estado='Pendiente').count()
    inscripciones_aprobadas = Inscripcion.query.filter_by(estado='Aprobada').count()
    inscripciones_rechazadas = Inscripcion.query.filter_by(estado='Rechazada').count()

    # --- CÓDIGO PARA EL MAPA COROPLÉTICO (Generación de IMAGEN PNG) ---
    mapa_coropletico_img_src = None # Guardará la imagen en formato Base64

    try:
        # 1. Obtener los datos de estudiantes agrupados por país
        estudiantes_por_pais_query = db.session.query(
            Estudiante.pais,
            func.count(Estudiante.id)
        ).filter(
            Estudiante.pais.isnot(None),
            Estudiante.pais != ''
        ).group_by(Estudiante.pais).all()

        df_estudiantes_pais = pd.DataFrame(estudiantes_por_pais_query, columns=['Pais', 'CantidadEstudiantes'])

        # --- Mapeo de nombres de países a códigos ISO-3 (Para Plotly) ---
        country_iso_mapping = {
            'Argentina': 'ARG', 'Bolivia': 'BOL', 'Brasil': 'BRA', 'Chile': 'CHL',
            'Colombia': 'COL', 'Costa Rica': 'CRI', 'Cuba': 'CUB', 'Ecuador': 'ECU',
            'El Salvador': 'SLV', 'Guatemala': 'GTM', 'Honduras': 'HND', 'México': 'MEX',
            'Nicaragua': 'NIC', 'Panamá': 'PAN', 'Paraguay': 'PRY', 'Perú': 'PER',
            'República Dominicana': 'DOM', 'Uruguay': 'URY', 'Venezuela': 'VEN',
            'Estados Unidos': 'USA',
            # Asegúrate de añadir cualquier otro país que puedas tener en tu DB
        }
        
        df_estudiantes_pais['PaisISO'] = df_estudiantes_pais['Pais'].map(country_iso_mapping)
        df_estudiantes_pais_plot = df_estudiantes_pais.dropna(subset=['PaisISO'])

        # 2. Crear el mapa coroplético con Plotly Express
        fig = px.choropleth(df_estudiantes_pais_plot,
                            locations="PaisISO",
                            locationmode="ISO-3",
                            color="CantidadEstudiantes",
                            hover_name="Pais",
                            color_continuous_scale="Blues",
                            range_color=[0, df_estudiantes_pais_plot['CantidadEstudiantes'].max() if not df_estudiantes_pais_plot.empty else 1],
                            title="Concentración de Estudiantes por País",
                            scope="world"
                           )
        
        # Ajustes de geos para el mapa
        fig.update_geos(
            # fitbounds="locations",
            visible=False,
            showcountries=True,
            countrycolor="DarkGrey",
            showland=True,
            landcolor="LightGrey",
            # Opcional: Centrar en LATAM. Ajusta estos rangos si el mapa no se ve como esperas.
            lataxis_range=[-55, 35], 
            lonaxis_range=[-120, -30],
        )
        
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

        # Convertir la figura a una IMAGEN PNG y codificarla en Base64
        img_bytes = fig.to_image(format="png", width=1200, height=900, scale=1) # Ajuste de tamaño aquí
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        mapa_coropletico_img_src = f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"Error al generar el mapa coroplético: {e}")
        flash(f"Error al generar el mapa de países: {e}", "danger")
        mapa_coropletico_img_src = None

    return render_template(
        'admin/admin_statistics.html',
        total_estudiantes=total_estudiantes,
        total_inscripciones=total_inscripciones,
        total_cursos=total_cursos,
        inscripciones_pendientes=inscripciones_pendientes,
        inscripciones_aprobadas=inscripciones_aprobadas,
        inscripciones_rechazadas=inscripciones_rechazadas,
        estudiantes_por_pais=estudiantes_por_pais_query,
        mapa_coropletico_img_src=mapa_coropletico_img_src
    )


@admin_bp.route('/api/data_mapa')
@login_required
@role_required(['admin'])
def data_mapa():
    student_counts_raw = db.session.query(
        Estudiante.pais,
        func.count(Inscripcion.id)
    ).join(Estudiante, Inscripcion.estudiante_id == Estudiante.id)\
     .filter(Inscripcion.estado.in_(['pendiente', 'aprobada'])) \
     .group_by(Estudiante.pais)\
     .all()

    student_counts = {}
    for pais, count in student_counts_raw:
        if pais:
            student_counts[pais] = count

    # >>> OPCIONAL: Datos de ejemplo para pruebas si tu DB está vacía o si quieres ver el mapa funcionando con algo <<<
    # student_counts = {
    #     "Guatemala": 150, "Mexico": 300, "Colombia": 200, "Argentina": 180,
    #     "Peru": 120, "Chile": 90, "Ecuador": 70, "Bolivia": 60,
    #     "Venezuela": 50, "Cuba": 30, "Dominican Republic": 45, "Puerto Rico": 25,
    #     "Honduras": 35, "El Salvador": 40, "Nicaragua": 20, "Costa Rica": 80,
    #     "Panama": 55, "Paraguay": 65, "Uruguay": 75
    # }

    return jsonify(student_counts)


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@role_required(['admin'])
def dashboard():
    total_estudiantes = Estudiante.query.count()
    inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()
    total_cursos = Curso.query.count()
    
    total_cursos_activos = Curso.query.filter_by(activo=True).count()
    total_estudiantes = Estudiante.query.count() 
    total_inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()

    solicitudes_por_pais_query = db.session.query(
        Estudiante.pais,
        func.count(Inscripcion.id)
    ).join(Estudiante, Inscripcion.estudiante_id == Estudiante.id)\
     .filter(Estudiante.pais.isnot(None))\
     .group_by(Estudiante.pais).all()

    solicitudes_map_data = {pais: count for pais, count in solicitudes_por_pais_query}

    return render_template(
        'admin/admin_dashboard.html',
        title='Panel de Administración',
        total_cursos=total_cursos_activos, # Usamos el conteo de cursos activos
        total_estudiantes=total_estudiantes,
        total_inscripciones_pendientes=total_inscripciones_pendientes,
        solicitudes_por_pais=solicitudes_map_data 
    )


#                       VER LISTA DE ESTUDIANTES
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

#                       ELIMINAR ESTUDIANTE
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


#                       PROCESAR ARCHIVO EXCEL DE ESTUDIANTES
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
                        errores.append(f'Fila {index + 2}: Formato de fecha inválido. Use AAAA-MM-DD')
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
            print(f"   {field}: {errors}")
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.student_list'))

#                       EXPORTAR ESTUDIANTES A EXCEL
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
                # Ajusta el ancho de columna usando openpyxl directamente
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
    

# your_flask_app/blueprints/admin.py (Continuación)

#                       EXPORTAR INSCRIPCIONES A EXCEL
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
                    # Ajusta el ancho de columna usando openpyxl directamente
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

#                       PROCESAR ARCHIVO EXCEL DE INSCRIPCIONES
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
            print(f"   {field}: {errors}")
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('admin.manage_inscripciones')) # Redirige a la gestión de inscripciones

@admin_bp.route('/manage_inscripciones', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def manage_inscripciones():
    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Número de inscripciones por página

    # Obtener parámetros de filtro de la URL
    filter_estado = request.args.get('estado', 'all')
    filter_curso = request.args.get('curso', 'all')
    search_query = request.args.get('search', '')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Construir la consulta base
    query = Inscripcion.query.join(Estudiante) # Unir con Estudiante para poder filtrar por datos del estudiante

    # Aplicar filtros
    if filter_estado != 'all':
        query = query.filter(Inscripcion.estado == filter_estado)

    # Filtrar por curso (asumiendo que curso_slug es un identificador único para los cursos)
    if filter_curso != 'all':
        query = query.filter(Inscripcion.curso_slug == filter_curso)

    # Filtrar por búsqueda general (nombre, DNI, correo del estudiante)
    if search_query:
        search_pattern = f"%{bleach.clean(search_query)}%"
        query = query.filter(or_(
            Estudiante.nombre.ilike(search_pattern),
            Estudiante.apellidos.ilike(search_pattern),
            Estudiante.dni.ilike(search_pattern),
            Estudiante.correo.ilike(search_pattern)
        ))

    # Filtrar por rango de fechas
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Inscripcion.fecha_inscripcion >= start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Para incluir todo el día de end_date, filtramos hasta el inicio del día siguiente
            query = query.filter(Inscripcion.fecha_inscripcion < (end_date + timedelta(days=1)))
    except ValueError:
        flash('Formato de fecha inválido. Por favor use AAAA-MM-DD.', 'danger')
        # Redirigir para limpiar los parámetros de fecha inválidos
        return redirect(url_for('admin.manage_inscripciones', 
                                estado=filter_estado, 
                                curso=filter_curso, 
                                search=search_query))

    # Ordenar y paginar
    inscripciones = query.order_by(Inscripcion.fecha_inscripcion.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Obtener todos los cursos para el filtro desplegable
    all_cursos = Curso.query.all()

    # Manejar las acciones de aprobación/rechazo
    if request.method == 'POST':
        form = InscripcionApprovalForm()
        if form.validate_on_submit():
            inscripcion_id = form.inscripcion_id.data
            action = form.action.data
            razon_rechazo = bleach.clean(form.razon_rechazo.data) if form.razon_rechazo.data else None
            
            inscripcion = Inscripcion.query.get_or_404(inscripcion_id)

            if action == 'approve':
                inscripcion.estado = 'Aprobada'
                inscripcion.razon_rechazo = None # Limpiar razón si se aprueba
                flash(f'Inscripción {inscripcion.id} aprobada exitosamente.', 'success')
            elif action == 'reject':
                inscripcion.estado = 'Rechazada'
                inscripcion.razon_rechazo = razon_rechazo
                flash(f'Inscripción {inscripcion.id} rechazada exitosamente.', 'warning')
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar la inscripción: {e}', 'danger')
            
            # Redirigir de vuelta a la página con los mismos filtros y página
            return redirect(url_for('admin.manage_inscripciones', 
                                    page=page, 
                                    estado=filter_estado, 
                                    curso=filter_curso, 
                                    search=search_query,
                                    start_date=start_date_str,
                                    end_date=end_date_str))
        else:
            # Si el formulario POST no es válido (ej. falta razón de rechazo)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en el formulario ({field}): {error}', 'danger')
            # Intentar mantener los parámetros de paginación y filtro
            return redirect(url_for('admin.manage_inscripciones', 
                                    page=page, 
                                    estado=filter_estado, 
                                    curso=filter_curso, 
                                    search=search_query,
                                    start_date=start_date_str,
                                    end_date=end_date_str))


    # Si es un GET request o después de un POST no válido sin redirección
    form = InscripcionApprovalForm() # Asegúrate de pasar un formulario vacío para cada fila en el template
    return render_template('admin/manage_inscripciones.html', 
                           title='Gestión de Inscripciones',
                           inscripciones=inscripciones,
                           form=form, # Pasar el formulario para el modal
                           filter_estado=filter_estado,
                           filter_curso=filter_curso,
                           search_query=search_query,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           all_cursos=all_cursos) # Pasar todos los cursos para el filtro

@admin_bp.route('/manage_cursos')
@login_required
@role_required(['admin'])
def manage_cursos():
    cursos = Curso.query.all()
    return render_template('admin/manage_cursos.html', cursos=cursos)

@admin_bp.route('/toggle_curso_status/<slug>', methods=['POST'])
@login_required
@role_required(['admin'])
def toggle_curso_status(slug):
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    curso.activo = not curso.activo
    db.session.commit()
    flash(f'Estado del curso "{curso.nombre}" actualizado a {"Activo" if curso.activo else "Inactivo"}.', 'success')
    return redirect(url_for('admin.manage_cursos'))

@admin_bp.route('/edit_curso/<slug>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def edit_curso(slug):
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    form = EstudianteForm(obj=curso) # Reutiliza EstudianteForm o crea un CursoForm

    if form.validate_on_submit():
        curso.nombre = bleach.clean(form.nombre.data)
        # Asume que tu CursoForm tiene un campo slug_data si lo estás permitiendo editar
        # Si no, el slug no debería ser editable directamente por un form de Estudiante
        # Para el ejemplo, usaremos el mismo slug, pero esto debería venir de un CursoForm
        # curso.slug = generate_slug(form.nombre.data) # Si quieres generar uno nuevo
        curso.descripcion = bleach.clean(form.descripcion.data) # Asumiendo campo en CursoForm
        curso.activo = form.activo.data # Asumiendo campo en CursoForm

        try:
            db.session.commit()
            flash('Curso actualizado exitosamente.', 'success')
            return redirect(url_for('admin.manage_cursos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el curso: {e}', 'danger')
    
    return render_template('admin/edit_curso.html', form=form, curso=curso, title='Editar Curso')


@admin_bp.route('/add_curso', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def add_curso():
    form = EstudianteForm() # Debería ser CursoForm()

    if form.validate_on_submit():
        # Generar un slug a partir del nombre del curso
        new_slug = bleach.clean(form.nombre.data).lower().replace(' ', '-')
        # Verificar si el slug ya existe
        existing_curso = Curso.query.filter_by(slug=new_slug).first()
        if existing_curso:
            flash('Ya existe un curso con este nombre. Por favor, elige uno diferente.', 'danger')
            return render_template('admin/add_curso.html', form=form, title='Agregar Curso')

        new_curso = Curso(
            nombre=bleach.clean(form.nombre.data),
            slug=new_slug, # Asignar el slug generado
            descripcion=bleach.clean(form.descripcion.data), # Asumiendo campo en CursoForm
            activo=form.activo.data # Asumiendo campo en CursoForm
        )
        db.session.add(new_curso)
        try:
            db.session.commit()
            flash('Curso agregado exitosamente.', 'success')
            return redirect(url_for('admin.manage_cursos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar el curso: {e}', 'danger')

    return render_template('admin/add_curso.html', form=form, title='Agregar Curso')


@admin_bp.route('/delete_curso/<slug>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_curso(slug):
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    
    # Opcional: Verificar si hay inscripciones asociadas antes de eliminar
    inscripciones_asociadas = Inscripcion.query.filter_by(curso_slug=curso.slug).count()
    if inscripciones_asociadas > 0:
        flash(f'No se puede eliminar el curso "{curso.nombre}" porque tiene {inscripciones_asociadas} inscripciones asociadas.', 'danger')
        return redirect(url_for('admin.manage_cursos'))

    try:
        db.session.delete(curso)
        db.session.commit()
        flash('Curso eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el curso: {e}', 'danger')
    
    return redirect(url_for('admin.manage_cursos'))


