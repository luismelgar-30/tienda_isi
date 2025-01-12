from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import pandas as pd


app_impuesto = Flask(__name__)
app_impuesto.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/impuesto'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="impuesto", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="impuesto"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def impuesto_exists(id_impuesto):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM impuesto WHERE id_impuesto = %s"
    cursor.execute(query, (id_impuesto,))
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

def insert_user(tipo_impuesto, tasa_impuesto):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    query = "INSERT INTO impuesto (tipo_impuesto, tasa_impuesto) VALUES (%s, %s)"
    values = (tipo_impuesto, tasa_impuesto)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Tipo de Impuesto: {tipo_impuesto}, Tasa de Impuesto: {tasa_impuesto}"
        log_action('Inserted', screen_name='impuesto', details=details)
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_user(id_impuesto, tipo_impuesto, tasa_impuesto):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    query = "UPDATE impuesto SET tipo_impuesto = %s, tasa_impuesto = %s WHERE id_impuesto = %s"
    values = (tipo_impuesto, tasa_impuesto, id_impuesto)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Impuesto: {id_impuesto}, Tipo de Impuesto: {tipo_impuesto}, Tasa de Impuesto: {tasa_impuesto}"
        log_action('Updated', screen_name='impuesto', details=details)
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_user(id_impuesto):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    query = "DELETE FROM impuesto WHERE id_impuesto = %s"

    try:
        cursor.execute(query, (id_impuesto,))
        connection.commit()
        details = f"ID Impuesto: {id_impuesto}"
        log_action('Deleted', screen_name='impuesto', details=details)
        return True
    except Error as e:
        error_message = f"Error al eliminar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def get_impuesto(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS id_impuesto, tipo_impuesto, tasa_impuesto FROM impuesto LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        impuesto = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_impuesto = cursor.fetchone()[0]
        return impuesto, total_impuesto
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_impuesto(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"SELECT SQL_CALC_FOUND_ROWS * FROM impuesto WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        impuesto = cursor.fetchall()
        cursor.execute(f"SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return impuesto, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_impuesto_by_id(id_impuesto):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT id_impuesto, tipo_impuesto, tasa_impuesto FROM impuesto WHERE id_impuesto = %s"
    cursor.execute(query, (id_impuesto,))
    impuesto = cursor.fetchone()
    cursor.close()
    connection.close()
    return impuesto

def get_historico_impuestos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM historicos_impuestos LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        historico_impuestos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_historico_impuestos = cursor.fetchone()[0]
        return historico_impuestos, total_historico_impuestos
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

@app_impuesto.route('/historico_impuestos')
@check_permission('permiso_impuesto')
def historico_impuestos():
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10))
    historicos, total_historicos = get_historico_impuestos(page, per_page)

    total_pages = (total_historicos + per_page - 1) // per_page
    return render_template('historico_impuestos.html', historicos=historicos, page=page, per_page=per_page, total_historicos=total_historicos, total_pages=total_pages)


@app_impuesto.route('/')
@check_permission('permiso_impuesto')
def index_impuesto():
    return render_template('index_impuesto.html')

