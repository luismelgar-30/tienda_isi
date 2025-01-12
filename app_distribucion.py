from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import pandas as pd

app_distribucion = Flask(__name__)
app_distribucion.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/distribucion'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="distribucion", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="distribucion"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def distribucion_exists(id_distribucion):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM distribucion_almacenes WHERE id_distribucion = %s"
    cursor.execute(query, (id_distribucion,))
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

def validate_text_field(field_value, field_name):
    if not 3 <= len(field_value) <= 20:
        return f"El campo {field_name} debe tener entre 3 y 20 caracteres."
    if re.search(r'\d', field_value):
        return f"El campo {field_name} no puede contener números."
    if re.search(r'[^a-zA-Z]', field_value):
        return f"El campo {field_name} no puede contener caracteres especiales."
    if re.search(r'(.)\1\1', field_value):
        return f"El campo {field_name} no puede contener tres letras repetidas consecutivas."
    return None

def validate_numeric_field(field_value, field_name):
    if not field_value.isdigit():
        return f"El campo {field_name} solo puede contener números."
    return None

def validate_date_field(date_value, field_name):
    try:
        date_obj = datetime.strptime(date_value, '%Y-%m-%d')
        if date_obj < datetime.now():
            return f"El campo {field_name} no puede ser una fecha anterior a la actual."
    except ValueError:
        return f"El campo {field_name} debe ser una fecha válida."
    return None

def get_distribuciones(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
    SELECT SQL_CALC_FOUND_ROWS d.id_distribucion, ao.nombre AS almacen_origen, ad.nombre AS almacen_destino, 
           p.nombre AS nombre_producto, d.cantidad, d.fecha
    FROM distribucion_almacenes d
    JOIN almacenes ao ON d.id_almacenes_origen = ao.id_almacenes
    JOIN almacenes ad ON d.id_almacenes_destino = ad.id_almacenes
    JOIN producto p ON d.id_producto = p.id_producto
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (per_page, offset))
        distribuciones = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_distribuciones = cursor.fetchone()[0]
        return distribuciones, total_distribuciones
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_distribucion_by_id(id_distribucion):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM distribucion_almacenes WHERE id_distribucion = %s"
    try:
        cursor.execute(query, (id_distribucion,))
        distribucion = cursor.fetchone()
        return distribucion
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()


