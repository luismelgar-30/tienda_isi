from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask import send_file
from flask import Flask, session
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


app_almacenes = Flask(__name__)
app_almacenes.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/almacenes'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="almacenes", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="almacenes"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def almacen_exists(nombre, direccion, id_sucursal):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM almacenes WHERE nombre = %s AND direccion = %s AND id_sucursal = %s"
    cursor.execute(query, (nombre, direccion, id_sucursal))
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


def validate_text_field(text):
    if not 3 <= len(text) <= 20:
        return False, "El campo debe tener entre 3 y 20 caracteres."
    
    if re.search(r'\d', text):
        return False, "El campo no puede contener números."

    if re.search(r'[^\w\s]', text):
        return False, "El campo no puede contener caracteres especiales."

    if re.search(r'(.)\1\1', text):
        return False, "El campo no puede contener tres letras seguidas iguales."

    return True, ""

def insert_almacen(nombre, direccion, id_sucursal):
    if almacen_exists(nombre, direccion, id_sucursal):
        return False  # Retorna False si ya existe el almacén

    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "INSERT INTO almacenes (nombre, direccion, id_sucursal) VALUES (%s, %s, %s)"
    values = (nombre, direccion, id_sucursal)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre: {nombre}, Dirección: {direccion}, ID Sucursal: {id_sucursal}"
        log_action('Inserted', screen_name='almacenes', details=details)  # Registra la acción de inserción en logs
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def get_sucursales():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_sucursal, Ciudad FROM sucursales"
    try:
        cursor.execute(query)
        sucursales = cursor.fetchall()
        return sucursales
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()

def get_almacenes(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
        SELECT a.id_almacenes, a.nombre, a.direccion, s.Ciudad
        FROM almacenes a
        JOIN sucursales s ON a.id_sucursal = s.id_sucursal
        LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (per_page, offset))
        almacenes = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_almacenes = cursor.fetchone()[0]
        return almacenes, total_almacenes
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_almacen_by_id(id_almacen):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
        SELECT a.id_almacenes, a.nombre, a.direccion, a.id_sucursal, s.Ciudad
        FROM almacenes a
        JOIN sucursales s ON a.id_sucursal = s.id_sucursal
        WHERE a.id_almacenes = %s
    """
    try:
        cursor.execute(query, (id_almacen,))
        almacen = cursor.fetchone()
        return almacen
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def update_almacen(id_almacen, nombre, direccion, id_sucursal):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "UPDATE almacenes SET nombre = %s, direccion = %s, id_sucursal = %s WHERE id_almacenes = %s"
        values = (nombre, direccion, id_sucursal, id_almacen)
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"ID Almacen: {id_almacen}, Nombre: {nombre}, Dirección: {direccion}, ID Sucursal: {id_sucursal}"
        log_action('Updated', screen_name='almacenes', details=details)  # Registra la acción de actualización

        return True
    except Exception as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_almacen(id_almacen):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Obtener detalles del almacén antes de eliminar para el log
        cursor.execute("SELECT nombre, direccion, id_sucursal FROM almacenes WHERE id_almacenes = %s", (id_almacen,))
        almacen = cursor.fetchone()
        
        if not almacen:
            print("El almacén no existe")
            return False

        query = "DELETE FROM almacenes WHERE id_almacenes = %s"
        cursor.execute(query, (id_almacen,))
        connection.commit()

        # Registro en logs después de la eliminación
        nombre, direccion, id_sucursal = almacen
        details = f"ID Almacen: {id_almacen}, Nombre: {nombre}, Dirección: {direccion}, ID Sucursal: {id_sucursal}"
        log_action('Deleted', screen_name='almacenes', details=details)  # Registra la acción de eliminación

        return True
    except Exception as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def almacen_existe(nombre, direccion, id_sucursal):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
        SELECT COUNT(*)
        FROM almacenes
        WHERE nombre = %s AND direccion = %s AND id_sucursal = %s
    """
    values = (nombre, direccion, id_sucursal)
    try:
        cursor.execute(query, values)
        result = cursor.fetchone()
        return result[0] > 0  # Si el conteo es mayor que 0, el almacén ya existe
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return False
    finally:
        cursor.close()
        connection.close()


def get_historico_almacenes(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM historicos_almacenes LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        historico_almacenes = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_historico_almacenes = cursor.fetchone()[0]
        return historico_almacenes, total_historico_almacenes
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_almacenes(page, per_page, search_query=None, search_criteria=None):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = """
        SELECT a.id_almacenes, a.nombre, a.direccion, s.Ciudad
        FROM almacenes a
        JOIN sucursales s ON a.id_sucursal = s.id_sucursal
    """
    filters = []
    params = []

    # Agregar condición de búsqueda
    if search_query and search_criteria:
        filters.append(f"{search_criteria} LIKE %s")
        params.append(f'%{search_query}%')

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Consulta para paginación
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    try:
        cursor.execute(query, params)
        almacenes = cursor.fetchall()

        # Hacer una consulta separada para contar el total de registros
        count_query = """
            SELECT COUNT(*)
            FROM almacenes a
            JOIN sucursales s ON a.id_sucursal = s.id_sucursal
        """
        if filters:
            count_query += " WHERE " + " AND ".join(filters)

        cursor.execute(count_query, params[:-2])  # Usamos los mismos parámetros sin LIMIT y OFFSET
        total_almacenes = cursor.fetchone()[0]

        return almacenes, total_almacenes
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()


@app_almacenes.route('/historico_almacenes')
@check_permission('permiso_almacen')
def historico_almacenes():
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10))
    historicos, total_historicos = get_historico_almacenes(page, per_page)

    total_pages = (total_historicos + per_page - 1) // per_page
    return render_template('historico_almacenes.html', historicos=historicos, page=page, per_page=per_page, total_historicos=total_historicos, total_pages=total_pages)


