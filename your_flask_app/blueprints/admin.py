# your_flask_app/blueprints/admin.py - COMPLETO Y CORREGIDO

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
<<<<<<< HEAD
from ..decorators import role_required # Importa tu decorador
from ..models import Estudiante, Inscripcion, Curso, User # <--- IMPORTANTE: Añade 'Curso' aquífrom ..forms import EstudianteForm, InscripcionApprovalForm # Importa los formularios si es necesario
from ..extensions import db # Necesario para interactuar con la base de datos
from ..forms import EstudianteForm, InscripcionApprovalForm, UploadExcelForm # Importa UploadExcelForm si no lo tienes
import bleach # Para limpiar la entrada del usuario
# Nuevas importaciones para excel
=======
from ..decorators import role_required
from ..models import Estudiante, Inscripcion
from ..forms import EstudianteForm, InscripcionApprovalForm, UploadExcelForm
from ..extensions import db
import bleach
# NUEVAS IMPORTACIONES PARA EXCEL
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask import send_file, make_response
from io import BytesIO
<<<<<<< HEAD
import pandas as pd
from datetime import datetime
from sqlalchemy import or_,func # <--- ¡Añade esta línea!
from flask import jsonify

import plotly.express as px
import json
import base64
=======
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db

# Crea una instancia de Blueprint
admin_bp = Blueprint('admin', __name__, 
                    template_folder='../templates/admin',
                    url_prefix='/admin')

<<<<<<< HEAD

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
                            color_continuous_scale="Blues", # <--- CAMBIADO A AZULES
                            range_color=[0, df_estudiantes_pais_plot['CantidadEstudiantes'].max() if not df_estudiantes_pais_plot.empty else 1],
                            title="Concentración de Estudiantes por País",
                            scope="world"
                           )
        
        # Ajustes de geos para el mapa
        fig.update_geos(
            # fitbounds="locations", # Podrías quitar esto si quieres que se vea todo el continente y no solo los países con datos
            visible=False,          # Oculta el fondo del mapa mundial si no hay datos
            showcountries=True,     # <--- AHORA MUESTRA TODOS LOS PAÍSES
            countrycolor="DarkGrey", # <--- COLOR DEL BORDE DE LOS PAÍSES
            showland=True,          # Muestra la tierra
            landcolor="LightGrey",  # Color de la tierra donde no hay datos
            # Opcional: Centrar en LATAM. Ajusta estos rangos si el mapa no se ve como esperas.
            lataxis_range=[-55, 35], 
            lonaxis_range=[-120, -30],
        )
        
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

        # Convertir la figura a una IMAGEN PNG y codificarla en Base64
        img_bytes = fig.to_image(format="png", width=1000, height=900, scale=1)
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
@role_required(['admin']) # Asegúrate de que solo los administradores puedan acceder
def data_mapa():
    # Consulta la base de datos para contar el número de inscripciones por país.
    # Se une a la tabla Estudiante para obtener el país de residencia.
    # Solo cuenta inscripciones que NO sean 'rechazada' o 'cancelada'
    # (ajusta el filtro de estado según lo que consideres "solicitudes pendientes/activas")

    student_counts_raw = db.session.query(
        Estudiante.pais,
        func.count(Inscripcion.id)
    ).join(Estudiante, Inscripcion.estudiante_id == Estudiante.id)\
     .filter(Inscripcion.estado.in_(['pendiente', 'aprobada'])) \
     .group_by(Estudiante.pais)\
     .all()

    # Formatear los datos para el frontend como un diccionario { "Pais": conteo }
    student_counts = {}
    for pais, count in student_counts_raw:
        if pais: # Asegurarse de que el país no sea None/vacío
            student_counts[pais] = count

    # >>> OPCIONAL: Datos de ejemplo para pruebas si tu DB está vacía o si quieres ver el mapa funcionando con algo <<<
    # Puedes descomentar y usar esto para probar si no tienes datos en la DB aún.
    # Asegúrate de que los nombres de los países aquí coincidan con los de tu archivo GeoJSON.
    student_counts = {
        "Guatemala": 150,
        "Mexico": 300,
        "Colombia": 200,
        "Argentina": 180,
        "Peru": 120,
        "Chile": 90,
        "Ecuador": 70,
        "Bolivia": 60,
        "Venezuela": 50,
        "Cuba": 30,
        "Dominican Republic": 45,
        "Puerto Rico": 25,
        "Honduras": 35,
        "El Salvador": 40,
        "Nicaragua": 20,
        "Costa Rica": 80,
        "Panama": 55,
        "Paraguay": 65,
        "Uruguay": 75
    }

    return jsonify(student_counts)







@admin_bp.route('/') # Esta ruta se accederá como /admin/
@admin_bp.route('/dashboard') # Esta ruta se accederá como /admin/dashboard
=======
#                   DASHBOARD PRINCIPAL
@admin_bp.route('/')
@admin_bp.route('/dashboard')
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db
@login_required
@role_required(['admin'])
def dashboard():
    total_estudiantes = Estudiante.query.count()
    inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()
