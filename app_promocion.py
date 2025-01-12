import datetime
from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import re
import pandas as pd

app_promocion = Flask(__name__)
app_promocion.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/promocion'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="promocion", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="promocion"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")


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


def promocion_exists(id_promocion):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM promocion WHERE id_promocion = %s"
    cursor.execute(query, (id_promocion,))
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

def validate_promotion(nombre, valor):
    regexNoTresRepetidas = re.compile(r'(.)\1\1')
    regexNoLetrasEnNumero = re.compile(r'[a-zA-Z]')
    
    if regexNoTresRepetidas.search(nombre):
        return "No se permiten tres letras repetidas consecutivas."

    if regexNoLetrasEnNumero.search(valor):
        return "No se permiten letras en el campo de valor."

    return None

def get_promocion(limit, offset, filter_by=None, filter_value=None):
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()

    query = "SELECT * FROM promocion"
    params = []

    # Aplicar el filtro si está presente
    if filter_by and filter_value:
        query += f" WHERE {filter_by} LIKE %s"
        params.append(f"%{filter_value}%")

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        cursor.execute(query, tuple(params))
        promociones = cursor.fetchall()
        return promociones
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()


def get_promocion_count():
    connection = create_connection()
    if connection is None:
        return 0
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM promocion"
    try:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        return count
    except Error as e:
        print(f"The error '{e}' occurred")
        return 0
    finally:
        cursor.close()
        connection.close()

def get_promocion_by_id(id_promocion):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM promocion WHERE id_promocion = %s"
    try:
        cursor.execute(query, (id_promocion,))
        promocion = cursor.fetchone()
        return promocion
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_promocion(nombre, valor):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()
    query = """INSERT INTO promocion (nombre, valor)
               VALUES (%s, %s)"""
    values = (nombre, valor)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre: {nombre}, Valor: {valor}"
        log_action('Inserted', screen_name='promocion', details=details)  # Registro de log
        print("Promoción insertada exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def update_promocion(id_promocion, nombre, valor):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()
    query = """UPDATE promocion SET nombre = %s, valor = %s 
                WHERE id_promocion = %s"""
    values = (nombre, valor, id_promocion)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Promoción: {id_promocion}, Nombre: {nombre}, Valor: {valor}"
        log_action('Updated', screen_name='promocion', details=details)  # Registro de log
        print("Promoción actualizada exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def delete_promocion(id_promocion):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor()
    query = "DELETE FROM promocion WHERE id_promocion = %s"
    
    try:
        cursor.execute(query, (id_promocion,))
        connection.commit()
        details = f"ID Promoción: {id_promocion}"
        log_action('Deleted', screen_name='promocion', details=details)  # Registro de log
        print("Promoción eliminada exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

@app_promocion.route('/')
@check_permission('permiso_promocion')
def index_promocion():
    return render_template('index_promocion.html')

@app_promocion.route('/promocion', methods=['GET'])
@check_permission('permiso_promocion')
def promocion():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    filter_by = request.args.get('filter_by', None)
    filter_value = request.args.get('filter_value', None)

    promociones = get_promocion(per_page, (page - 1) * per_page, filter_by, filter_value)
    total_promociones = get_promocion_count()

    total_pages = (total_promociones + per_page - 1) // per_page

    return render_template('promocion.html', 
                           promociones=promociones, 
                           total_pages=total_pages, 
                           current_page=page, 
                           per_page=per_page, 
                           filter_by=filter_by, 
                           filter_value=filter_value)


@app_promocion.route('/promocion/agregar', methods=['GET', 'POST'])
@check_permission('permiso_promocion')
def agregar_promocion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        valor = request.form['valor']
        
        error = validate_promotion(nombre, valor)
        if error:
            flash(error)
            return redirect(url_for('agregar_promocion'))
        
        if insert_promocion(nombre, valor):
            flash("Promoción agregada con éxito")
        else:
            flash("Error al agregar la promoción")

        return redirect(url_for('promocion'))
    return render_template('agregar_promocion.html')

@app_promocion.route('/promocion/editar/<int:id_promocion>', methods=['GET', 'POST'])
@check_permission('permiso_promocion')
def editar_promocion(id_promocion):
    promocion = get_promocion_by_id(id_promocion)
    if not promocion:
        flash("Promoción no encontrada")
        return redirect(url_for('promocion'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()  # Elimina espacios en blanco
        valor = request.form.get('valor', '').strip()
        
        error = validate_promotion(nombre, valor)
        if error:
            flash(error)
            return redirect(url_for('editar_promocion', id_promocion=id_promocion))

        if update_promocion(id_promocion, nombre, valor):
            flash("Promoción actualizada con éxito")
        else:
            flash("Error al actualizar la promoción")

        return redirect(url_for('promocion'))

    return render_template('edit_promocion.html', promocion=promocion)

@app_promocion.route('/promocion/eliminar/<int:id_promocion>', methods=['GET', 'POST'])
@check_permission('permiso_promocion')
def eliminar_promocion(id_promocion):
    if request.method == 'POST':
        if delete_promocion(id_promocion):
            flash('¡Promoción eliminada exitosamente!')
            return redirect(url_for('promocion'))
        else:
            flash('Ocurrió un error al eliminar la promoción. Por favor, intente nuevamente.')

    promocion = get_promocion_by_id(id_promocion)
    if promocion is None:
        flash('Promoción no encontrada.')
        return redirect(url_for('promocion'))

    return render_template('eliminar_promocion.html', promocion=promocion)

@app_promocion.route('/descargar_excel')
@check_permission('permiso_promocion')
def descargar_excel():
    # Obtener todas las promocion sin paginación
    promocion = get_todas_promociones()  # Función para obtener todas las promocion

    if not promocion:
        flash('No hay promocion para descargar.')
        return redirect(url_for('promocion'))  # Asegúrate de que la ruta 'promocion' está bien definida

    # Definir las columnas correctas
    columnas = ['id_promocion',' nombre',' valor']

    # Crear un DataFrame con los datos de las promocion
    df = pd.DataFrame(promocion, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='promocion', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['promocion']

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de Descuentos')
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='Descuento.xlsx')


# Nueva función para obtener todas las promocion sin límites
def get_todas_promociones():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'promocion'
    query = "SELECT id_promocion, nombre, valor FROM promocion"

    try:
        cursor.execute(query)
        promocion = cursor.fetchall()  # Obtener todas las filas
        return promocion
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

@app_promocion.route('/descargar_pdf')
@check_permission('permiso_promocion')
def descargar_pdf():
    # Obtener todas las promociones y dividir en páginas de 10
    promociones = get_todas_promociones()
    paginacion = [promociones[i:i + 10] for i in range(0, len(promociones), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, promociones in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Descuentos")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Promociones
        data = [["ID", "Nombre", "Valor"]]  # Encabezado de la tabla
        data += [[promocion[0], promocion[1], promocion[2]] for promocion in promociones]  # Datos de promociones

        # Configuración de la tabla
        table = Table(data, colWidths=[1.5 * inch, 3 * inch, 2 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Descuentos.pdf')


if __name__ == "__main__":
    app_promocion.run(debug=True, port=5014)
