from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import pandas as pd
from io import BytesIO
from flask import send_file
from flask import Flask, session
import io
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime

app_cliente = Flask(__name__)
app_cliente.secret_key = 'your_secret_key'


LOGS_DIR = 'logs/cliente'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="cliente", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="cliente"):
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

def cliente_exists(nombre):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM cliente WHERE nombre = %s"
    cursor.execute(query, (nombre,))
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

def get_cliente():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT * FROM cliente"
    try:
        cursor.execute(query)
        cliente = cursor.fetchall()
        return cliente
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_cliente_by_id(id_cliente):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM cliente WHERE id_cliente = %s"
    try:
        cursor.execute(query, (id_cliente,))
        cliente = cursor.fetchone()
        return cliente
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_user(nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "INSERT INTO cliente (nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la inserción
        details = f"Nombre: {nombre}, Apellido: {apellido}, Email: {email}"
        log_action('Inserted', screen_name='clientes', details=details)  # Registro de la acción de inserción

        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_user(id_cliente, nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "UPDATE cliente SET nombre = %s, apellido = %s, fecha_nacimiento = %s, email = %s, telefono = %s, direccion = %s, fecha_registro = %s, tipo = %s, documento = %s WHERE id_cliente = %s"
    values = (nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento, id_cliente)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"ID: {id_cliente}, Nombre: {nombre}, Apellido: {apellido}, Email: {email}"
        log_action('Updated', screen_name='clientes', details=details)  # Registro de la acción de actualización

        return True
    except Error as e:
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_user(id_cliente):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()

    # Obtener detalles del cliente antes de eliminar para el log
    cursor.execute("SELECT nombre, apellido, email FROM cliente WHERE id_cliente = %s", (id_cliente,))
    cliente = cursor.fetchone()

    if not cliente:
        print("Cliente no encontrado")
        return False

    nombre, apellido, email = cliente
    query = "DELETE FROM cliente WHERE id_cliente = %s"
    try:
        cursor.execute(query, (id_cliente,))
        connection.commit()

        # Registro en logs después de la eliminación
        details = f"ID: {id_cliente}, Nombre: {nombre}, Apellido: {apellido}, Email: {email}"
        log_action('Deleted', screen_name='clientes', details=details)  # Registro de la acción de eliminación

        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def search_users(search_query):
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT * FROM cliente WHERE id_cliente LIKE %s OR nombre LIKE %s OR apellido LIKE %s OR fecha_nacimiento LIKE %s OR email LIKE %s OR telefono LIKE %s OR direccion LIKE %s  OR fecha_registro LIKE %s OR tipo LIKE %s OR documento LIKE %s"
    values = (f'%{search_query}%', f'%{search_query}%',f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}', f'%{search_query}',f'%{search_query}',f'%{search_query}00')
    try:
        cursor.execute(query, values)
        cliente = cursor.fetchall()
        return cliente
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_historico_clientes(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM historicos_clientes LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        historico_clientes = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_historico_clientes = cursor.fetchone()[0]
        return historico_clientes, total_historico_clientes
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

@app_cliente.template_filter('format_dni')
@check_permission('permiso_cliente')
def format_dni(dni):
    if dni and len(dni) == 13:
        return f"{dni[:4]}-{dni[4:8]}-{dni[8:]}"
    return dni

@app_cliente.route('/historico_clientes')
@check_permission('permiso_cliente')
def historico_clientes():
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10))
    historicos, total_historicos = get_historico_clientes(page, per_page)

    total_pages = (total_historicos + per_page - 1) // per_page
    return render_template('historico_clientes.html', historicos=historicos, page=page, per_page=per_page, total_historicos=total_historicos, total_pages=total_pages)

@app_cliente.route('/')
@check_permission('permiso_cliente')
def index_cliente():
    return render_template('index_cliente.html')

@app_cliente.route('/cliente')
@check_permission('permiso_cliente')
def cliente():
    # Obtener el número de clientes a mostrar por página (5, 10, 15) desde los parámetros de la URL
    per_page = int(request.args.get('per_page', 5))  # 5 es el valor por defecto
    page = request.args.get('page', 1, type=int)
    
    search_query = request.args.get('search')
    
    if search_query:
        cliente = search_users(search_query)
    else:
        cliente = get_cliente()
    
    # Paginación manual
    total_clientes = len(cliente)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_cliente = cliente[start:end]
    
    total_pages = (total_clientes + per_page - 1) // per_page
    
    return render_template(
        'cliente.html',
        cliente=paginated_cliente,
        search_query=search_query,
        page=page,
        per_page=per_page,
        total_clientes=total_clientes,
        total_pages=total_pages
    )

@app_cliente.route('/submit', methods=['POST'])
@check_permission('permiso_cliente')
def submit():
    
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    fecha_nacimiento = request.form['fecha_nacimiento']
    email = request.form['email']
    telefono = request.form['telefono']
    direccion = request.form['direccion']
    fecha_registro = request.form['fecha_registro']
    tipo = request.form['tipo']
    documento = request.form['documento']

    if not  nombre or not apellido or not fecha_nacimiento or not email or not telefono or not direccion or not fecha_registro or not tipo or not documento:
        flash('Todos los campos son necesarios!')
        return redirect(url_for('index_cliente'))

    if insert_user( nombre, apellido, fecha_nacimiento, email,telefono,direccion,fecha_registro, tipo, documento):
        flash('Cliente insertado!')
    else:
        flash('Error insertando el cliente.')
    
    return redirect(url_for('index_cliente'))

@app_cliente.route('/edit_cliente/<int:id_cliente>', methods=['GET', 'POST'])
@check_permission('permiso_cliente')
def edit_cliente(id_cliente):
    if request.method == 'POST':
        
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        fecha_registro = request.form['fecha_registro']
        tipo = request.form['tipo']
        documento = request.form['documento']

        if not id_cliente or not nombre or not apellido or not fecha_nacimiento or not email or not telefono or not direccion or not fecha_registro or not tipo or not documento:
            flash('All fields are required!')
            return redirect(url_for('edit_cliente', id_cliente=id_cliente))

        if update_user(id_cliente, nombre, apellido, fecha_nacimiento, email,telefono,direccion,fecha_registro, tipo, documento):
            flash('Cliente actualizado!')
        else:
            flash('Error actualizando el cliente.')
        
        return redirect(url_for('cliente'))

    cliente = get_cliente_by_id(id_cliente)
    if cliente is None:
        flash('Product not found!')
        return redirect(url_for('cliente'))
    return render_template('edit_cliente.html', cliente=cliente)

@app_cliente.route('/eliminar_cliente/<int:id_cliente>', methods=['GET', 'POST'])
@check_permission('permiso_cliente')
def eliminar_cliente(id_cliente):
    if request.method == 'POST':
        if delete_user(id_cliente):
            flash('Product deleted successfully!')
        else:
            flash('An error occurred while deleting the product.')
        return redirect(url_for('cliente'))

    cliente = get_cliente_by_id(id_cliente)
    if cliente is None:
        flash('Product not found!')
        return redirect(url_for('cliente'))
    return render_template('eliminar_cliente.html', cliente=cliente)

# Nueva función para generar y descargar el archivo Excel
@app_cliente.route('/descargar_excel')
@check_permission('permiso_cliente')
def descargar_excel():
    cliente = get_cliente()  # Obtener los datos de la base de datos

    if not cliente:
        flash('No hay clientes para descargar.')
        return redirect(url_for('cliente'))

    # Crear un DataFrame con los datos de los clientes
    columnas = ['ID', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Email', 'Telefono', 'Direccion', 'Fecha Registro', 'Tipo', 'Documento']
    df = pd.DataFrame(cliente, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='Clientes', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir metadatos
        workbook = writer.book
        worksheet = writer.sheets['Clientes']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadata en las primeras filas
        worksheet.write('A1', 'Listado de Clientes', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='clientes.xlsx')

def get_todos_clientes():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT id_cliente, nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento
        FROM cliente
    """
    try:
        cursor.execute(query)
        clientes = cursor.fetchall()
        return clientes
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_cliente.route('/descargar_pdf')
@check_permission('permiso_cliente')
def descargar_pdf():
    # Obtener todos los clientes y dividir en páginas de 10
    clientes = get_todos_clientes()
    paginacion = [clientes[i:i + 10] for i in range(0, len(clientes), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto = landscape(A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primer_nombre = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, clientes_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Clientes")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {primer_nombre}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Clientes
        data = [["ID", "Nombre", "Apellido", "Fecha Nacimiento", "Email", "Teléfono", "Dirección", "Fecha Registro", "Tipo", "Documento"]]  # Encabezado de la tabla
        data += [[cliente[0], cliente[1], cliente[2], cliente[3], cliente[4], cliente[5], cliente[6], cliente[7], cliente[8], cliente[9]] 
                 for cliente in clientes_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[0.8 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.5 * inch, 
                                       1.2 * inch, 1.8 * inch, 1.2 * inch, 1 * inch, 1 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Clientes.pdf')


if __name__ == '__main__':
    app_cliente.run(debug=True,port=5004)
