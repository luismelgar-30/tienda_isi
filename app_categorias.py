import datetime
from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import pandas as pd

app_categorias = Flask(__name__)
app_categorias.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/categorias'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="categorias", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="categorias"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def categoria_exists(nombre_categoria):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM categorias WHERE nombre_categoria = %s"
    cursor.execute(query, (nombre_categoria,))
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

def get_categorias(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT * FROM categorias LIMIT %s OFFSET %s"
    
    try:
        # Execute the main query to fetch categories with pagination
        cursor.execute(query, (per_page, offset))
        categorias = cursor.fetchall()

        # Execute the query to count total categories
        cursor.execute("SELECT COUNT(*) FROM categorias")
        total_count = cursor.fetchone()[0]

        return categorias, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_categoria_by_id(id_categoria):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM categorias WHERE id_categoria = %s"
    try:
        cursor.execute(query, (id_categoria,))
        categoria = cursor.fetchone()
        return categoria
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_categoria(nombre_categoria, descripcion):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "INSERT INTO categorias (nombre_categoria, descripcion) VALUES (%s, %s)"
    values = (nombre_categoria, descripcion)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la inserción
        details = f"Nombre: {nombre_categoria}, Descripción: {descripcion}"
        log_action('Inserted', screen_name='categorias', details=details)  # Registro de la acción de inserción

        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_categoria(id_categoria, nombre_categoria, descripcion):   
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE categorias
    SET nombre_categoria = %s, descripcion = %s
    WHERE id_categoria = %s
    """
    values = (nombre_categoria, descripcion, id_categoria)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"ID: {id_categoria}, Nombre: {nombre_categoria}, Descripción: {descripcion}"
        log_action('Updated', screen_name='categorias', details=details)  # Registro de la acción de actualización

        print(f"Updated {cursor.rowcount} rows")  # Debugging line
        return True
    except Error as e:
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_categoria(id_categoria):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    # Obtener detalles de la categoría antes de eliminar para el log
    cursor.execute("SELECT nombre_categoria, descripcion FROM categorias WHERE id_categoria = %s", (id_categoria,))
    categoria = cursor.fetchone()
    
    if not categoria:
        print("Categoría no encontrada")
        return False

    nombre_categoria, descripcion = categoria
    query = "DELETE FROM categorias WHERE id_categoria = %s"
    try:
        cursor.execute(query, (id_categoria,))
        connection.commit()

        # Registro en logs después de la eliminación
        details = f"ID: {id_categoria}, Nombre: {nombre_categoria}, Descripción: {descripcion}"
        log_action('Deleted', screen_name='categorias', details=details)  # Registro de la acción de eliminación

        return True
    except Exception as e:  # Catching general exceptions can be more appropriate here
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def search_categorias(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    if search_criteria not in ['nombre_categoria', 'Descripcion']:
        search_criteria = 'nombre_categoria'

    query = f"SELECT * FROM categorias WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    
    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        categorias = cursor.fetchall()

        cursor.execute(f"SELECT COUNT(*) FROM categorias WHERE {search_criteria} LIKE %s", (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return categorias, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def validate_input(field_value, field_type='text'):
    if not field_value:
        return "El campo no puede estar vacío."
    
    if field_type == 'text':
        if len(field_value) < 3:
            return "No se permiten menos de tres letras."
        if re.search(r'(.)\1{2,}', field_value):
            return "No se permiten más de tres letras seguidas."
        if re.search(r'\d', field_value):
            return "No se permiten números en este campo."
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', field_value):
            return "No se permiten símbolos en este campo."
       
    return None

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



@app_categorias.route('/')
@check_permission('permiso_categoria')
def index_categorias():
    return render_template('index_categorias.html')

@app_categorias.route('/categorias')
@check_permission('permiso_categoria')
def categorias():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if search_criteria and search_query:
        categorias, total_count = search_categorias(search_criteria, search_query, page, per_page)
    else:
        categorias, total_count = get_categorias(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('categorias.html', categorias=categorias, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_categorias.route('/submit', methods=['POST'])
@check_permission('permiso_categoria')
def submit_categoria():
    nombre_categoria = request.form.get('nombre_categoria')
    descripcion = request.form.get('Descripcion')

    # Validaciones
    nombre_error = validate_input(nombre_categoria)
    descripcion_error = validate_input(descripcion)

    if nombre_error or descripcion_error:
        if nombre_error:
            flash(nombre_error)
        if descripcion_error:
            flash(descripcion_error)
        return redirect(url_for('index_categorias'))

    # Inserta la categoría en la base de datos
    if insert_categoria(nombre_categoria, descripcion):
        flash('Categoría insertada correctamente!')
    else:
        flash('Ocurrió un error al insertar la categoría.')

    return redirect(url_for('index_categorias'))

@app_categorias.route('/edit_categoria/<int:id_categoria>', methods=['GET', 'POST'])
@check_permission('permiso_categoria')
def edit_categoria(id_categoria):
    if request.method == 'POST':
        nombre_categoria = request.form.get('nombre_categoria')
        descripcion = request.form.get('Descripcion')

        # Validaciones
        nombre_error = validate_input(nombre_categoria)
        descripcion_error = validate_input(descripcion)

        if nombre_error or descripcion_error:
            if nombre_error:
                flash(nombre_error)
            if descripcion_error:
                flash(descripcion_error)
            return redirect(url_for('edit_categoria', id_categoria=id_categoria))

        if update_categoria(id_categoria, nombre_categoria, descripcion):
            flash('Categoría actualizada correctamente!')
        else:
            flash('Error al actualizar la categoría.')
        return redirect(url_for('categorias'))
    
    categoria = get_categoria_by_id(id_categoria)
    return render_template('edit_categoria.html', categoria=categoria)

@app_categorias.route('/eliminar/<int:id_categoria>', methods=['GET', 'POST'])
@check_permission('permiso_categoria')
def eliminar_categoria(id_categoria):
    if request.method == 'POST':
        if delete_categoria(id_categoria):
            flash('Categoría eliminada exitosamente!')
        else:
            flash('Ocurrió un error al eliminar la categoría.')
        return redirect(url_for('categorias'))

    categoria = get_categoria_by_id(id_categoria)
    if categoria is None:
        flash('Categoría no encontrada!')
        return redirect(url_for('categorias'))
    
    return render_template('eliminar_categoria.html', categoria=categoria)

@app_categorias.route('/descargar_excel')
@check_permission('permiso_categoria')
def descargar_excel():
    # Obtener todas las categorías sin paginación
    categoria = get_todas_categorias()  # Función para obtener todas las categorías

    if not categoria:
        flash('No hay categorías para descargar.')
        return redirect(url_for('categoria'))  # Asegúrate de que la ruta 'categoria' está bien definida

    # Definir las columnas correctas
    columnas = ['id_categoria', 'nombre_categoria', 'Descripcion']

    # Crear un DataFrame con los datos de las categorías
    df = pd.DataFrame(categoria, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='categorias', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['categorias']
        bold_format = workbook.add_format({'bold': True})


        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de categorías', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='categorias.xlsx')


# Nueva función para obtener todas las categorías sin límites
def get_todas_categorias():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'categorias'
    query = "SELECT id_categoria, nombre_categoria, Descripcion FROM categorias"

    try:
        cursor.execute(query)
        categorias = cursor.fetchall()  # Obtener todas las filas
        return categorias
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

@app_categorias.route('/descargar_pdf')
@check_permission('permiso_categoria')
def descargar_pdf():
    # Obtener todas las categorías y dividir en páginas de 10
    categorias = get_todas_categorias()
    paginacion = [categorias[i:i + 10] for i in range(0, len(categorias), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, categorias_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Categorías")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Categorías
        data = [["ID Categoría", "Nombre", "Descripción"]]  # Encabezado de la tabla
        data += [[record[0], record[1], record[2]] for record in categorias_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 2 * inch, 4 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Categorias.pdf')



if __name__ == '__main__':
    app_categorias.run(debug=True, port=5009)
