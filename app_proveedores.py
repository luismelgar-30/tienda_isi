from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
import pandas as pd
from io import BytesIO
from flask import send_file
from flask import Flask, session
import io
import datetime
from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime

app_proveedores = Flask(__name__)
app_proveedores.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/proveedores'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="proveedores", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="proveedores"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def proveedores_exists(id_proveedor):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM proveedores WHERE id_proveedor = %s"
    cursor.execute(query, (id_proveedor,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

def check_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Verifica si el permiso está presente en la sesión
            if session.get(permission) != 1:
                # Si no tiene permiso, redirige a la página principal
                return redirect("http://127.0.0.1:5030/index_principal")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="proyecto_is1"
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
        return connection
    except Error as e:
        error_message = f"Error al conectar a la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return None

def get_proveedor(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = "SELECT * FROM proveedores LIMIT %s OFFSET %s"
    
    try:
        cursor.execute(query, (per_page, offset))
        proveedores = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM proveedores")
        total_count = cursor.fetchone()[0]

        return proveedores, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_proveedor_by_id(id_proveedor):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM proveedores WHERE id_proveedor = %s"
    try:
        cursor.execute(query, (id_proveedor,))
        proveedores = cursor.fetchone()
        return proveedores
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_user(Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()

    # Validar Documento
    error_message = validate_document(Documento, tipo)
    if error_message:
        print(f"Validation error: {error_message}")
        return False

    # Asegura el formato del teléfono
    Telefono = Telefono.replace("-", "")
    if len(Telefono) == 8:
        Telefono = Telefono[:4] + '-' + Telefono[4:]
    
    query = """INSERT INTO proveedores (Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre del Proveedor: {Nombre_del_proveedor}, Compañía: {nombre_compañia}, Teléfono: {Telefono}"
        log_action('Inserted', screen_name='proveedores', details=details)  # Registro de log
        print("Proveedor insertado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def update_user(id_proveedor, Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()
    query = """UPDATE proveedores
               SET Nombre_del_proveedor = %s, Producto_Servicio = %s, Historial_de_desempeño = %s, nombre_compañia = %s, Telefono = %s, Ciudad = %s, tipo = %s, Documento = %s
               WHERE id_proveedor = %s"""
    values = (Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento, id_proveedor)
    
    try:
        print(f"Ejecutando consulta: {query} con valores {values}")
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Proveedor: {id_proveedor}, Nombre: {Nombre_del_proveedor}, Compañía: {nombre_compañia}"
        log_action('Updated', screen_name='proveedores', details=details)  # Registro de log
        print(f"Proveedor actualizado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def delete_proveedor(id_proveedor):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()
    query = "DELETE FROM proveedores WHERE id_proveedor = %s"
    
    try:
        cursor.execute(query, (id_proveedor,))
        connection.commit()
        details = f"ID Proveedor: {id_proveedor}"
        log_action('Deleted', screen_name='proveedores', details=details)  # Registro de log
        print("Proveedor eliminado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def search_users(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0

    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Normaliza el número de teléfono
    if search_criteria == 'Telefono':
        # Elimina guiones del input de búsqueda
        search_query = search_query.replace('-', '')

        # Consulta que elimina guiones del teléfono almacenado en la base de datos
        query = """
        SELECT * FROM proveedores
        WHERE REPLACE(Telefono, '-', '') LIKE %s
        LIMIT %s OFFSET %s
        """
    else:
        query = f"SELECT * FROM proveedores WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"

    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        proveedores = cursor.fetchall()

        # Obtén el total de proveedores con la misma condición
        if search_criteria == 'Telefono':
            cursor.execute("""
            SELECT COUNT(*) FROM proveedores
            WHERE REPLACE(Telefono, '-', '') LIKE %s
            """, (f'%{search_query}%',))
        else:
            cursor.execute(f"SELECT COUNT(*) FROM proveedores WHERE {search_criteria} LIKE %s", (f'%{search_query}%',))
        
        total_count = cursor.fetchone()[0]

        return proveedores, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

import re

def validate_input(value, field_name, doc_type=None):
    # Validación para Ciudad
    if field_name == 'Ciudad':
        if not value:
            return 'El campo no puede estar vacío.'
        if len(value) < 3 or len(value) > 50:
            return 'El nombre de la ciudad debe tener entre 3 y 50 caracteres.'

    # Validación para Nombre del Proveedor
    if field_name == 'Nombre_del_proveedor':
        if not value:
            return 'El campo no puede estar vacío.'
        if len(value) < 3 or len(value) > 50:
            return 'El nombre del proveedor debe tener entre 3 y 50 caracteres.'

    # Validación para Producto/Servicio
    if field_name == 'Producto_Servicio':
        if not value:
            return 'El campo no puede estar vacío.'
        if len(value) < 3 or len(value) > 100:
            return 'El campo Producto/Servicio debe tener entre 3 y 100 caracteres.'

    # Validación para Historial de Desempeño
    if field_name == 'Historial_de_desempeño':
        if len(value) > 255:
            return 'El historial de desempeño no puede exceder los 255 caracteres.'

    # Validación para Nombre de Compañía
    if field_name == 'nombre_compañia':
        if not value:
            return 'El campo no puede estar vacío.'
        if len(value) < 3 or len(value) > 100:
            return 'El nombre de la compañía debe tener entre 3 y 100 caracteres.'

    # Validación para Teléfono
    if field_name == 'telefono':
        if not value:
            return 'El campo no puede estar vacío.'
        if len(value) != 8 or not value.isdigit():
            return 'El teléfono debe tener exactamente 8 dígitos.'
        if value[0] not in "9382":
            return 'El primer número del Teléfono debe ser 9, 3, 8 o 2.'

    # Validación para Tipo
    if field_name == 'tipo':
        if value not in ['Proveedor', 'Servicio', 'Ambos']:
            return 'El tipo debe ser uno de los siguientes: Proveedor, Servicio, Ambos.'

    # Validación para Documento
    if field_name == 'document':
        if doc_type == 'RTN':
            if len(value) != 14 or not value.isdigit():
                return 'El RTN debe tener exactamente 14 dígitos.'
        elif doc_type == 'DNI':
            if len(value) != 13 or not value.isdigit():
                return 'El Número de Identidad debe tener exactamente 13 dígitos.'
        elif doc_type == 'Pasaporte':
            if not (value.startswith('E') and len(value) == 8 and value[1:].isdigit()):
                return 'El Pasaporte debe comenzar con una E mayúscula seguido de 7 números.'

    return None  # Sin errores



def validate_document(tipo, documento,doc_type=None):
    if tipo == 'DNI':
        return bool(re.match(r'^\d{13}$', documento))
    elif tipo == 'RTN':
        return bool(re.match(r'^\d{14}$', documento))
    elif tipo == 'Pasaporte':
        return bool(re.match(r'^E\d{7}$', documento))
    return False


def format_document(document, doc_type):
    if doc_type == 'DNI':
        return f"{document[:4]}-{document[4:8]}-{document[8:]}"
    elif doc_type == 'RTN':
        return f"{document[:4]}-{document[4:8]}-{document[8:]}"
    return document


def format_document(document, doc_type):
    if doc_type == 'DNI':
        return f"{document[:4]}-{document[4:8]}-{document[8:]}"
    elif doc_type == 'RTN':
        return f"{document[:4]}-{document[4:8]}-{document[8:]}"
    return document

@app_proveedores.route('/')
@check_permission('permiso_proveedor')
def index_proveedores():
    return render_template('index_proveedores.html')

@app_proveedores.route('/proveedores')
@check_permission('permiso_proveedor')
def proveedores():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))  # Obtiene el valor del parámetro 'per_page' o usa 10 por defecto

    if search_criteria and search_query:
        proveedores, total_count = search_users(search_criteria, search_query, page, per_page)
    else:
        proveedores, total_count = get_proveedor(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('proveedores.html', proveedores=proveedores, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_proveedores.route('/submit', methods=['POST'])
@check_permission('permiso_proveedor')
def submit():
    Nombre_del_proveedor = request.form['Nombre_del_proveedor']
    Producto_Servicio = request.form['Producto_Servicio']
    Historial_de_desempeño = request.form['Historial_de_desempeño']
    nombre_compañia = request.form['nombre_compañia']
    Telefono = request.form['Telefono']
    Ciudad = request.form['Ciudad']
    tipo = request.form['Tipo']
    Documento = request.form['Documento']

    # Validaciones
    errors = []
    # Validar campos de texto generales
    for field, field_type in zip([Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Ciudad], ['text']*5):
        error_message = validate_input(field, field_type,doc_type=None)
        if error_message:
            errors.append(error_message)
    
    # Validar teléfono
    error_message = validate_input(Telefono, 'telefono')
    if error_message:
        errors.append(error_message)

    # Validar documento según tipo
    error_message = validate_input(Documento, 'document', tipo)
    if error_message:
        errors.append(error_message)

    if errors:
        flash(' '.join(errors))
        return redirect(url_for('index_proveedores'))

    # Inserta el proveedor en la base de datos
    if insert_user(Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento):
        flash('Proveedor insertado correctamente!')
    else:
        flash('Ocurrió un error al insertar el proveedor.')

    return redirect(url_for('index_proveedores'))



@app_proveedores.route('/edit/<int:id_proveedor>', methods=['GET', 'POST'])
@check_permission('permiso_proveedor')
def edit_proveedores(id_proveedor):
    if request.method == 'POST':
        Nombre_del_proveedor = request.form['Nombre_del_proveedor']
        Producto_Servicio = request.form['Producto_Servicio']
        Historial_de_desempeño = request.form['Historial_de_desempeño']
        nombre_compañia = request.form['nombre_compañia']
        Telefono = request.form['Telefono']
        Ciudad = request.form['Ciudad']
        tipo = request.form['tipo']
        Documento = request.form['Documento']

        # Validaciones
        errors = []
        for field, field_type in zip([Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Ciudad], ['text']*6):
            error_message = validate_input(field, field_type)
            if error_message:
                errors.append(error_message)
        
        if validate_input(Telefono, 'telefono'):
            error_message = validate_input(Telefono, 'telefono')
            if error_message:
                errors.append(error_message)

        if validate_input(Documento, 'document'):
            error_message = validate_input(Documento, 'document')
            if error_message:
                errors.append(error_message)

        if errors:
            flash(' '.join(errors))
            return redirect(url_for('edit_proveedores', id_proveedor=id_proveedor))

        if update_user(id_proveedor, Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento):
            flash('Proveedor actualizado correctamente!')
        else:
            flash('Ocurrió un error al actualizar el proveedor.')
        return redirect(url_for('proveedores'))

    proveedores = get_proveedor_by_id(id_proveedor)
    return render_template('edit_proveedores.html', proveedores=proveedores)

@app_proveedores.route('/eliminar/<int:id_proveedor>', methods=['GET', 'POST'])
@check_permission('permiso_proveedor')
def eliminar_proveedores(id_proveedor):
    if request.method == 'POST':
        if delete_proveedor(id_proveedor):
            flash('Proveedor eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el proveedor.')
        return redirect(url_for('proveedores'))

    proveedor = get_proveedor_by_id(id_proveedor)
    if proveedor is None:
        flash('Proveedor no encontrado!')
        return redirect(url_for('proveedores'))
    
    return render_template('eliminar_proveedores.html', proveedor=proveedor)

@app_proveedores.route('/descargar_excel_proveedores')
@check_permission('permiso_proveedor')
def descargar_excel_proveedores():
    # Obtener todas las proveedores sin paginación
    proveedores = get_todos_proveedores()  # Función para obtener todas las proveedores

    if not proveedores:
        flash('No hay proveedores para descargar.')
        return redirect(url_for('proveedores'))  # Asegúrate de que la ruta 'proveedores' está bien definida

    # Definir las columnas correctas
    columnas = ['id_proveedor', 'Nombre_del_proveedor', 'Producto_Servicio','Historial_de_desempeño', 'nombre_compañia', 'Telefono','Ciudad', 'tipo', 'Documento']

    # Crear un DataFrame con los datos de las proveedores
    df = pd.DataFrame(proveedores, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='proveedores', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['proveedores']
        bold_format = workbook.add_format({'bold': True})


        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de proveedores', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='proveedores.xlsx')

def get_todos_proveedores():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT id_proveedor, Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, 
               nombre_compañia, Telefono, Ciudad, tipo, Documento
        FROM proveedores
    """
    try:
        cursor.execute(query)
        proveedores = cursor.fetchall()
        return proveedores
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_proveedores.route('/descargar_pdf')
@check_permission('permiso_proveedor')
def descargar_pdf():
    # Obtener todos los proveedores y dividir en páginas de 10
    proveedores = get_todos_proveedores()
    paginacion = [proveedores[i:i + 10] for i in range(0, len(proveedores), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    ancho, alto = A3

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primer_nombre = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, proveedores_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Proveedores")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {primer_nombre}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Proveedores
        data = [["ID", "Nombre del Proveedor", "Producto/Servicio", "Historial de Desempeño", 
                 "Nombre Compañía", "Teléfono", "Ciudad", "Tipo", "Documento"]]  # Encabezado de la tabla
        data += [[proveedor[0], proveedor[1], proveedor[2], proveedor[3], proveedor[4], 
                  proveedor[5], proveedor[6], proveedor[7], proveedor[8]] 
                 for proveedor in proveedores_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[0.8 * inch, 1.5 * inch, 1.5 * inch, 1.8 * inch, 1.5 * inch, 
                                       1.2 * inch, 1.2 * inch, 0.8 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Posicionar la tabla en el centro de la página
        table.wrapOn(c, ancho, alto)
        table.drawOn(c, (ancho - table._width) / 2, y - table._height)

        # Pie de página
        total_paginas = len(paginacion)
        c.drawCentredString(ancho / 2, 30, f"Página {pagina} / {total_paginas}")

        # Crear nueva página si hay más datos
        if pagina < len(paginacion):
            c.showPage()

    # Guardar y retornar el PDF
    c.save()
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Proveedores.pdf')



if __name__ == '__main__':
    app_proveedores.run(debug=True,port=5005)