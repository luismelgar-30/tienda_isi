from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash,session
import mysql.connector
import re
from mysql.connector import Error
from datetime import datetime  # Solo importamos la clase datetime
import pandas as pd
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
 

app_mantenimiento = Flask(__name__)
app_mantenimiento.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/mantenimiento'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="mantenimiento", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="mantenimiento"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def mantenimiento_exists(id_mantenimiento):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM mantenimiento WHERE id_mantenimiento = %s"
    cursor.execute(query, (id_mantenimiento,))
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

def get_mantenimientos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM mantenimiento_equipo LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        mantenimientos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_mantenimientos = cursor.fetchone()[0]
        return mantenimientos, total_mantenimientos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_mantenimiento_by_id(id_mantenimiento):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM mantenimiento_equipo WHERE id_mantenimiento = %s"
    try:
        cursor.execute(query, (id_mantenimiento,))
        mantenimiento = cursor.fetchone()
        return mantenimiento
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_mantenimiento(id_equipo, fecha, tipo, detalles, estado, documento):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO mantenimiento_equipo (id_equipo, fecha, tipo, detalles, estado, documento) 
               VALUES (%s, %s, %s, %s, %s, %s)"""
    values = (id_equipo, fecha, tipo, detalles, estado, documento)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Equipo: {id_equipo}, Fecha: {fecha}, Tipo: {tipo}, Detalles: {detalles}, Estado: {estado}, Documento: {documento}"
        log_action('Inserted', screen_name='mantenimiento_equipo', details=details)  # Registro de log
        print("Mantenimiento insertado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_mantenimiento(id_mantenimiento, id_equipo, fecha, tipo, detalles, estado, documento):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """UPDATE mantenimiento_equipo 
               SET id_equipo = %s, fecha = %s, tipo = %s, detalles = %s, estado = %s, documento = %s 
               WHERE id_mantenimiento = %s"""
    values = (id_equipo, fecha, tipo, detalles, estado, documento, id_mantenimiento)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Mantenimiento: {id_mantenimiento}, ID Equipo: {id_equipo}, Fecha: {fecha}, Tipo: {tipo}, Detalles: {detalles}, Estado: {estado}, Documento: {documento}"
        log_action('Updated', screen_name='mantenimiento_equipo', details=details)  # Registro de log
        print("Mantenimiento actualizado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_mantenimiento(id_mantenimiento):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM mantenimiento_equipo WHERE id_mantenimiento = %s"
    
    try:
        cursor.execute(query, (id_mantenimiento,))
        connection.commit()
        details = f"ID Mantenimiento: {id_mantenimiento}"
        log_action('Deleted', screen_name='mantenimiento_equipo', details=details)  # Registro de log
        print("Mantenimiento eliminado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def search_mantenimientos_by_field(field, value, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = f"""
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM mantenimiento_equipo 
    WHERE {field} = %s
    LIMIT %s OFFSET %s
    """
    values = (value, per_page, offset)
    try:
        cursor.execute(query, values)
        mantenimientos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_mantenimientos = cursor.fetchone()[0]
        return mantenimientos, total_mantenimientos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_mantenimientos(search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    
    query = """
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM mantenimiento_equipo 
    WHERE id_equipo LIKE %s 
       OR tipo LIKE %s 
       OR detalles LIKE %s 
       OR estado LIKE %s 
       OR fecha LIKE %s
    LIMIT %s OFFSET %s
    """
    values = (
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        per_page, 
        offset
    )
    try:
        cursor.execute(query, values)
        mantenimientos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_mantenimientos = cursor.fetchone()[0]
        return mantenimientos, total_mantenimientos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def validate_text_field(text, field_name, min_length=3, max_length=40):
    if not text or len(text) < min_length or len(text) > max_length:
        return f"{field_name} debe tener entre {min_length} y {max_length} caracteres."
    return None


def validate_numeric_field(value, field_name):
    if not value.isdigit():
        return f'{field_name} debe ser un número entero.'
    return None

def validate_date_field(value, field_name):
    try:
        date_format = '%Y-%m-%d'
        datetime.strptime(value, date_format)
    except ValueError:
        return f'{field_name} debe estar en el formato YYYY-MM-DD.'
    return None

@app_mantenimiento.route('/')
@check_permission('permiso_mantenimiento')
def index_mantenimiento():
    return render_template('index_mantenimiento.html')

@app_mantenimiento.route('/mantenimientos')
@check_permission('permiso_mantenimiento')
def mantenimientos():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    if search_query:
        if ':' in search_query:
            search_field, search_value = search_query.split(':', 1)
            if search_field in ["id_equipo", "tipo", "detalles", "estado", "fecha"]:
                mantenimientos, total_mantenimientos = search_mantenimientos_by_field(search_field, search_value, page, per_page)
            else:
                mantenimientos, total_mantenimientos = search_mantenimientos(search_value, page, per_page)
        else:
            mantenimientos, total_mantenimientos = search_mantenimientos(search_query, page, per_page)
    else:
        mantenimientos, total_mantenimientos = get_mantenimientos(page, per_page)

    total_pages = (total_mantenimientos + per_page - 1) // per_page
    return render_template('mantenimientos.html', mantenimientos=mantenimientos, search_query=search_query, page=page, per_page=per_page, total_mantenimientos=total_mantenimientos, total_pages=total_pages)

@app_mantenimiento.route('/submit', methods=['POST'])
@check_permission('permiso_mantenimiento')
def submit():
    id_equipo = request.form['id_equipo']
    fecha = request.form['fecha']
    tipo = request.form['tipo']
    detalles = request.form['detalles']
    estado = request.form['estado']
    documento = request.form['documento']

    error_message = None
    error_message = validate_text_field(id_equipo, 'ID Equipo')
    if error_message is None:
        error_message = validate_date_field(fecha, 'Fecha')
    if error_message is None:
        error_message = validate_text_field(tipo, 'Tipo')
    if error_message is None:
        error_message = validate_text_field(detalles, 'Detalles')
    if error_message is None:
        error_message = validate_text_field(estado, 'Estado')
    if error_message is None:
        error_message = validate_text_field(documento, 'Documento')

    if error_message:
        flash(error_message)
        return redirect(url_for('index_mantenimiento'))

    if insert_mantenimiento(id_equipo, fecha, tipo, detalles, estado, documento):
        flash('Mantenimiento insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el mantenimiento.')
    
    return redirect(url_for('mantenimientos'))

@app_mantenimiento.route('/edit/<int:id_mantenimiento>', methods=['GET', 'POST'])
@check_permission('permiso_mantenimiento')
def edit_mantenimiento(id_mantenimiento):
    if request.method == 'POST':
        # Recoger los valores del formulario
        id_equipo = request.form.get('id_equipo')
        fecha = request.form.get('fecha')
        tipo = request.form.get('tipo')
        detalles = request.form.get('detalles')
        estado = request.form.get('estado')
        documento = request.form.get('documento')

        # Imprimir los valores recogidos para depuración
        print(f"Datos del formulario: id_equipo={id_equipo}, fecha={fecha}, tipo={tipo}, detalles={detalles}, estado={estado}, documento={documento}")
        flash(f"Datos recibidos: ID equipo: {id_equipo}, Fecha: {fecha}, Tipo: {tipo}, Detalles: {detalles}, Estado: {estado}, Documento: {documento}")

        # Validaciones (ajustadas)
        error_message = None
        if not id_equipo:
            error_message = 'El campo ID Equipo es obligatorio.'  # Elimina la validación de números
        
        if error_message is None:
            error_message = validate_date_field(fecha, 'Fecha')
        if error_message is None:
            error_message = validate_text_field(tipo, 'Tipo')
        if error_message is None:
            error_message = validate_text_field(detalles, 'Detalles')
        if error_message is None:
            error_message = validate_text_field(estado, 'Estado')
        if error_message is None:
            error_message = validate_text_field(documento, 'Documento')

        if error_message:
            flash(f"Error de validación: {error_message}")
            print(f"Error de validación: {error_message}")  # Mensaje de depuración
            return redirect(url_for('edit_mantenimiento', id_mantenimiento=id_mantenimiento))

        # Si no hay errores, intentamos actualizar el mantenimiento
        print("Validación exitosa, intentando actualizar...")
        if update_mantenimiento(id_mantenimiento, id_equipo, fecha, tipo, detalles, estado, documento):
            flash('Mantenimiento actualizado exitosamente!')
            print("Actualización exitosa")
        else:
            flash('Ocurrió un error al actualizar el mantenimiento.')
            print("Error al intentar actualizar el mantenimiento")

        return redirect(url_for('mantenimientos'))

    # Obtener los datos del mantenimiento actual
    mantenimiento = get_mantenimiento_by_id(id_mantenimiento)
    if mantenimiento is None:
        flash('Mantenimiento no encontrado.')
        print(f"Mantenimiento con ID {id_mantenimiento} no encontrado")  # Mensaje de depuración
        return redirect(url_for('mantenimientos'))

    print(f"Mantenimiento encontrado: {mantenimiento}")  # Mensaje de depuración
    return render_template('edit_mantenimiento.html', mantenimiento=mantenimiento)


@app_mantenimiento.route('/delete_mantenimiento/<int:id_mantenimiento>', methods=['GET', 'POST'])
@check_permission('permiso_mantenimiento')
def eliminar_mantenimiento(id_mantenimiento):
    # Verificar si el método es POST
    if request.method == 'POST':
        if delete_mantenimiento(id_mantenimiento):  # Asegúrate de tener una función delete_mantenimiento() definida
            flash('Mantenimiento eliminado exitosamente.')
        else:
            flash('Error al eliminar el mantenimiento.')
        return redirect(url_for('mantenimientos'))

    # Si el método no es POST, verificar si el mantenimiento existe
    mantenimiento = get_mantenimiento_by_id(id_mantenimiento)  # Asegúrate de tener una función get_mantenimiento_by_id() definida
    if mantenimiento is None:
        flash('Mantenimiento no encontrado.')
        return redirect(url_for('mantenimientos'))

    return render_template('eliminar_mantenimiento.html', mantenimiento=mantenimiento)

@app_mantenimiento.route('/export_mantenimiento', methods=['GET'])
@check_permission('permiso_mantenimiento')
def export_mantenimiento():
    # Obtener todas las mantenimiento sin paginación
    mantenimiento = get_todos_mantenimientos()  # Función para obtener todas las mantenimiento

    if not mantenimiento:
        flash('No hay mantenimiento para descargar.')
        return redirect(url_for('mantenimiento'))  # Asegúrate de que la ruta 'mantenimiento' está bien definida

    # Definir las columnas correctas
    columnas=['id_mantenimiento', 'id_equipo', 'fecha', 'tipo', 'detalles', 'estado', 'documento']

    # Crear un DataFrame con los datos de las mantenimiento
    df = pd.DataFrame(mantenimiento, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='mantenimiento', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['mantenimiento']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de mantenimiento', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='mantenimiento.xlsx')

def get_todos_mantenimientos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = "SELECT id_mantenimiento, id_equipo, fecha, tipo, detalles, estado, documento FROM mantenimiento_equipo"
    try:
        cursor.execute(query)
        mantenimientos = cursor.fetchall()
        return mantenimientos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_mantenimiento.route('/descargar_pdf')
@check_permission('permiso_mantenimiento')
def descargar_pdf():
    # Obtener todos los registros de mantenimiento y dividir en páginas de 10
    mantenimientos = get_todos_mantenimientos()
    paginacion = [mantenimientos[i:i + 10] for i in range(0, len(mantenimientos), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    ancho, alto = landscape(A4)

    # Ruta del logo
    logo_path = "static/logo.png" 
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, mantenimientos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Mantenimiento de Equipos")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Mantenimientos
        data = [["ID", "ID Equipo", "Fecha", "Tipo", "Detalles", "Estado", "Documento"]]  # Encabezado de la tabla
        data += [[mant[0], mant[1], mant[2], mant[3], mant[4], mant[5], mant[6]] for mant in mantenimientos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 1 * inch, 1.3 * inch, 1.5 * inch, 2 * inch, 1 * inch, 1.3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Mantenimiento_Equipos.pdf')



if __name__ == '__main__':
    app_mantenimiento.run(debug=True,port=5031)