<<<<<<< HEAD
    total_cursos = Curso.query.count() # <--- NUEVA LÍNEA: Obtiene el total de cursos
    
    total_cursos = Curso.query.filter_by(activo=True).count()
    total_estudiantes = Estudiante.query.count() 
    total_inscripciones_pendientes = Inscripcion.query.filter_by(estado='pendiente').count()

    # --- NUEVO CÓDIGO PARA LOS DATOS DEL MAPA ---
    # Contar estudiantes (o solicitudes) por país
    # Asume que quieres contar estudiantes que tienen un perfil.
    # Si quieres contar SOLICITUDES DE BECA, la consulta sería sobre la tabla Inscripcion
    # y necesitaría un JOIN con Estudiante para obtener el país.
    
    # Opción 1: Contar estudiantes registrados por país
    estudiantes_por_pais = db.session.query(
        Estudiante.pais,
        func.count(Estudiante.id)
    ).group_by(Estudiante.pais).all()

    # Opción 2 (más precisa para "solicitudes de beca" si una solicitud es una Inscripcion):
    # Contar INSCRIPCIONES (solicitudes) por país del estudiante asociado
    # NOTA: Asegúrate que tu modelo Inscripcion tiene una relación con Estudiante (que debe tenerla).
    # from ..models import Estudiante, Inscripcion # Asegúrate de que ambas estén importadas arriba
    solicitudes_por_pais_query = db.session.query(
        Estudiante.pais,
        func.count(Inscripcion.id)
    ).join(Estudiante, Inscripcion.estudiante_id == Estudiante.id)\
     .filter(Estudiante.pais.isnot(None))\
     .group_by(Estudiante.pais).all()

    # Convertir el resultado a un diccionario para fácil acceso en JavaScript
    # Usaremos la Opción 2 para el mapa de calor, ya que es "solicitudes de beca".
    solicitudes_map_data = {pais: count for pais, count in solicitudes_por_pais_query}

    # --- FIN DEL NUEVO CÓDIGO ---

    return render_template(
        'admin/admin_dashboard.html',
        title='Panel de Administración',
        total_cursos=total_cursos,
        total_estudiantes=total_estudiantes,
        total_inscripciones_pendientes=total_inscripciones_pendientes,
        # <--- PASA LOS NUEVOS DATOS AL TEMPLATE ---
        solicitudes_por_pais=solicitudes_map_data 
    )



=======
    return render_template('dashboard.html',
                        title='Panel de Administrador',
                        total_estudiantes=total_estudiantes,
                        inscripciones_pendientes=inscripciones_pendientes)
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db

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

<<<<<<< HEAD
=======
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
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db

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
    