def search_distribuciones(search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
    SELECT SQL_CALC_FOUND_ROWS d.id_distribucion, ao.nombre AS almacen_origen, ad.nombre AS almacen_destino, 
           p.nombre AS nombre_producto, d.cantidad, d.fecha
    FROM distribucion_almacenes d
    JOIN almacenes ao ON d.id_almacenes_origen = ao.id_almacenes
    JOIN almacenes ad ON d.id_almacenes_destino = ad.id_almacenes
    JOIN producto p ON d.id_producto = p.id_producto
    WHERE ao.nombre LIKE %s OR ad.nombre LIKE %s OR p.nombre LIKE %s
    LIMIT %s OFFSET %s
    """
    search_pattern = f"%{search_query}%"
    try:
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, per_page, offset))
        distribuciones = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_distribuciones = cursor.fetchone()[0]
        return distribuciones, total_distribuciones
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def insert_distribucion(id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha):
    connection = create_connection()
    if connection is None:
        print("No se pudo establecer la conexión a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    INSERT INTO distribucion_almacenes (id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha) 
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Almacén Origen: {id_almacenes_origen}, ID Almacén Destino: {id_almacenes_destino}, ID Producto: {id_producto}, Cantidad: {cantidad}, Fecha: {fecha}"
        log_action('Inserted', screen_name='distribucion_almacenes', details=details)  # Registro de log
        print("Inserción exitosa.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_distribucion(id_distribucion, id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha):
    connection = create_connection()
    if connection is None:
        print("No se pudo establecer la conexión a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE distribucion_almacenes 
    SET id_almacenes_origen = %s, id_almacenes_destino = %s, id_producto = %s, cantidad = %s, fecha = %s 
    WHERE id_distribucion = %s
    """
    values = (id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha, id_distribucion)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Distribución: {id_distribucion}, ID Almacén Origen: {id_almacenes_origen}, ID Almacén Destino: {id_almacenes_destino}, ID Producto: {id_producto}, Cantidad: {cantidad}, Fecha: {fecha}"
        log_action('Updated', screen_name='distribucion_almacenes', details=details)  # Registro de log
        print("Actualización exitosa.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_distribucion(id_distribucion):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM distribucion_almacenes WHERE id_distribucion = %s"
    
    try:
        cursor.execute(query, (id_distribucion,))
        connection.commit()
        details = f"ID Distribución: {id_distribucion}"
        log_action('Deleted', screen_name='distribucion_almacenes', details=details)  # Registro de log
        print("Eliminación exitosa.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

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


@app_distribucion.route('/')
@check_permission('permiso_distribucion')
def index_distribucion():
    connection = create_connection()
    if connection is None:
        return render_template('index_distribucion.html', almacenes=[], productos=[])
    cursor = connection.cursor()
    
    cursor.execute("SELECT id_almacenes, nombre FROM almacenes")
    almacenes = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre FROM producto")
    productos = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('index_distribucion.html', almacenes=almacenes, productos=productos)

@app_distribucion.route('/distribuciones')
@check_permission('permiso_distribucion')
def distribuciones():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    if search_query:
        distribuciones, total_distribuciones = search_distribuciones(search_query, page, per_page)
    else:
        distribuciones, total_distribuciones = get_distribuciones(page, per_page)

    total_pages = (total_distribuciones + per_page - 1) // per_page
    return render_template('distribuciones.html', distribuciones=distribuciones, search_query=search_query, page=page, per_page=per_page, total_distribuciones=total_distribuciones, total_pages=total_pages)

@app_distribucion.route('/submit', methods=['POST'])
@check_permission('permiso_distribucion')
def submit():
    id_almacenes_origen = request.form['id_almacenes_origen']
    id_almacenes_destino = request.form['id_almacenes_destino']
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']
    fecha = request.form['fecha']

    if not id_almacenes_origen or not id_almacenes_destino  or not id_producto or not cantidad or not fecha:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_distribucion'))

    if insert_distribucion(id_almacenes_origen,id_almacenes_destino, id_producto, cantidad, fecha):
        flash('Distribución insertada exitosamente!')
    else:
        flash('Ocurrió un error al insertar la distribución.')

    return redirect(url_for('distribucion'))

@app_distribucion.route('/edit_distribucion/<int:id_distribucion>', methods=['GET', 'POST'])
@check_permission('permiso_distribucion')
def edit_distribucion(id_distribucion):
    if request.method == 'POST':
        id_almacenes_origen = request.form['id_almacenes_origen']
        id_almacenes_destino = request.form['id_almacenes_destino']
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        fecha = request.form['fecha']

        if not id_almacenes_origen or not id_almacenes_destino or not id_producto or not cantidad or not fecha:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_distribucion', id_distribucion=id_distribucion))

        if update_distribucion(id_distribucion, id_almacenes_origen, id_almacenes_destino, id_producto, cantidad, fecha):
            flash('Distribución actualizada exitosamente!')
        else:
            flash('Ocurrió un error al actualizar la distribución.')
        
        return redirect(url_for('distribuciones'))

    distribucion = get_distribucion_by_id(id_distribucion)
    if distribucion is None:
        flash('Distribución no encontrada!')
        return redirect(url_for('distribuciones'))

    # Obtener listas de almacenes y productos
    connection = create_connection()
    if connection is None:
        return render_template('edit_distribucion.html', distribucion=distribucion, almacenes=[], productos=[])

    cursor = connection.cursor()
    cursor.execute("SELECT id_almacenes, nombre FROM almacenes")
    almacenes = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre FROM producto")
    productos = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('edit_distribucion.html', distribucion=distribucion, almacenes=almacenes, productos=productos)

@app_distribucion.route('/delete/<int:id_distribucion>', methods=['GET', 'POST'])
@check_permission('permiso_distribucion')
def eliminar_distribucion(id_distribucion):
    # Verificar si el método es POST
    if request.method == 'POST':
        if delete_distribucion(id_distribucion):
            flash('Distribución eliminada exitosamente.')
        else:
            flash('Error al eliminar la distribución.')
        return redirect(url_for('distribuciones'))

    # Si el método no es POST, verificar si la distribución existe
    distribucion = get_distribucion_by_id(id_distribucion)
    if distribucion is None:
        flash('Distribución no encontrada.')
        return redirect(url_for('distribuciones'))

    return render_template('eliminar_distribucion.html', distribucion=distribucion)

@app_distribucion.route('/descargar_excel')
@check_permission('permiso_distribucion')
def descargar_excel():
    # Obtener todas las distribuciones sin paginación
    distribuciones = get_todas_distribuciones(limit=10, offset=0)  # Función para obtener todas las distribuciones

    if not distribuciones:
        flash('No hay distribuciones para descargar.')
        return redirect(url_for('distribuciones'))  # Asegúrate de que la ruta 'distribuciones' está bien definida

    # Definir las columnas correctas
    columnas = ['id_distribucion','almacen_origen', 'almacen_destino', 'nombre_producto', 'cantidad', 'fecha']

    # Crear un DataFrame con los datos de las distribuciones
    df = pd.DataFrame(distribuciones, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='distribuciones', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['distribuciones']

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de distribuciones')
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='distribuciones.xlsx')

def get_todas_distribuciones(limit, offset):
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'distribuciones'
    query = """
    SELECT d.id_distribucion, ao.nombre AS almacen_origen, ad.nombre AS almacen_destino, 
           p.nombre AS nombre_producto, d.cantidad, d.fecha
    FROM distribucion_almacenes d
    JOIN almacenes ao ON d.id_almacenes_origen = ao.id_almacenes
    JOIN almacenes ad ON d.id_almacenes_destino = ad.id_almacenes
    JOIN producto p ON d.id_producto = p.id_producto
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (limit, offset))  # Pasar limit y offset como parámetros
        distribuciones = cursor.fetchall()  # Obtener todas las filas
        return distribuciones
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()



@app_distribucion.route('/descargar_pdf')
@check_permission('permiso_distribucion')
def descargar_pdf():
    # Obtener todas las distribuciones y dividir en páginas de 10
    distribuciones = get_todas_las_distribuciones_pdf()
    paginacion = [distribuciones[i:i + 10] for i in range(0, len(distribuciones), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, distribuciones_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Distribución de Almacenes")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Distribuciones
        data = [["ID Distribución", "Almacén Origen", "Almacén Destino", "ID Producto", "Cantidad", "Fecha"]]  # Encabezado de la tabla
        data += [[record[0], record[1], record[2], record[3], record[4], record[5]] for record in distribuciones_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Distribucion_Almacenes.pdf')

def get_todas_las_distribuciones_pdf():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
    SELECT  d.id_distribucion, ao.nombre AS almacen_origen, ad.nombre AS almacen_destino, 
           p.nombre AS nombre_producto, d.cantidad, d.fecha
    FROM distribucion_almacenes d
    JOIN almacenes ao ON d.id_almacenes_origen = ao.id_almacenes
    JOIN almacenes ad ON d.id_almacenes_destino = ad.id_almacenes
    JOIN producto p ON d.id_producto = p.id_producto
    """
    try:
        cursor.execute(query)
        distribuciones = cursor.fetchall()
        return distribuciones
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()



if __name__ == '__main__':
    app_distribucion.run(debug=True,port=5002)
