import datetime
from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import pandas as pd
from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime

app_equipo = Flask(__name__)
app_equipo.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/equipo'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="equipo", details=None):
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

def log_error(error_message, screen_name="equipo"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def equipo_exists(id_equipo):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM equipo WHERE id_equipo = %s"
    cursor.execute(query, (id_equipo,))
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


def get_equipos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM equipo LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        equipos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_equipos = cursor.fetchone()[0]
        return equipos, total_equipos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_equipo_by_id(id_equipo):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM equipo WHERE id_equipo = %s"
    try:
        cursor.execute(query, (id_equipo,))
        equipo = cursor.fetchone()
        return equipo
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_equipo(id_equipo, tipo, modelo, numero_serie, estado):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO equipo (id_equipo, tipo, modelo, numero_serie, estado) 
               VALUES (?, ?, ?, ?, ?)"""
    
    try:
        cursor.execute(query, (id_equipo, tipo, modelo, numero_serie, estado))
        connection.commit()
        details = f"ID Equipo: {id_equipo}, Tipo: {tipo}, Modelo: {modelo}, Número de Serie: {numero_serie}, Estado: {estado}"
        log_action('Inserted', screen_name='equipo', details=details)  # Registro de log
        print("Inserción exitosa.")
        return True
    except Exception as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_equipo(id_equipo, tipo, modelo, numero_serie, estado):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = """UPDATE equipo SET tipo = ?, modelo = ?, numero_serie = ?, estado = ? 
               WHERE id_equipo = ?"""
    
    try:
        cursor.execute(query, (tipo, modelo, numero_serie, estado, id_equipo))
        connection.commit()
        details = f"ID Equipo: {id_equipo}, Tipo: {tipo}, Modelo: {modelo}, Número de Serie: {numero_serie}, Estado: {estado}"
        log_action('Updated', screen_name='equipo', details=details)  # Registro de log
        print("Actualización exitosa.")
        return True
    except Exception as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_equipo(id_equipo):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM equipo WHERE id_equipo = ?"
    
    try:
        cursor.execute(query, (id_equipo,))
        connection.commit()
        details = f"ID Equipo: {id_equipo}"
        log_action('Deleted', screen_name='equipo', details=details)  # Registro de log
        print("Eliminación exitosa.")
        return True
    except Exception as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


@app_equipo.route('/')
@check_permission('permiso_equipo')
def index_equipo():
    return render_template('index_equipo.html')

@app_equipo.route('/equipos')
@check_permission('permiso_equipo')
def equipos():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    if search_query:
        equipos, total_equipos = search_equipos(search_query, page, per_page)
    else:
        equipos, total_equipos = get_equipos(page, per_page)

    total_pages = (total_equipos + per_page - 1) // per_page
    return render_template('equipos.html', equipos=equipos, search_query=search_query, page=page, per_page=per_page, total_equipos=total_equipos, total_pages=total_pages)

@app_equipo.route('/submit', methods=['POST'])
@check_permission('permiso_equipo')
def submit():
    id_equipo = request.form['id_equipo']
    tipo = request.form['tipo']
    modelo = request.form['modelo']
    numero_serie = request.form['numero_serie']
    estado = request.form['estado']

    if not id_equipo or not tipo or not modelo or not numero_serie or not estado:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_equipo'))

    if insert_equipo(id_equipo, tipo, modelo, numero_serie, estado):
        flash('Equipo insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el equipo.')
    
    return redirect(url_for('equipo'))

@app_equipo.route('/edit_equipo/<int:id_equipo>', methods=['GET', 'POST'])
@check_permission('permiso_equipo')
def edit_equipo(id_equipo):
    if request.method == 'POST':
        tipo = request.form['tipo']
        modelo = request.form['modelo']
        numero_serie = request.form['numero_serie']
        estado = request.form['estado']

        if not tipo or not modelo or not numero_serie or not estado:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_equipo', id_equipo=id_equipo))

        if update_equipo(id_equipo, tipo, modelo, numero_serie, estado):
            flash('Equipo actualizado exitosamente!')
        else:
            flash('Ocurrió un error al actualizar el equipo.')
        
        return redirect(url_for('equipos'))

    equipo = get_equipo_by_id(id_equipo)
    if equipo is None:
        flash('Equipo no encontrado!')
        return redirect(url_for('equipos'))
    return render_template('edit_equipo.html', equipo=equipo)

@app_equipo.route('/eliminar_equipo/<int:id_equipo>', methods=['GET', 'POST'])
@check_permission('permiso_equipo')
def eliminar_equipo(id_equipo):
    if request.method == 'POST':
        if delete_equipo(id_equipo):
            flash('Equipo eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el equipo.')
        return redirect(url_for('equipos'))

    equipo = get_equipo_by_id(id_equipo)
    if equipo is None:
        flash('Equipo no encontrado!')
        return redirect(url_for('equipos'))
    return render_template('eliminar_equipo.html', equipo=equipo)

def search_equipos(search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    
    query = """
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM equipo 
    WHERE id_equipo LIKE %s 
       OR tipo LIKE %s 
       OR Modelo LIKE %s 
       OR numero_serie LIKE %s 
       OR estado LIKE %s
    LIMIT %s OFFSET %s
    """
    values = (
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        per_page, 
        offset
    )
    try:
        cursor.execute(query, values)
        equipos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_equipos = cursor.fetchone()[0]
        return equipos, total_equipos
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

@app_equipo.route('/descargar_excel')
@check_permission('permiso_equipo')
def descargar_excel():
    # Obtener todas las equipos sin paginación
    equipos = get_todas_equipos()  # Función para obtener todas las equipos

    if not equipos:
        flash('No hay equipos para descargar.')
        return redirect(url_for('equipos'))  # Asegúrate de que la ruta 'equipos' está bien definida

    # Definir las columnas correctas
    columnas = ['id_equipo', 'tipo', 'modelo',' numero_serie', 'estado']

    # Crear un DataFrame con los datos de las equipos
    df = pd.DataFrame(equipos, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='equipos', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['equipos']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de equipos', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='equipos.xlsx')


# Nueva función para obtener todas las equipos sin límites
def get_todas_equipos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'equipos'
    query = "SELECT id_equipo, tipo, modelo, numero_serie, estado FROM equipo"

    try:
        cursor.execute(query)
        equipos = cursor.fetchall()  # Obtener todas las filas
        return equipos
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_todos_equipos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT id_equipo, tipo, Modelo, numero_serie, estado
        FROM equipo
    """
    try:
        cursor.execute(query)
        equipos = cursor.fetchall()
        return equipos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_equipo.route('/descargar_pdf')
@check_permission('permiso_equipo')
def descargar_pdf():
    # Obtener todos los equipos y dividir en páginas de 10
    equipos = get_todos_equipos()
    paginacion = [equipos[i:i + 10] for i in range(0, len(equipos), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    ancho, alto = A3

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, equipos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Equipo")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Equipos
        data = [["ID", "Tipo", "Modelo", "Número de Serie", "Estado"]]  # Encabezado de la tabla
        data += [[equipo[0], equipo[1], equipo[2], equipo[3], equipo[4]] for equipo in equipos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 2 * inch, 2 * inch, 2 * inch, 1.5 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Equipo.pdf')


if __name__ == "__main__":
    app_equipo.run(debug=True,port=5020)
