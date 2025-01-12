import datetime
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

app_pantallas = Flask(__name__)
app_pantallas.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/pantallas'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="pantallas", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="pantallas"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def pantallas_exists(nombre_pantalla):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM pantallas WHERE nombre_pantalla = %s"
    cursor.execute(query, (nombre_pantalla,))
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

def get_pantallas(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
        SELECT p.id_pantalla, r.nombre_rol, p.permiso_producto, p.permiso_empleado, p.permiso_inventario, 
               p.permiso_capacitacion, p.permiso_cliente, p.permiso_proveedor, p.permiso_sucursal,
               p.permiso_equipo, p.permiso_pedido_cliente, p.permiso_pedido_proveedor, p.permiso_devolucion_venta,
               p.permiso_devolucion_compra, p.permiso_promocion, p.permiso_mantenimiento, p.permiso_transportista,
               p.permiso_sar, p.permiso_usuario, p.permiso_categoria, p.permiso_distribucion, p.permiso_puesto_trabajo,
               p.permiso_impuesto, p.permiso_almacen
        FROM pantalla p
        JOIN roles r ON p.id_rol = r.id_rol
        LIMIT %s OFFSET %s
    """
    
    try:
        cursor.execute(query, (per_page, offset))
        pantallas = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM pantalla")
        total_count = cursor.fetchone()[0]

        return pantallas, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_pantallas_by_id(id_pantalla):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT id_pantalla, id_rol, permiso_producto, permiso_empleado, permiso_inventario, 
           permiso_capacitacion, permiso_cliente, permiso_proveedor, permiso_sucursal,
           permiso_equipo, permiso_pedido_cliente, permiso_pedido_proveedor, permiso_devolucion_venta,
           permiso_devolucion_compra, permiso_promocion, permiso_mantenimiento, permiso_transportista,
           permiso_sar, permiso_usuario, permiso_categoria, permiso_distribucion, permiso_puesto_trabajo,
           permiso_impuesto, permiso_almacen
    FROM pantalla
    WHERE id_pantalla = %s
    """
    try:
        cursor.execute(query, (id_pantalla,))
        pantallas = cursor.fetchone()
        return pantallas
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_pantallas(id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion,
                    permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente,
                    permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion,
                    permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario, 
                    permiso_categoria, permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    INSERT INTO pantalla (id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion,
                          permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente,
                          permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion,
                          permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario, 
                          permiso_categoria, permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion,
              permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente,
              permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion,
              permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario, 
              permiso_categoria, permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la inserción
        details = f"Rol ID: {id_rol}, Producto: {permiso_producto}, Empleado: {permiso_empleado}, " \
                  f"Inventario: {permiso_inventario}, Capacitacion: {permiso_capacitacion}, Cliente: {permiso_cliente}, " \
                  f"Proveedor: {permiso_proveedor}, Sucursal: {permiso_sucursal}, Equipo: {permiso_equipo}, " \
                  f"Pedido Cliente: {permiso_pedido_cliente}, Pedido Proveedor: {permiso_pedido_proveedor}, " \
                  f"Devolucion Venta: {permiso_devolucion_venta}, Devolucion Compra: {permiso_devolucion_compra}, " \
                  f"Promocion: {permiso_promocion}, Mantenimiento: {permiso_mantenimiento}, Transportista: {permiso_transportista}, " \
                  f"SAR: {permiso_sar}, Usuario: {permiso_usuario}, Categoria: {permiso_categoria}, " \
                  f"Distribucion: {permiso_distribucion}, Puesto Trabajo: {permiso_puesto_trabajo}, " \
                  f"Impuesto: {permiso_impuesto}, Almacen: {permiso_almacen}"
        log_action('Inserted', screen_name='pantalla', details=details)

        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()

def update_pantallas(id_pantalla, id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion,
                    permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente,
                    permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion,
                    permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario, 
                    permiso_categoria, permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE pantalla
    SET id_rol = %s, permiso_producto = %s, permiso_empleado = %s, permiso_inventario = %s, permiso_capacitacion = %s,
        permiso_cliente = %s, permiso_proveedor = %s, permiso_sucursal = %s, permiso_equipo = %s, permiso_pedido_cliente = %s,
        permiso_pedido_proveedor = %s, permiso_devolucion_venta = %s, permiso_devolucion_compra = %s, permiso_promocion = %s,
        permiso_mantenimiento = %s, permiso_transportista = %s, permiso_sar = %s, permiso_usuario = %s, 
        permiso_categoria = %s, permiso_distribucion = %s, permiso_puesto_trabajo = %s, permiso_impuesto = %s, permiso_almacen = %s
    WHERE id_pantalla = %s
    """
    values = (id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion, permiso_cliente,
              permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente, permiso_pedido_proveedor,
              permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion, permiso_mantenimiento,
              permiso_transportista, permiso_sar, permiso_usuario, permiso_categoria, permiso_distribucion,
              permiso_puesto_trabajo, permiso_impuesto, permiso_almacen, id_pantalla)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"Rol ID: {id_rol}, Producto: {permiso_producto}, Empleado: {permiso_empleado}, " \
                  f"Inventario: {permiso_inventario}, Capacitacion: {permiso_capacitacion}, Cliente: {permiso_cliente}, " \
                  f"Proveedor: {permiso_proveedor}, Sucursal: {permiso_sucursal}, Equipo: {permiso_equipo}, " \
                  f"Pedido Cliente: {permiso_pedido_cliente}, Pedido Proveedor: {permiso_pedido_proveedor}, " \
                  f"Devolucion Venta: {permiso_devolucion_venta}, Devolucion Compra: {permiso_devolucion_compra}, " \
                  f"Promocion: {permiso_promocion}, Mantenimiento: {permiso_mantenimiento}, Transportista: {permiso_transportista}, " \
                  f"SAR: {permiso_sar}, Usuario: {permiso_usuario}, Categoria: {permiso_categoria}, " \
                  f"Distribucion: {permiso_distribucion}, Puesto Trabajo: {permiso_puesto_trabajo}, " \
                  f"Impuesto: {permiso_impuesto}, Almacen: {permiso_almacen}"
        log_action('Updated', screen_name='pantalla', details=details)

        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()


def delete_pantallas(id_pantalla):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM pantalla WHERE id_pantalla = %s"
    try:
        cursor.execute(query, (id_pantalla,))
        connection.commit()

        # Registro en logs después de la eliminación
        details = f"ID Pantalla: {id_pantalla}"
        log_action('Deleted', screen_name='pantalla', details=details)

        return True
    except Error as e:
        error_message = f"Error al eliminar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()

def search_pantallas(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar el criterio de búsqueda
    if search_criteria not in ['id_rol', 'permiso_producto', 'permiso_empleado', 'permiso_inventario', 
                               'permiso_capacitacion', 'permiso_cliente', 'permiso_proveedor', 
                               'permiso_sucursal', 'permiso_equipo', 'permiso_pedido_cliente', 
                               'permiso_pedido_proveedor', 'permiso_devolucion_venta', 
                               'permiso_devolucion_compra', 'permiso_promocion', 'permiso_mantenimiento', 
                               'permiso_transportista', 'permiso_sar', 'permiso_usuario', 'permiso_categoria',
        'permiso_distribucion', 'permiso_puesto_trabajo', 'permiso_impuesto', 'permiso_almacen']:
        search_criteria = 'id_rol'  # Default search criterion

    # Consulta SQL para buscar en la tabla de pantallas con criterios dinámicos
    query = f"SELECT * FROM pantalla WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    
    try:
        # Ejecutar la consulta para obtener los registros de pantallas
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        pantallas = cursor.fetchall()

        # Ejecutar una consulta para obtener el conteo total de registros que coinciden con el criterio de búsqueda
        cursor.execute(f"SELECT COUNT(*) FROM pantalla WHERE {search_criteria} LIKE %s", (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return pantallas, total_count
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

@app_pantallas.route('/')
def index_pantallas():
    return render_template('index_pantallas.html')

@app_pantallas.route('/pantallas')
def pantallas():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if search_criteria and search_query:
        pantallas, total_count = search_pantallas(search_criteria, search_query, page, per_page)
    else:
        pantallas, total_count = get_pantallas(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('pantallas.html', pantallas=pantallas, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_pantallas.route('/submit_pantalla', methods=['POST'])
def submit_pantallas():
    id_rol = request.form.get('id_rol')
    permiso_producto = int(request.form.get('permiso_producto', 0))
    permiso_empleado = int(request.form.get('permiso_empleado', 0))
    permiso_inventario = int(request.form.get('permiso_inventario', 0))
    permiso_capacitacion = int(request.form.get('permiso_capacitacion', 0))
    permiso_cliente = int(request.form.get('permiso_cliente', 0))
    permiso_proveedor = int(request.form.get('permiso_proveedor', 0))
    permiso_sucursal = int(request.form.get('permiso_sucursal', 0))
    permiso_equipo = int(request.form.get('permiso_equipo', 0))
    permiso_pedido_cliente = int(request.form.get('permiso_pedido_cliente', 0))
    permiso_pedido_proveedor = int(request.form.get('permiso_pedido_proveedor', 0))
    permiso_devolucion_venta = int(request.form.get('permiso_devolucion_venta', 0))
    permiso_devolucion_compra = int(request.form.get('permiso_devolucion_compra', 0))
    permiso_promocion = int(request.form.get('permiso_promocion', 0))
    permiso_mantenimiento = int(request.form.get('permiso_mantenimiento', 0))
    permiso_transportista = int(request.form.get('permiso_transportista', 0))
    permiso_sar = int(request.form.get('permiso_sar', 0))
    permiso_usuario = int(request.form.get('permiso_usuario', 0))
    permiso_categoria = int(request.form.get('permiso_categoria', 0))
    permiso_distribucion = int(request.form.get('permiso_distribucion', 0))
    permiso_puesto_trabajo = int(request.form.get('permiso_puesto_trabajo', 0))
    permiso_impuesto = int(request.form.get('permiso_impuesto', 0))
    permiso_almacen = int(request.form.get('permiso_almacen', 0))

    # Inserta el permiso en la base de datos
    if insert_pantallas(id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion, permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente, permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion, permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario, permiso_categoria, permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen):
        flash('Permiso de pantalla insertado correctamente!')
    else:
        flash('Ocurrió un error al insertar el permiso de pantalla.')

    return redirect(url_for('pantallas'))


@app_pantallas.route('/edit_pantallas/<int:id_pantalla>', methods=['GET', 'POST'])
def edit_pantallas(id_pantalla):
    if request.method == 'POST':
        # Obtener los pantallas actuales
        id_rol = request.form.get('id_rol')
        if not id_rol:
            flash('El rol es obligatorio.')
            return redirect(url_for('edit_pantallas', id_pantalla=id_pantalla))

        # Manejo de checkboxes (pantallas de pantalla)
        permiso_producto = 1 if request.form.get('permiso_producto') == 'on' else 0
        permiso_empleado = 1 if request.form.get('permiso_empleado') == 'on' else 0
        permiso_inventario = 1 if request.form.get('permiso_inventario') == 'on' else 0
        permiso_capacitacion = 1 if request.form.get('permiso_capacitacion') == 'on' else 0
        permiso_cliente = 1 if request.form.get('permiso_cliente') == 'on' else 0
        permiso_proveedor = 1 if request.form.get('permiso_proveedor') == 'on' else 0
        permiso_sucursal = 1 if request.form.get('permiso_sucursal') == 'on' else 0
        permiso_equipo = 1 if request.form.get('permiso_equipo') == 'on' else 0
        permiso_pedido_cliente = 1 if request.form.get('permiso_pedido_cliente') == 'on' else 0
        permiso_pedido_proveedor = 1 if request.form.get('permiso_pedido_proveedor') == 'on' else 0
        permiso_devolucion_venta = 1 if request.form.get('permiso_devolucion_venta') == 'on' else 0
        permiso_devolucion_compra = 1 if request.form.get('permiso_devolucion_compra') == 'on' else 0
        permiso_promocion = 1 if request.form.get('permiso_promocion') == 'on' else 0
        permiso_mantenimiento = 1 if request.form.get('permiso_mantenimiento') == 'on' else 0
        permiso_transportista = 1 if request.form.get('permiso_transportista') == 'on' else 0
        permiso_sar = 1 if request.form.get('permiso_sar') == 'on' else 0
        permiso_usuario = 1 if request.form.get('permiso_usuario') == 'on' else 0
        permiso_categoria = 1 if request.form.get('permiso_categoria') == 'on' else 0
        permiso_distribucion = 1 if request.form.get('permiso_distribucion') == 'on' else 0
        permiso_puesto_trabajo = 1 if request.form.get('permiso_puesto_trabajo') == 'on' else 0
        permiso_impuesto = 1 if request.form.get('permiso_impuesto') == 'on' else 0
        permiso_almacen = 1 if request.form.get('permiso_almacen') == 'on' else 0

        # Actualizar los pantallas de pantalla
        if update_pantallas(id_pantalla, id_rol, permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion, permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo, permiso_pedido_cliente, permiso_pedido_proveedor, permiso_devolucion_venta, permiso_devolucion_compra, permiso_promocion, permiso_mantenimiento, permiso_transportista, permiso_sar, permiso_usuario,permiso_categoria,permiso_distribucion,permiso_puesto_trabajo,permiso_impuesto,permiso_almacen):
            flash('Permiso de pantalla actualizado correctamente!')
        else:
            flash('Error al actualizar el permiso de pantalla.')

        return redirect(url_for('pantallas'))

    # Obtener los pantallas actuales para el id_pantalla seleccionado
    pantallas = get_pantallas_by_id(id_pantalla)
    return render_template('edit_pantallas.html', pantallas=pantallas)

@app_pantallas.route('/eliminar_pantalla/<int:id_pantalla>', methods=['GET', 'POST'])
def eliminar_pantallas(id_pantalla):
    if request.method == 'POST':
        if delete_pantallas(id_pantalla):
            flash('Permiso de pantalla eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el permiso de pantalla.')
        return redirect(url_for('pantallas'))

    pantallas = get_pantallas_by_id(id_pantalla)
    if pantallas is None:
        flash('Permiso de pantalla no encontrado!')
        return redirect(url_for('pantallas'))
    
    return render_template('eliminar_pantallas.html', pantallas=pantallas)


@app_pantallas.route('/descargar_excel')
def descargar_excel():
    # Obtener todas las categorías sin paginación
    pantallas = get_todas_pantallas()  # Función para obtener todas las categorías

    if not pantallas:
        flash('No hay categorías para descargar.')
        return redirect(url_for('pantallas'))  # Asegúrate de que la ruta 'pantallas' está bien definida

    # Definir las columnas correctas
    columnas = ['id_pantalla', 'nombre_pantalla', 'Descripcion']

    # Crear un DataFrame con los datos de las categorías
    df = pd.DataFrame(pantallas, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='pantallas', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['pantallas']

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de categorías')
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='pantallas.xlsx')


# Nueva función para obtener todas las categorías sin límites
def get_todas_pantallas():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'pantallas'
    query = "SELECT id_pantalla, nombre_pantalla, Descripcion FROM pantallas"

    try:
        cursor.execute(query)
        pantallas = cursor.fetchall()  # Obtener todas las filas
        return pantallas
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

@app_pantallas.route('/descargar_pdf')
def descargar_pdf():
    # Obtener todas las categorías y dividir en páginas de 10
    pantallas = get_todas_pantallas()
    paginacion = [pantallas[i:i + 10] for i in range(0, len(pantallas), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, pantallas_pagina in enumerate(paginacion, start=1):
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
        data = [["id_pantalla", "Nombre_pantalla", "Descripción"]]  # Encabezado de la tabla
        data += [[record[0], record[1], record[2]] for record in pantallas_pagina]

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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='pantallas.pdf')



if __name__ == '__main__':
    app_pantallas.run(debug=True, port=5037)
