import datetime
from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import pandas as pd

app_sucursales = Flask(__name__)
app_sucursales.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/sucursales'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="sucursales", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

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

def log_error(error_message, screen_name="sucursales"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def sucursales_exists(id_sucursal):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM sucursales WHERE id_sucursal = %s"
    cursor.execute(query, (id_sucursal,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

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

def format_telefono(telefono):
    cleaned_phone = re.sub(r'[^0-9-]', '', telefono)
    parts = cleaned_phone.split('-')
    
    if len(parts) == 1:
        if len(parts[0]) == 8:
            return f"{parts[0][:4]}-{parts[0][4:]}"
        return cleaned_phone
    
    elif len(parts) == 2:
        if len(parts[0]) == 4 and len(parts[1]) == 4:
            return f"{parts[0]}-{parts[1]}"
    
    return cleaned_phone

def contains_two_vowels_consecutive(text):
    vowels = "aeiouáéíóú"
    for i in range(len(text) - 1):
        if text[i].lower() in vowels and text[i] == text[i + 1]:
            return True
    return False


def insert_sucursal(ciudad, telefono):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return "error", None

    cursor = connection.cursor()
    errors = []
  
    # Validaciones para el campo "ciudad"
    if not ciudad:
        errors.append('¡Todos los campos obligatorios deben ser completados!')
    elif len(ciudad) < 3:
        errors.append('La ciudad debe tener al menos 3 caracteres.')
    elif any(char.isdigit() for char in ciudad):
        errors.append('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.')
    elif re.search(r'(.)\1\1', ciudad):  # Tres letras repetidas
        errors.append('La ciudad no puede tener más de dos letras iguales consecutivas.')
    elif re.search(r'[!@#$%^&*(),.?":{}|<>]', ciudad):  # Caracteres especiales
        errors.append('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.')
    elif contains_two_vowels_consecutive(ciudad):
        errors.append("La ciudad no puede tener dos vocales iguales consecutivas.")

    # Validación de existencia de ciudad en la base de datos
    query_ciudad = "SELECT COUNT(*) FROM sucursales WHERE ciudad = %s"
    cursor.execute(query_ciudad, (ciudad,))
    if cursor.fetchone()[0] > 0:
        errors.append("ciudad_exists")

    # Validaciones para el campo "telefono"
    formatted_telefono = format_telefono(telefono)
    
    if not re.match(r'^\d{4}-\d{4}$', telefono):
        errors.append("El teléfono contiene caracteres no permitidos. Solo se permiten números y un guión en el formato xxxx-xxxx.")

    # Validación de existencia de teléfono en la base de datos
    query_telefono = "SELECT COUNT(*) FROM sucursales WHERE telefono = %s"
    cursor.execute(query_telefono, (formatted_telefono,))
    if cursor.fetchone()[0] > 0:
        errors.append("telefono_exists")

    # Si hay errores, retornamos los errores
    if errors:
        cursor.close()
        connection.close()
        return "error", errors

    # Inserción en la base de datos si no hay errores
    query_insert = "INSERT INTO sucursales (ciudad, telefono) VALUES (%s, %s)"
    values = (ciudad, formatted_telefono)
    try:
        cursor.execute(query_insert, values)
        connection.commit()
        details = f"Ciudad: {ciudad}, Teléfono: {formatted_telefono}"
        log_action('Inserted', screen_name='sucursales', details=details)  # Registro de log
        return "success", None
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return "error", ["database_error"]
    finally:
        cursor.close()
        connection.close()

def update_sucursal(id_sucursal, ciudad, telefono):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    formatted_telefono = format_telefono(telefono)
    query = """UPDATE sucursales SET ciudad = %s, telefono = %s WHERE id_sucursal = %s"""
    values = (ciudad, formatted_telefono, id_sucursal)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Sucursal: {id_sucursal}, Ciudad: {ciudad}, Teléfono: {formatted_telefono}"
        log_action('Updated', screen_name='sucursales', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_sucursal(id_sucursal):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM sucursales WHERE id_sucursal = %s"
    try:
        cursor.execute(query, (id_sucursal,))
        connection.commit()
        details = f"ID Sucursal: {id_sucursal}"
        log_action('Deleted', screen_name='sucursales', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def get_sucursales(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS id_sucursal, ciudad, telefono FROM sucursales LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        sucursales = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_sucursales = cursor.fetchone()[0]
        return sucursales, total_sucursales
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_sucursales(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"SELECT SQL_CALC_FOUND_ROWS * FROM sucursales WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        sucursales = cursor.fetchall()
        cursor.execute(f"SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return sucursales, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_sucursal_by_id(id_sucursal):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT id_sucursal, ciudad, telefono FROM sucursales WHERE id_sucursal = %s"
    cursor.execute(query, (id_sucursal,))
    sucursal = cursor.fetchone()
    cursor.close()
    connection.close()
    return sucursal

VALID_CIUDAD_REGEX = re.compile(r'^[a-zA-Z\s]+$')  # Only letters and spaces
VALID_TELEFONO_REGEX = re.compile(r'^\d{4}-\d{4}$|^\d{8}$')  # Allows 1234-5678 or 12345678

@app_sucursales.route('/')
@check_permission('permiso_sucursal')
def index_sucursales():
    return render_template('index_sucursales.html')

@app_sucursales.route('/sucursales')
@check_permission('permiso_sucursal')
def sucursales():
    search_criteria = request.args.get('search_criteria', 'ciudad')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    if search_query:
        sucursales, total_count = search_sucursales(search_criteria, search_query, page, per_page)
    else:
        sucursales, total_count = get_sucursales(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('sucursales.html', sucursales=sucursales, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_sucursales.route('/submit', methods=['POST'])
@check_permission('permiso_sucursal')
def submit():
    ciudad = request.form.get('ciudad')
    telefono = request.form.get('telefono')

    errors = []

    if not ciudad or not telefono:
        errors.append('¡Todos los campos obligatorios deben ser completados!')
    else:
        if not VALID_CIUDAD_REGEX.match(ciudad):
            errors.append('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.')

        if not VALID_TELEFONO_REGEX.match(telefono):
            errors.append('El teléfono contiene caracteres no permitidos. Solo se permiten números y un guión en el formato xxxx-xxxx.')

    if not errors:
        result, db_errors = insert_sucursal(ciudad, telefono)
        if result == "success":
            flash('¡Sucursal ingresada exitosamente!')
        elif db_errors:
            for db_error in db_errors:
                if db_error == "telefono_exists":
                    errors.append('El teléfono ya está registrado en otra sucursal. Por favor, ingrese uno nuevo.')
                elif db_error == "ciudad_exists":
                    errors.append('La ciudad ya está registrada en otra sucursal. Por favor, ingrese una nueva.')
                elif db_error == "database_error":
                    errors.append('Ocurrió un error al ingresar la sucursal. Por favor, intente nuevamente.')
        else:
            errors.append('Ocurrió un error al ingresar la sucursal. Por favor, intente nuevamente.')

    for error in errors:
        flash(error)
    return redirect(url_for('index_sucursales'))

@app_sucursales.route('/edit_sucursal/<int:id_sucursal>', methods=['GET', 'POST'])
@check_permission('permiso_sucursal')
def edit_sucursal(id_sucursal):
    if request.method == 'POST':
        ciudad = request.form.get('ciudad')
        telefono = request.form.get('telefono')

        errors = []

        if not ciudad or not telefono:
            errors.append('¡Todos los campos obligatorios deben ser completados!')
        else:
            if not VALID_CIUDAD_REGEX.match(ciudad):
                errors.append('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.')

            if not VALID_TELEFONO_REGEX.match(telefono):
                errors.append('El teléfono contiene caracteres no permitidos. Solo se permiten números y un guión en el formato xxxx-xxxx.')

        if not errors:
            if update_sucursal(id_sucursal, ciudad, telefono):
                flash('¡Sucursal actualizada exitosamente!')
                return redirect(url_for('sucursales'))
            else:
                flash('Ocurrió un error al actualizar la sucursal. Por favor, intente nuevamente.')
        else:
            for error in errors:
                flash(error)

    sucursal = get_sucursal_by_id(id_sucursal)
    return render_template('edit_sucursales.html', sucursal=sucursal)


@app_sucursales.route('/eliminar_sucursales/<int:id_sucursal>', methods=['GET', 'POST'])
@check_permission('permiso_sucursal')
def eliminar_sucursal(id_sucursal):
    if request.method == 'POST':
        if delete_sucursal(id_sucursal):
            flash('¡Sucursal eliminada exitosamente!')
            return redirect(url_for('sucursales'))
        else:
            flash('Ocurrió un error al eliminar la sucursal. Por favor, intente nuevamente.')
            return redirect(url_for('sucursales'))

    sucursal = get_sucursal_by_id(id_sucursal)
    if sucursal is None:
        flash('Sucursal no encontrada.')
        return redirect(url_for('sucursales'))

    return render_template('eliminar_sucursales.html', sucursal=sucursal)

@app_sucursales.route('/descargar_excel')
@check_permission('permiso_sucursal')
def descargar_excel():
    # Obtener todas las sucursales sin paginación
    sucursales = get_todas_sucursales()  # Función para obtener todas las sucursales

    if not sucursales:
        flash('No hay sucursales para descargar.')
        return redirect(url_for('sucursales'))  # Asegúrate de que la ruta 'sucursales' está bien definida

    # Definir las columnas correctas
    columnas = ['id_sucursal', 'ciudad', 'telefono']

    # Crear un DataFrame con los datos de las sucursales
    df = pd.DataFrame(sucursales, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='sucursales', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['sucursales']
        bold_format = workbook.add_format({'bold': True})


        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de sucursales', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='sucursales.xlsx')


# Nueva función para obtener todas las sucursales sin límites
def get_todas_sucursales():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'sucursales'
    query = "SELECT id_sucursal, ciudad, telefono FROM sucursales"

    try:
        cursor.execute(query)
        sucursales = cursor.fetchall()  # Obtener todas las filas
        return sucursales
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_todas_sucursales():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT id_sucursal, Ciudad, Telefono
        FROM sucursales
    """
    try:
        cursor.execute(query)
        sucursales = cursor.fetchall()
        return sucursales
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_sucursales.route('/descargar_pdf')
@check_permission('permiso_sucursal')
def descargar_pdf():
    # Obtener todas las sucursales y dividir en páginas de 10
    sucursales = get_todas_sucursales()
    paginacion = [sucursales[i:i + 10] for i in range(0, len(sucursales), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, sucursales_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Sucursales")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Sucursales
        data = [["ID", "Ciudad", "Teléfono"]]  # Encabezado de la tabla
        data += [[sucursal[0], sucursal[1], sucursal[2]] for sucursal in sucursales_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1.5 * inch, 3 * inch, 2.5 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Sucursales.pdf')


if __name__ == '__main__':
    app_sucursales.run(debug=True, port=5008)