<<<<<<< HEAD
    return redirect(url_for('admin.student_list'))


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
        flash('Formato de fecha inválido. Por favor usa YYYY-MM-DD.', 'danger')
        # Redirigir para limpiar los parámetros de fecha incorrectos
        return redirect(url_for('admin.manage_inscripciones',
                                 estado=filter_estado,
                                 curso=filter_curso,
                                 search=search_query))

    # Ordenar las inscripciones
    inscripciones = query.order_by(Inscripcion.fecha_inscripcion.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Obtener todos los cursos únicos para el filtro desplegable
    # Esto asume que los slugs de cursos son estáticos o que los obtendrás de un modelo 'Curso' si existe
    unique_cursos_slugs = db.session.query(Inscripcion.curso_slug).distinct().all()
    # Convertir a una lista de strings
    all_cursos = [s[0] for s in unique_cursos_slugs if s[0]]

    # Información de los cursos (mantener como un diccionario para mostrar nombres amigables)
    cursos_info = {
        'programadores-junior': {'titulo': 'Programa de Programadores Jr.'},
        'ciberseguridad': {'titulo': 'Curso de Ciberseguridad'}
        # Añade aquí otros cursos que tengas
    }
    # Asegurarse de que all_cursos incluya los cursos conocidos, aunque no tengan inscripciones aún
    for slug, info in cursos_info.items():
        if slug not in all_cursos:
            all_cursos.append(slug)


    return render_template('manage_inscripcion.html',
                           inscripciones=inscripciones, # Ahora es un objeto Pagination
                           cursos_info=cursos_info,
                           all_cursos=sorted(all_cursos), # Pasar cursos únicos para el filtro
                           filter_estado=filter_estado,
                           filter_curso=filter_curso,
                           search_query=search_query,
                           start_date=start_date_str,
                           end_date=end_date_str)


@admin_bp.route('/manage_inscripciones/<int:inscripcion_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def update_inscripcion_status(inscripcion_id):
    inscripcion = Inscripcion.query.get_or_404(inscripcion_id)
    form = InscripcionApprovalForm(obj=inscripcion) # Pre-llenar el formulario con datos de la inscripción

    if form.validate_on_submit():
        inscripcion.estado = bleach.clean(form.estado.data)
        inscripcion.razon_rechazo = bleach.clean(form.razon_rechazo.data) if form.razon_rechazo.data else None

        db.session.commit()
        flash(f'Estado de inscripción {inscripcion_id} actualizado a "{inscripcion.estado}".', 'success')
        return redirect(url_for('admin.manage_inscripciones'))
    
    # Asegurarse de que el estudiante esté cargado para la plantilla
    estudiante_asociado = Estudiante.query.get(inscripcion.estudiante_id)

    return render_template('update_inscripcion_status.html',
                           title='Actualizar Estado',
                           form=form,
                           inscripcion=inscripcion,
                           estudiante_asociado=estudiante_asociado) # Pasar el estudiante asociado









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


@admin_bp.route('/export_inscripciones', methods=['GET'])
@login_required
@role_required(['admin'])
def export_inscripciones():
    # Obtener los mismos parámetros de filtro que manage_inscripciones
    filter_estado = request.args.get('estado', 'all')
    filter_curso = request.args.get('curso', 'all')
    search_query = request.args.get('search', '')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = Inscripcion.query.join(Estudiante) # Unir con Estudiante

    if filter_estado != 'all':
        query = query.filter(Inscripcion.estado == filter_estado)
    if filter_curso != 'all':
        query = query.filter(Inscripcion.curso_slug == filter_curso)

    if search_query:
        search_pattern = f"%{bleach.clean(search_query)}%"
        query = query.filter(or_(
            Estudiante.nombre.ilike(search_pattern),
            Estudiante.apellidos.ilike(search_pattern),
            Estudiante.dni.ilike(search_pattern),
            Estudiante.correo.ilike(search_pattern)
        ))

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Inscripcion.fecha_inscripcion >= start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Inscripcion.fecha_inscripcion < (end_date + timedelta(days=1)))
    except ValueError:
        flash('Formato de fecha inválido para exportación. Por favor usa YYYY-MM-DD.', 'danger')
        return redirect(url_for('admin.manage_inscripciones'))

    inscripciones = query.order_by(Inscripcion.fecha_inscripcion.desc()).all()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Pestaña de Inscripciones
        data = []
        for inscripcion in inscripciones:
            estudiante = inscripcion.estudiante # Acceder al estudiante relacionado
            data.append({
                'ID Inscripción': inscripcion.id,
                'Nombre Estudiante': estudiante.nombre if estudiante else 'N/A',
                'Apellidos Estudiante': estudiante.apellidos if estudiante else 'N/A',
                'DNI Estudiante': estudiante.dni if estudiante else 'N/A',
                'Correo Estudiante': estudiante.correo if estudiante else 'N/A',
                'País': estudiante.pais if estudiante else 'N/A',
                'Ciudad': estudiante.ciudad if estudiante else 'N/A',
                'Grado': estudiante.grado if estudiante else 'N/A',
                'Fecha Nacimiento': estudiante.fecha_nacimiento.strftime('%Y-%m-%d') if estudiante and estudiante.fecha_nacimiento else 'N/A',
                'Institución Educativa': estudiante.institucion_educativa if estudiante else 'N/A',
                'Año Graduación': estudiante.anio_graduacion if estudiante else 'N/A',
                'Curso': inscripcion.curso_slug,
                'Fecha Solicitud': inscripcion.fecha_inscripcion.strftime('%Y-%m-%d %H:%M:%S'),
                'Estado': inscripcion.estado,
                'Razón Rechazo': inscripcion.razon_rechazo or ''
            })
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Inscripciones', index=False)

        # Pestaña de Estadísticas (mantener como estaba o ajustar si es necesario)
        total_inscripciones = Inscripcion.query.count()
        pendientes = Inscripcion.query.filter_by(estado='pendiente').count()
        aceptadas = Inscripcion.query.filter_by(estado='aceptada').count()
        rechazadas = Inscripcion.query.filter_by(estado='rechazada').count()
        # Puedes añadir más estadísticas si lo deseas

        stats_data = {
            'Métrica': ['Total de Inscripciones', 'Pendientes', 'Aceptadas', 'Rechazadas', 'Fecha de Exportación'],
            'Valor': [
                total_inscripciones,
                pendientes,
                aceptadas,
                rechazadas,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)

        # Formatear todas las hojas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(worksheet.columns):
                max_length = 0
                column = [cell for cell in col]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50) # Limitar el ancho para evitar columnas excesivamente anchas
                worksheet.set_column(i, i, adjusted_width) # set_column usa índices de columna, no letras

    output.seek(0)

    filename = f"inscripciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )




@admin_bp.route('/manage_cursos')
@login_required
@role_required(['admin'])
def manage_cursos():
    cursos = Curso.query.all() # Obtener todos los cursos
    return render_template('manage_cursos.html', cursos=cursos)

@admin_bp.route('/toggle_curso_status/<slug>', methods=['POST'])
@login_required
@role_required(['admin'])
def toggle_curso_status(slug):
    curso = Curso.query.filter_by(slug=slug).first_or_404()
    curso.activo = not curso.activo # Cambiar el estado booleano
    db.session.commit()
    flash(f'El estado del curso "{curso.nombre}" ha sido actualizado a {"Activo" if curso.activo else "Inactivo"}.', 'success')
    return redirect(url_for('admin.manage_cursos'))
=======
    return redirect(url_for('admin.manage_inscripciones'))
>>>>>>> 046713a14b52c2d51e3448a4a8e5ccd0df8a79db
