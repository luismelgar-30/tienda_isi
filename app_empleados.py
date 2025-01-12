from functools import wraps
import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
import datetime
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

app_empleados = Flask(__name__)
app_empleados.secret_key = 'your_secret_key'


LOGS_DIR = 'logs/empleados'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="empleados", details=None):
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


def log_error(error_message, screen_name="empleados"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

# Función para cifrar la contraseña
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Verificar la contraseña
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def empleados_exists(id_empleados):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM empleados WHERE id_empleados = %s"
    cursor.execute(query, (id_empleados,))
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

def insert_user(nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password):
    connection = create_connection()
    if connection is None:
        return False

    hashed_password = hash_password(password)  # Cifrar la contraseña
    cursor = connection.cursor()
    query = """INSERT INTO empleados (nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, hashed_password)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre: {nombre}, Apellido: {apellido}, ID Puesto: {id_puesto}, ID Sucursal: {id_sucursal}, Email: {email}"
        log_action('Inserted', screen_name='empleados', details=details)  # Registro de log
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


def update_user(id_empleado, nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = """UPDATE empleados SET nombre = %s, apellido = %s, fecha_nacimiento = %s, id_puesto = %s,
               fecha_contratacion = %s, id_sucursal = %s, email = %s, telefono = %s, tipo = %s, documento = %s, password = %s
               WHERE id_empleado = %s"""
    values = (nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password, id_empleado)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Empleado: {id_empleado}, Nombre: {nombre}, Apellido: {apellido}, ID Puesto: {id_puesto}, Email: {email}"
        log_action('Updated', screen_name='empleados', details=details)  # Registro de log
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

def delete_user(id_empleado):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM empleados WHERE id_empleado = %s"
    
    try:
        cursor.execute(query, (id_empleado,))
        connection.commit()
        details = f"ID Empleado: {id_empleado}"
        log_action('Deleted', screen_name='empleados', details=details)  # Registro de log
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

def get_empleados(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM empleados LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        empleados = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_empleados = cursor.fetchone()[0]
        return empleados, total_empleados
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_users(search_query, search_criteria, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"SELECT SQL_CALC_FOUND_ROWS * FROM empleados WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (f"%{search_query}%", per_page, offset))
        empleados = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_empleados = cursor.fetchone()[0]
        return empleados, total_empleados
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_empleados_by_id(id_empleado):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM empleados WHERE id_empleado = %s"
    try:
        cursor.execute(query, (id_empleado,))
        empleado = cursor.fetchone()
        return empleado
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def get_sucursales():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_sucursal, ciudad FROM sucursales"
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

def get_puestos_de_trabajo():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_puesto, puesto_trabajo FROM puesto_de_trabajo"
    try:
        cursor.execute(query)
        puestos = cursor.fetchall()
        return puestos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()


def get_historico_empleados(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM historico_empleados LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        historicos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_historicos = cursor.fetchone()[0]
        return historicos, total_historicos
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

@app_empleados.route('/historico_empleados')
@check_permission('permiso_empleado')
def historico_empleados():
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10))
    historicos, total_historicos = get_historico_empleados(page, per_page)

    total_pages = (total_historicos + per_page - 1) // per_page
    return render_template('historico_empleados.html', historicos=historicos, page=page, per_page=per_page, total_historicos=total_historicos, total_pages=total_pages)

@app_empleados.route('/')
@check_permission('permiso_empleado')
def index_empleados():
    sucursales = get_sucursales()
    puestos_de_trabajo = get_puestos_de_trabajo()  # Obtener puestos de trabajo
    return render_template('index_empleados.html', puestos_de_trabajo=puestos_de_trabajo, sucursales=sucursales)

@app_empleados.route('/empleados')
@check_permission('permiso_empleado')
def empleados():
    search_query = request.args.get('search', '')  # Obtiene el término de búsqueda
    search_criteria = request.args.get('search_criteria', 'id_empleado')  # Obtiene el criterio de búsqueda
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 5))

    # Si hay un término de búsqueda, realiza la búsqueda
    if search_query:
        empleados, total_empleados = search_users(search_query, search_criteria, page, per_page)
    else:
        empleados, total_empleados = get_empleados(page, per_page)

    total_pages = (total_empleados + per_page - 1) // per_page
    return render_template('empleados.html', empleados=empleados, search_query=search_query, 
                           search_criteria=search_criteria, page=page, per_page=per_page, 
                           total_empleados=total_empleados, total_pages=total_pages)

@app_empleados.route('/submit', methods=['POST'])
@check_permission('permiso_empleado')
def submit():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    id_puesto = request.form.get('id_puesto')
    fecha_contratacion = request.form.get('fecha_contratacion')
    id_sucursal = request.form.get('id_sucursal')  # Usando id_sucursal
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    tipo = request.form.get('tipo')
    documento = request.form.get('documento')
    password = request.form.get('password')

    
    if insert_user(nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password):
        flash("Empleado agregado correctamente.")
    else:
        flash("Error al agregar el empleado.")

    return redirect(url_for('empleados'))


@app_empleados.route('/edit_empleados/<int:id_empleado>', methods=['GET', 'POST'])
@check_permission('permiso_empleado')
def edit_empleados(id_empleado):
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    id_puesto = request.form.get('id_puesto')
    fecha_contratacion = request.form.get('fecha_contratacion')
    id_sucursal = request.form.get('id_sucursal')  # Usando id_sucursal
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    tipo = request.form.get('tipo')
    documento = request.form.get('documento')
    password = request.form.get('password')



    empleado = get_empleados_by_id(id_empleado)
    if not empleado:
        flash("Empleado no encontrado.")
        return redirect(url_for('empleados'))
    
    if update_user(id_empleado, nombre, apellido, fecha_nacimiento, id_puesto, fecha_contratacion, id_sucursal, email, telefono, tipo, documento, password):
        flash('Usuario actualizado exitosamente.')
    else:
        flash('Ocurrió un error al actualizar el usuario.')
    
    sucursales = get_sucursales()
    puestos_de_trabajo = get_puestos_de_trabajo()
    return render_template('edit_empleados.html', empleado=empleado, puestos_de_trabajo=puestos_de_trabajo, sucursales=sucursales)

@app_empleados.route('/eliminar_empleados/<int:id_empleado>', methods=['GET', 'POST'])
@check_permission('permiso_empleado')
def eliminar_empleados(id_empleado):
    if request.method == 'POST':
        if delete_user(id_empleado):
            flash('¡empleados eliminada exitosamente!')
            return redirect(url_for('empleados'))
        else:
            flash('Ocurrió un error al eliminar el empleados. Por favor, intente nuevamente.')
            return redirect(url_for('empleados'))

    empleados = get_empleados_by_id(id_empleado)
    if empleados is None:
        flash('empleados no encontrada.')
        return redirect(url_for('empleados'))

    return render_template('eliminar_empleados.html', empleados=empleados)

@app_empleados.route('/descargar_excel_empleados')
@check_permission('permiso_empleado')
def descargar_excel_empleados():
    # Obtener todas las empleados sin paginación
    empleados, total_empleados = get_todos_los_empleados()  # Ajuste para aceptar los dos valores

    if total_empleados == 0:
        flash('No hay empleados para descargar.')
        return redirect(url_for('empleados'))


    # Definir las columnas correctas
    columnas = [
        'ID Empleado', 'Nombre', 'Apellido', 'Fecha de Nacimiento', 'Puesto de Trabajo', 
        'Fecha de Contratación', 'Ciudad de Sucursal', 'Email', 'Teléfono', 'Tipo', 'Documento'
    ]
    # Crear un DataFrame con los datos de las empleados
    df = pd.DataFrame(empleados, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='empleados', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['empleados']
        bold_format = workbook.add_format({'bold': True})


        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de empleados', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='empleados.xlsx')

def get_todos_los_empleados():
    connection = create_connection()
    if connection is None:
        return [], 0

    cursor = connection.cursor()
    query = """
    SELECT e.id_empleado, e.nombre, e.apellido, e.fecha_nacimiento, 
           pt.puesto_trabajo AS puesto_trabajo, 
           e.fecha_contratacion, 
           s.ciudad AS ciudad_sucursal, 
           e.email, e.telefono, e.tipo, e.documento
    FROM empleados e
    JOIN puesto_de_trabajo pt ON e.id_puesto = pt.id_puesto
    JOIN sucursales s ON e.id_sucursal = s.id_sucursal
    ORDER BY e.id_empleado DESC
    """
    try:
        cursor.execute(query)
        empleados = cursor.fetchall()
        
        # Debugging output
        print("Fetched empleados data:", empleados)
        
        total_empleados = len(empleados)
        return empleados, total_empleados
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()



def get_todos_empleados():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT id_empleado, nombre, apellido, fecha_nacimiento, id_puesto,
               fecha_contratacion, id_sucursal, email, telefono, tipo, documento 
        FROM empleados
    """
    try:
        cursor.execute(query)
        empleados = cursor.fetchall()
        return empleados
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_empleados.route('/descargar_pdf')
@check_permission('permiso_empleado')
def descargar_pdf():
    # Obtener todos los empleados y dividir en páginas de 10
    empleados = get_todos_empleados()
    paginacion = [empleados[i:i + 10] for i in range(0, len(empleados), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto = landscape(A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primer_nombre = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, empleados_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Empleados")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {primer_nombre}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Empleados
        data = [["ID", "Nombre", "Apellido", "Fecha Nacimiento", "Puesto", "Fecha Contratación", 
                 "Sucursal", "Email", "Teléfono", "Tipo", "Documento"]]  # Encabezado de la tabla
        data += [[emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6], emp[7], emp[8], emp[9], emp[10]] 
                 for emp in empleados_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[0.8 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1 * inch, 
                                       1.2 * inch, 1 * inch, 1.5 * inch, 1.2 * inch, 1 * inch, 1 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Empleados.pdf')


if __name__ == '__main__':
    app_empleados.run(debug=True,port=5003)