@app_impuesto.route('/impuesto')
@check_permission('permiso_impuesto')
def impuesto():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    if search_query:
        impuesto, total_count = search_impuesto(search_criteria, search_query, page, per_page)
    else:
        impuesto, total_count = get_impuesto(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('impuesto.html', impuesto=impuesto, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)


@app_impuesto.route('/submit', methods=['POST'])
@check_permission('permiso_impuesto')
def submit():
    tipo_impuesto = request.form['tipo_impuesto']
    tasa_impuesto = request.form['tasa_impuesto']
    
    # Verificar si el impuesto seleccionó "Otro" y llenó el campo de texto adicional
    if tipo_impuesto == "Otro":
        tipo_impuesto = request.form['otro_tipo_impuesto']
    
    if tasa_impuesto == "Otro":
        tasa_impuesto = request.form['otro_tasa_impuesto']

    # Insertar en la base de datos
    if insert_user(tipo_impuesto, tasa_impuesto):
        flash('Impuesto ingresado exitosamente.')
    else:
        flash('Ocurrió un error al ingresar el impuesto.')
    
    return redirect(url_for('impuesto'))


@app_impuesto.route('/edit_impuesto/<int:id_impuesto>', methods=['GET', 'POST'])
@check_permission('permiso_impuesto')
def edit_impuesto(id_impuesto):
    if request.method == 'POST':
        tipo_impuesto = request.form['tipo_impuesto']
        tasa_impuesto = request.form['tasa_impuesto']


        if update_user(id_impuesto, tipo_impuesto, tasa_impuesto):
            flash('impuesto actualizado exitosamente.')
        else:
            flash('Ocurrió un error al actualizar el impuesto.')
        
        return redirect(url_for('impuesto'))

    impuesto = get_impuesto_by_id(id_impuesto)
    if impuesto is None:
        flash('impuesto no encontrado.')
        return redirect(url_for('impuesto'))
    return render_template('edit_impuesto.html', impuesto=impuesto)


@app_impuesto.route('/eliminar_impuesto/<int:id_impuesto>', methods=['GET', 'POST'])
@check_permission('permiso_impuesto')
def eliminar_impuesto(id_impuesto):
    if request.method == 'POST':
        if delete_user(id_impuesto):
            flash('¡impuesto eliminada exitosamente!')
            return redirect(url_for('impuesto'))
        else:
            flash('Ocurrió un error al eliminar el impuesto. Por favor, intente nuevamente.')
            return redirect(url_for('impuesto'))

    impuesto = get_impuesto_by_id(id_impuesto)
    if impuesto is None:
        flash('impuesto no encontrada.')
        return redirect(url_for('impuesto'))

    return render_template('eliminar_impuesto.html', impuesto=impuesto)

@app_impuesto.route('/descargar_excel')
@check_permission('permiso_impuesto')
def descargar_excel():

    # Obtener todas las impuesto sin paginación
    impuesto = get_todas_impuesto()  # Función para obtener todas las impuesto

    if not impuesto:
        flash('No hay impuesto para descargar.')
        return redirect(url_for('impuesto'))  # Asegúrate de que la ruta 'impuesto' está bien definida

    # Definir las columnas correctas
    columnas = ['id_impuesto',' tipo_impuesto',' tasa_impuesto']

    # Crear un DataFrame con los datos de las impuesto
    df = pd.DataFrame(impuesto, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='impuesto', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['impuesto']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de impuesto', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='impuesto.xlsx')


# Nueva función para obtener todas las impuesto sin límites
def get_todas_impuesto():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'impuesto'
    query = "SELECT SQL_CALC_FOUND_ROWS id_impuesto, tipo_impuesto, tasa_impuesto FROM impuesto"

    try:
        cursor.execute(query)
        impuesto = cursor.fetchall()  # Obtener todas las filas
        return impuesto
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
    
def get_todos_impuestos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = "SELECT  id_impuesto, tipo_impuesto, tasa_impuesto FROM impuesto"
    try:
        cursor.execute(query)
        impuesto = cursor.fetchall()
        return impuesto
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_impuesto.route('/descargar_pdf')
def descargar_pdf():
    # Obtener todos los transportistas y dividir en páginas de 10
    impuestos2 = get_todos_impuestos()
    paginacion = [impuestos2[i:i + 10] for i in range(0, len(impuestos2), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, impuestos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Impuestos")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Transportistas
        data = [["ID", "Tipo", "Tasa"]]  # Encabezado de la tabla
        data += [[impuestosC[0], impuestosC[1], impuestosC[2]] for impuestosC in impuestos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 3* inch, 3 * inch, 1* inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Impuestos.pdf')




if __name__ == '__main__':
    app_impuesto.run(debug=True,port=5024)