@app_almacenes.route('/')
@check_permission('permiso_almacen')
def index_almacenes():
    sucursales = get_sucursales()  # Cargar las sucursales al inicio
    return render_template('index_almacenes.html', sucursales=sucursales)

@app_almacenes.route('/almacenes')
@check_permission('permiso_almacen')
def almacenes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    search_query = request.args.get('search_query', '')
    search_criteria = request.args.get('search_criteria', 'nombre')

    almacenes, total_almacenes = get_almacenes(page, per_page, search_query, search_criteria)
    total_pages = (total_almacenes + per_page - 1) // per_page

    return render_template('almacenes.html', almacenes=almacenes, page=page, per_page=per_page, 
                           total_almacenes=total_almacenes, total_pages=total_pages, 
                           search_query=search_query, search_criteria=search_criteria)

@app_almacenes.route('/submit', methods=['POST'])
@check_permission('permiso_almacen')
def submit():
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    id_sucursal = request.form['sucursal']

    errors = {}

    # Validaciones del campo nombre
    is_valid, error_message = validate_text_field(nombre)
    if not is_valid:
        errors['nombre_error'] = error_message

    # Validaciones del campo dirección
    if not direccion:
        errors['direccion_error'] = 'El campo dirección es obligatorio.'

    # Verificar si el almacén ya existe
    if almacen_existe(nombre, direccion, id_sucursal):
        errors['almacen_error'] = 'El almacén ya existe con los mismos datos.'

    # Si hay errores, renderizar el formulario con mensajes de error
    if errors:
        sucursales = get_sucursales()  # Cargar sucursales de nuevo para el formulario
        return render_template('index_almacenes.html', errors=errors, sucursales=sucursales)

    # Si no hay errores, proceder a insertar el almacén
    if insert_almacen(nombre, direccion, id_sucursal):
        flash('Almacén insertado exitosamente!', 'success')
    else:
        flash('Ocurrió un error al insertar el almacén.', 'error')

    return redirect(url_for('almacenes'))

@app_almacenes.route('/edit_almacen/<int:id_almacen>', methods=['POST', 'GET'])
@check_permission('permiso_almacen')
def edit_almacen(id_almacen):
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        id_sucursal = request.form['sucursal']

        # Validar campo 'nombre'
        is_valid, error_message = validate_text_field(nombre)
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('edit_almacen', id_almacen=id_almacen))

        # Actualizar almacén
        if update_almacen(id_almacen, nombre, direccion, id_sucursal):
            flash('Almacén actualizado exitosamente!', 'success')
        else:
            flash('Ocurrió un error al actualizar el almacén.', 'error')
        
        return redirect(url_for('almacenes'))
    
    # Cargar el almacén existente para la edición
    almacen = get_almacen_by_id(id_almacen)
    if almacen is None:
        flash('Almacén no encontrado.', 'error')
        return redirect(url_for('almacenes'))

    sucursales = get_sucursales()  # Obtener las sucursales para el formulario
    return render_template('edit_almacen.html', almacen=almacen, sucursales=sucursales)

@app_almacenes.route('/delete_almacen/<int:id_almacen>', methods=['GET', 'POST'])
@check_permission('permiso_almacen')
def eliminar_almacen(id_almacen):
    # Verificar si el método es POST
    if request.method == 'POST':
        if delete_almacen(id_almacen):  # Asegúrate de tener una función delete_almacen() definida
            flash('Almacén eliminado exitosamente.')
        else:
            flash('Error al eliminar el almacén.')
        return redirect(url_for('almacenes'))

    # Si el método no es POST, verificar si el almacén existe
    almacen = get_almacen_by_id(id_almacen)  # Asegúrate de tener una función get_almacen_by_id() definida
    if almacen is None:
        flash('Almacén no encontrado.')
        return redirect(url_for('almacenes'))

    return render_template('eliminar_almacen.html', almacen=almacen)

@app_almacenes.route('/descargar_excel_almacenes')
@check_permission('permiso_almacen')
def descargar_excel_almacenes():
    # Obtener todas las almacenes sin paginación
    almacenes = get_todos_almacenes()  # Función para obtener todas las almacenes

    if not almacenes:
        flash('No hay almacenes para descargar.')
        return redirect(url_for('almacenes'))  # Asegúrate de que la ruta 'almacenes' está bien definida

    # Definir las columnas correctas
    columnas = ['ID Almacén', 'Nombre', 'Dirección', 'Ciudad']

    # Crear un DataFrame con los datos de las almacenes
    df = pd.DataFrame(almacenes, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='almacenes', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['almacenes']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de almacenes', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, 
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, 
                    download_name='almacenes.xlsx')


def get_todos_almacenes():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """SELECT a.id_almacenes, a.nombre, a.direccion, s.Ciudad
        FROM almacenes a
        JOIN sucursales s ON a.id_sucursal = s.id_sucursal"""
    try:
        cursor.execute(query)
        pedidos_compra_pv = cursor.fetchall()
        return pedidos_compra_pv
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_almacenes.route('/descargar_pdf')
@check_permission('permiso_almacen')
def descargar_pdf():
    # Obtener todos los transportistas y dividir en páginas de 10
    almacenes2 = get_todos_almacenes()
    paginacion = [almacenes2[i:i + 10] for i in range(0, len(almacenes2), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, almacenes_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Almacenes")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Transportistas
        data = [["ID", "Nombre", "Direccion","Sucursal"]]  # Encabezado de la tabla
        data += [[almacenesC[0], almacenesC[1], almacenesC[2], almacenesC[3]] for almacenesC in almacenes_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Almacenes.pdf')



if __name__ == "__main__":
    app_almacenes.run(debug=True,port=5018)
