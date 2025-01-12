from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash,send_file,session
import mysql.connector
from mysql.connector import Error
from io import BytesIO
import pandas as pd
import datetime
from flask import send_file, request
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime

app_sar = Flask(__name__)
app_sar.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/sar'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="sar", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="sar"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def sar_exists(id_sar):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM sar WHERE id_sar = %s"
    cursor.execute(query, (id_sar,))
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

def insert_sar(rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    INSERT INTO sar 
    (rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"RTN: {rtn}, CAI: {cai}, Rango: {rango_inicial}-{rango_final}, Sucursal ID: {id_sucursal}, Secuencial: {secuencial}, Estado: {estado}"
        log_action('Inserted', screen_name='sar', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return str(e)  # Cambia para devolver el mensaje de error
    finally:
        cursor.close()
        connection.close()

def update_sar(id_sar, rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE sar
    SET rtn = %s, cai = %s, fecha_emision = %s, fecha_vencimiento = %s, rango_inicial = %s, rango_final = %s, id_sucursal = %s, secuencial = %s, estado = %s
    WHERE id_sar = %s
    """
    values = (rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado, id_sar)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID SAR: {id_sar}, RTN: {rtn}, CAI: {cai}, Rango: {rango_inicial}-{rango_final}, Sucursal ID: {id_sucursal}, Secuencial: {secuencial}, Estado: {estado}"
        log_action('Updated', screen_name='sar', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_sar(id_sar):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM sar WHERE id_sar = %s"
    try:
        cursor.execute(query, (id_sar,))
        connection.commit()
        details = f"ID SAR: {id_sar}"
        log_action('Deleted', screen_name='sar', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def get_sar():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = """
    SELECT s.id_sar, s.rtn, s.cai, s.fecha_emision, s.fecha_vencimiento, s.rango_inicial, s.rango_final, su.ciudad, s.secuencial, s.estado
    FROM sar s
    JOIN sucursales su ON s.id_sucursal = su.id_sucursal
    """
    try:
        cursor.execute(query)
        sar = cursor.fetchall()
        return sar
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()

def get_sar_by_id(id_sar):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT s.id_sar, s.rtn, s.cai, 
           DATE_FORMAT(s.fecha_emision, '%Y-%m-%d'), 
           DATE_FORMAT(s.fecha_vencimiento, '%Y-%m-%d'), 
           s.rango_inicial, s.rango_final, 
           s.id_sucursal, s.secuencial, s.estado,
           su.ciudad
    FROM sar s
    JOIN sucursales su ON s.id_sucursal = su.id_sucursal
    WHERE s.id_sar = %s
    """
    try:
        cursor.execute(query, (id_sar,))
        sar = cursor.fetchone()
        return sar
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

@app_sar.route('/')
@check_permission('permiso_sar')
def index_sar():
    connection = create_connection()
    if connection is None:
        return render_template('index_sar.html', sucursales=[])
    cursor = connection.cursor()

    cursor.execute("SELECT id_sucursal, ciudad FROM sucursales")
    sucursales = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('index_sar.html', sucursales=sucursales)

@app_sar.route('/sars')
@check_permission('permiso_sar')
def sars():
    sar = get_sar()
    return render_template('sars.html', sar=sar)

@app_sar.route('/submit', methods=['POST'])
@check_permission('permiso_sar')
def submit():
    rtn = request.form['rtn']
    cai = request.form['cai']
    fecha_emision = request.form['fecha_emision']
    fecha_vencimiento = request.form['fecha_vencimiento']
    rango_inicial = request.form['rango_inicial']
    rango_final = request.form['rango_final']
    id_sucursal = request.form['id_sucursal']
    secuencial = request.form['secuencial']
    estado = request.form['estado']

    if not rtn or not cai or not fecha_emision or not fecha_vencimiento or not rango_inicial or not rango_final or not id_sucursal or not secuencial or not estado:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_sar'))

    if insert_sar(rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado):
        flash('SAR insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el SAR.')
    
    return redirect(url_for('index_sar'))

@app_sar.route('/edit_sar/<int:id_sar>', methods=['GET', 'POST'])
@check_permission('permiso_sar')
def edit_sar(id_sar):
    if request.method == 'POST':
        rtn = request.form['rtn']
        cai = request.form['cai']
        fecha_emision = request.form['fecha_emision']
        fecha_vencimiento = request.form['fecha_vencimiento']
        rango_inicial = request.form['rango_inicial']
        rango_final = request.form['rango_final']
        id_sucursal = request.form['id_sucursal']
        secuencial = request.form['secuencial']
        estado = request.form['estado']

        if not rtn or not cai or not fecha_emision or not fecha_vencimiento or not rango_inicial or not rango_final or not id_sucursal or not secuencial or not estado:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_sar', id_sar=id_sar))

        if update_sar(id_sar, rtn, cai, fecha_emision, fecha_vencimiento, rango_inicial, rango_final, id_sucursal, secuencial, estado):
            flash('SAR actualizado exitosamente!')
        else:
            flash('Ocurrió un error al actualizar el SAR.')
        
        return redirect(url_for('sars'))

    sar = get_sar_by_id(id_sar)
    if sar is None:
        flash('SAR no encontrado!')
        return redirect(url_for('sars'))

    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT id_sucursal, ciudad FROM sucursales")
    sucursales = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('edit_sar.html', sar=sar, sucursales=sucursales)

@app_sar.route('/eliminar_sar/<int:id_sar>', methods=['GET', 'POST'])
@check_permission('permiso_sar')
def eliminar_sar(id_sar):
    if request.method == 'POST':
        if delete_sar(id_sar):
            flash('SAR eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el SAR.')
        return redirect(url_for('sars'))

    sar = get_sar_by_id(id_sar)
    if sar is None:
        flash('SAR no encontrado!')
        return redirect(url_for('sars'))
    return render_template('eliminar_sar.html', sar=sar)

@app_sar.route('/descargar_excel_sar')
@check_permission('permiso_sar')
def descargar_excel_sar():
    # Obtener todas las sar sin paginación
    sar = get_sar()  # Función para obtener todas las sar

    if not sar:
        flash('No hay sar para descargar.')
        return redirect(url_for('sar'))  # Asegúrate de que la ruta 'sar' está bien definida

     # Definir las columnas correctas
    columnas = ['ID SAR', 'RTN', 'CAI', 'Fecha Emisión', 'Fecha Vencimiento', 'Rango Inicial', 'Rango Final', 'Ciudad', 'Secuencial', 'Estado']
    
    # Crear un DataFrame con los datos de las sar
    df = pd.DataFrame(sar, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='sar', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['sar']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de sar', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='sar.xlsx')

def get_todos_sar():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query =  """
    SELECT s.id_sar, s.rtn, s.cai, s.fecha_emision, s.fecha_vencimiento, s.rango_inicial, s.rango_final, su.ciudad, s.secuencial, s.estado
    FROM sar s
    JOIN sucursales su ON s.id_sucursal = su.id_sucursal
    """
    try:
        cursor.execute(query)
        sar_records = cursor.fetchall()
        return sar_records
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_sar.route('/descargar_pdf')
@check_permission('permiso_sar')
def descargar_pdf():
    # Obtener todos los registros SAR y dividir en páginas de 10
    sar_records = get_todos_sar()
    paginacion = [sar_records[i:i + 10] for i in range(0, len(sar_records), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto = landscape(A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, sar_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "SAR")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla SAR
        data = [["ID SAR", "RTN", "CAI", "Fecha Emisión", "Fecha Vencimiento", "Rango Inicial", "Rango Final", "ID Sucursal", "Secuencial", "Estado"]]
        data += [[record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9]] for record in sar_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[0.8 * inch, 1.2 * inch, 4 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch, 1 * inch, 1 * inch, 0.8 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='SAR.pdf')


if __name__ == "__main__":
    app_sar.run(debug=True, port=5027)
