import datetime
from functools import wraps
from io import BytesIO
import os
from flask import Flask, jsonify, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime

app_devoluciones = Flask(__name__)
app_devoluciones.secret_key = 'your_secret_key'  # Cambia 'your_secret_key' por una clave secreta segura

LOGS_DIR = 'logs/devoluciones_ventas'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="devoluciones_ventas", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="devoluciones_ventas"):
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


def devoluciones_ventas_exists(id_pedido, id_detalle):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    
    try:
        query = "SELECT COUNT(*) FROM devoluciones_ventas WHERE id_pedido = %s AND id_detalle = %s"
        cursor.execute(query, (id_pedido, id_detalle))
        exists = cursor.fetchone()[0] > 0
        return exists

    except Error as e:
        print(f"Error '{e}' ocurrió durante la verificación de existencia")
        return False

    finally:
        cursor.close()
        connection.close()

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

def get_devoluciones(page, per_page, search_query=None):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    if search_query:
        query = """
            SELECT d.id_devolucion, d.id_pedido, dt.id_detalle, p.nombre AS nombre_producto, 
                   d.fecha_devolucion, d.motivo, d.cantidad_devuelta
            FROM devoluciones_ventas d
            JOIN detalle_de_compra_cliente dt ON d.id_detalle = dt.id_detalle
            JOIN producto p ON dt.id_producto = p.id_producto
            WHERE d.id_devolucion LIKE %s OR d.id_pedido LIKE %s
            LIMIT %s OFFSET %s
        """
        values = (f'%{search_query}%', f'%{search_query}%', per_page, offset)
    else:
        query = """
            SELECT d.id_devolucion, d.id_pedido, dt.id_detalle, p.nombre AS nombre_producto, 
                   d.fecha_devolucion, d.motivo, d.cantidad_devuelta
            FROM devoluciones_ventas d
            JOIN detalle_de_compra_cliente dt ON d.id_detalle = dt.id_detalle
            JOIN producto p ON dt.id_producto = p.id_producto
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        cursor.execute(query, values)
        devoluciones = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return devoluciones, total_count
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_pedidos():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_pedido, fecha_pedido FROM pedido_de_compra_cliente"  # Cambiar el nombre de la tabla aquí
    try:
        cursor.execute(query)
        pedidos = cursor.fetchall()
        return pedidos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()

def get_detalles_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor()
    query = """
        SELECT dt.id_detalle, dt.id_producto, dt.cantidad, dt.precio_unitario 
        FROM detalle_de_compra_cliente dt 
        WHERE dt.id_pedido = %s
    """
    try:
        cursor.execute(query, (id_pedido,))
        detalles = cursor.fetchall()
        print(f"Detalles for ID {id_pedido}: {detalles}")  # Debug line
        return detalles
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()


def insert_devolucion(id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO devoluciones_ventas (id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta) 
               VALUES (%s, %s, %s, %s, %s)"""
    values = (id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Pedido: {id_pedido}, ID Detalle: {id_detalle}, Fecha: {fecha_devolucion}, Motivo: {motivo}, Cantidad Devuelta: {cantidad_devuelta}"
        log_action('Inserted', screen_name='devoluciones_ventas', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_devolucion(id_devolucion, id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE devoluciones_ventas
    SET id_pedido = %s,
        id_detalle = %s,
        fecha_devolucion = %s,
        motivo = %s,
        cantidad_devuelta = %s
    WHERE id_devolucion = %s
    """
    
    values = (id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta, id_devolucion)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Devolución: {id_devolucion}, ID Pedido: {id_pedido}, ID Detalle: {id_detalle}, Fecha: {fecha_devolucion}, Motivo: {motivo}, Cantidad Devuelta: {cantidad_devuelta}"
        log_action('Updated', screen_name='devoluciones_ventas', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_devolucion(id_devolucion):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM devoluciones_ventas WHERE id_devolucion = %s"
    
    try:
        cursor.execute(query, (id_devolucion,))
        connection.commit()
        details = f"ID Devolución: {id_devolucion}"
        log_action('Deleted', screen_name='devoluciones_ventas', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def get_devolucion_by_id(id_devolucion):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM devoluciones_ventas WHERE id_devolucion = %s"
    try:
        cursor.execute(query, (id_devolucion,))
        devolucion = cursor.fetchone()
        return devolucion
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()
    
def get_producto_by_id(id_producto):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM producto WHERE id_producto = %s"
    try:
        cursor.execute(query, (id_producto,))
        producto = cursor.fetchone()
        return producto  # Asegúrate de que aquí estás retornando el producto completo
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

@app_devoluciones.route('/detalles/<int:id_pedido>')
@check_permission('permiso_devolucion_venta')
def detalles(id_pedido):
    detalles = get_detalles_by_pedido(id_pedido)

    # Obtener los nombres de los productos
    productos_nombres = {}
    for detalle in detalles:
        id_producto = detalle[1]  # Suponiendo que el segundo elemento es el ID del producto
        producto = get_producto_by_id(id_producto)
        if producto:
            productos_nombres[id_producto] = producto[1]  # Suponiendo que el nombre del producto es el segundo elemento en la tupla

    return jsonify([{'id_detalle': detalle[0], 'nombre_producto': productos_nombres.get(detalle[1], 'Desconocido'), 'cantidad': detalle[2]} for detalle in detalles])

@app_devoluciones.route('/')
@check_permission('permiso_devolucion_venta')
def index_devoluciones_ventas():
    pedidos = get_pedidos()  # Your logic to fetch pedidos
    page = request.args.get('page', 1, type=int)  # Get the page number
    return render_template('index_devoluciones_ventas.html', pedidos=pedidos, page=page)

@app_devoluciones.route('/submit', methods=['POST'])
@check_permission('permiso_devolucion_venta')
def submit():

    id_pedido = request.form.get('id_pedido')
    id_detalle = request.form.get('id_detalle')
    fecha_devolucion = request.form.get('fecha_devolucion')  # Asegúrate de que este campo esté en el formulario
    motivo = request.form.get('motivo')
    cantidad_devuelta = request.form.get('cantidad_devuelta')

    if not id_pedido or not id_detalle or not fecha_devolucion or not motivo or not cantidad_devuelta:
        flash('¡Todos los campos obligatorios deben ser completados!')
        return redirect(url_for('index_devoluciones'))

    if insert_devolucion(id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta):
        flash('Devolución agregada exitosamente!')
    else:
        flash('Error al agregar la devolución.')

    return redirect(url_for('devoluciones_ventas'))  # Redirigir a la lista de devoluciones


@app_devoluciones.route('/devoluciones')
@check_permission('permiso_devolucion_venta')
def devoluciones_ventas():
    search_query = request.args.get('search_query', '')
    search_criteria = request.args.get('search_criteria', 'id_devolucion')  # Default value
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    devoluciones, total_count = get_devoluciones(page, per_page, search_query)

    total_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0)

    return render_template(
        'devoluciones_ventas.html',
        devoluciones=devoluciones,
        page=page,
        total_pages=total_pages,
        search_query=search_query,
        search_criteria=search_criteria,  # Ensure this is also passed
        per_page=per_page  # Pass per_page to the template
    )


@app_devoluciones.route('/edit_devolucion_ventas/<int:id_devolucion>', methods=['GET', 'POST'])
@check_permission('permiso_devolucion_venta')
def edit_devolucion_ventas(id_devolucion):
    if request.method == 'POST':
        id_pedido = request.form.get('id_pedido')
        id_detalle = request.form.get('id_detalle')
        fecha_devolucion = request.form.get('fecha_devolucion')
        motivo = request.form.get('motivo')
        cantidad_devuelta = request.form.get('cantidad_devuelta')

        # Validación de los campos obligatorios
        if not id_pedido or not id_detalle or not fecha_devolucion or not motivo or not cantidad_devuelta:
            flash('¡Todos los campos obligatorios deben ser completados!')
            # Redirige a la página de edición correcta
            return redirect(url_for('edit_devoluciones_ventas', id_devolucion=id_devolucion))

        # Actualización de la devolución
        if update_devolucion(id_devolucion, id_pedido, id_detalle, fecha_devolucion, motivo, cantidad_devuelta):
            flash('Devolución actualizada exitosamente!')
        else:
            flash('Error al actualizar la devolución.')

        # Redirige a la lista de devoluciones de ventas
        return redirect(url_for('devoluciones_ventas'))

    # Obtener la devolución y la lista de pedidos para el método GET
    devolucion = get_devolucion_by_id(id_devolucion)
    pedidos = get_pedidos()  # Obtener la lista de pedidos
    return render_template('edit_devoluciones_ventas.html', devolucion=devolucion, pedidos=pedidos)

@app_devoluciones.route('/eliminar_devolucion/<int:id_devolucion>', methods=['GET', 'POST'])
@check_permission('permiso_devolucion_venta')
def eliminar_devolucion(id_devolucion):
    if request.method == 'POST':
        if delete_devolucion(id_devolucion):  # Assuming you have a delete_devolucion function
            flash('¡Devolución eliminada exitosamente!')
        else:
            flash('Ocurrió un error al eliminar la devolución.')
        return redirect(url_for('devoluciones'))  # Assuming 'devolucion' is the endpoint for your devolución list

    devolucion = get_devolucion_by_id(id_devolucion)  # Assuming you have a get_devolucion_by_id function
    if devolucion is None:
        flash('¡Devolución no encontrada!')
        return redirect(url_for('devoluciones'))

    return render_template('eliminar_devolucion_ventas.html', devolucion=devolucion)

@app_devoluciones.route('/descargar_excel')
@check_permission('permiso_devolucion_venta')
def descargar_excel():
    # Obtener todas las devoluciones sin paginación
    devoluciones = get_todas_devoluciones()  # Función para obtener todas las devoluciones

    if not devoluciones:
        flash('No hay devoluciones para descargar.')
        return redirect(url_for('devoluciones_ventas'))  # Asegúrate de que la ruta 'devoluciones_ventas' está bien definida

    # Definir las columnas correctas
    columnas = ['id_devolucion', 'id_pedido', 'nombre_producto', 'fecha_devolucion', 'motivo', 'cantidad_devuelta']

    # Crear un DataFrame con los datos de las devoluciones
    df = pd.DataFrame(devoluciones, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='devoluciones', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['devoluciones']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de devoluciones_Ventas', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='devoluciones.xlsx')


# Nueva función para obtener todas las devoluciones sin límites
def get_todas_devoluciones():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'devoluciones'
    query = """
            SELECT d.id_devolucion, d.id_pedido, p.nombre AS nombre_producto, 
                   d.fecha_devolucion, d.motivo, d.cantidad_devuelta
            FROM devoluciones_ventas d
            JOIN detalle_de_compra_cliente dt ON d.id_detalle = dt.id_detalle
            JOIN producto p ON dt.id_producto = p.id_producto
        """  # Eliminado LIMIT y OFFSET

    try:
        cursor.execute(query)
        devoluciones = cursor.fetchall()  # Obtener todas las filas
        return devoluciones
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

@app_devoluciones.route('/descargar_pdf')
@check_permission('permiso_devolucion_venta')
def descargar_pdf():
    # Obtener todas las devoluciones y dividir en páginas de 10
    devoluciones = get_todas_devoluciones()
    paginacion = [devoluciones[i:i + 10] for i in range(0, len(devoluciones), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, devoluciones_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Devoluciones de Ventas")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Devoluciones
        data = [["ID Devolución", "ID Pedido", "ID Detalle", "Fecha Devolución", "Motivo", "Cantidad Devuelta"]]  # Encabezado de la tabla
        data += [[devolucion[0], devolucion[1], devolucion[2], devolucion[3], devolucion[4], devolucion[5]] for devolucion in devoluciones_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 1 * inch, 1 * inch, 1.5 * inch, 2.5 * inch, 1 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Devoluciones_Ventas.pdf')


if __name__ == '__main__':
    app_devoluciones.run(debug=True,port=5026)
