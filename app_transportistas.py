from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import mysql.connector
from mysql.connector import Error
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from io import BytesIO
import re

app_transportistas = Flask(__name__)
app_transportistas.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/transportistas'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="transportistas", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="transportistas"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def transportistas_exists(id_transportista):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM transportistas WHERE id_transportista = %s"
    cursor.execute(query, (id_transportista,))
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

def get_transportista(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = "SELECT * FROM transportistas LIMIT %s OFFSET %s"
    
    try:
        cursor.execute(query, (per_page, offset))
        transportistas = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM transportistas")
        total_count = cursor.fetchone()[0]

        return transportistas, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_transportista_by_id(id_transportista):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM transportistas WHERE id_transportista = %s"
    try:
        cursor.execute(query, (id_transportista,))
        transportista = cursor.fetchone()
        return transportista
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_transportista(nombre_empresa, telefono):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()

    # Asegura el formato del teléfono
    telefono = telefono.replace("-", "")  # Usa el nombre de variable correcto
    if len(telefono) == 8:
        telefono = telefono[:4] + '-' + telefono[4:]

    query = "INSERT INTO transportistas (nombre_empresa, Telefono) VALUES (%s, %s)"
    values = (nombre_empresa, telefono)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre Empresa: {nombre_empresa}, Teléfono: {telefono}"
        log_action('Inserted', screen_name='transportistas', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_transportista(id_transportista, nombre_empresa, Telefono):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "UPDATE transportistas SET nombre_empresa = %s, Telefono = %s WHERE id_transportista = %s"
    values = (nombre_empresa, Telefono, id_transportista)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Transportista: {id_transportista}, Nombre Empresa: {nombre_empresa}, Teléfono: {Telefono}"
        log_action('Updated', screen_name='transportistas', details=details)  # Registro de log
        print(f"Updated {cursor.rowcount} rows")  
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_transportista(id_transportista):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM transportistas WHERE id_transportista = %s"
    try:
        cursor.execute(query, (id_transportista,))
        connection.commit()
        details = f"ID Transportista: {id_transportista}"
        log_action('Deleted', screen_name='transportistas', details=details)  # Registro de log
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def search_transportistas(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Asegúrate de que el search_criteria esté en la lista de campos válidos
    if search_criteria not in ['nombre_empresa', 'Telefono']:
        search_criteria = 'nombre_empresa'  # Valor por defecto si el criterio de búsqueda es inválido

    if search_criteria == 'Telefono':
        # Usa REPLACE para eliminar los guiones de la base de datos durante la búsqueda
        query = f"""
        SELECT * FROM transportistas
        WHERE REPLACE(Telefono, '-', '') LIKE %s
        LIMIT %s OFFSET %s
        """
        count_query = f"""
        SELECT COUNT(*) FROM transportistas
        WHERE REPLACE(Telefono, '-', '') LIKE %s
        """
        search_query = search_query.replace('-', '')  # Elimina los guiones del query del usuario
    else:
        query = f"SELECT * FROM transportistas WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
        count_query = f"SELECT COUNT(*) FROM transportistas WHERE {search_criteria} LIKE %s"
    
    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        transportistas = cursor.fetchall()

        cursor.execute(count_query, (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return transportistas, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def empresa_existe(nombre_empresa):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM transportistas WHERE nombre_empresa = %s"
    try:
        cursor.execute(query, (nombre_empresa,))
        count = cursor.fetchone()[0]
        return count > 0  # Retorna True si existe, False si no existe
    except Error as e:
        print(f"The error '{e}' occurred")
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


def validate_input(field_value, field_type='text'):
    if not field_value:
        return 'El campo es obligatorio.'
    
    if field_type == 'text':
        if len(field_value) < 3 or len(field_value) > 20:
            return 'El campo debe tener entre 3 y 20 caracteres.'
        if re.search(r'\d', field_value):
            return 'El campo no debe contener números.'
        if re.search(r'(.)\1{2,}', field_value):
            return 'El campo no debe tener tres letras repetidas.'
        if re.search(r'[!?@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?]', field_value):
            return 'El campo no debe contener signos especiales.'
    
    elif field_type == 'telefono':
        clean_value = field_value.replace('-', '')
        if len(clean_value) != 8 or not clean_value.isdigit():
            return 'El campo Teléfono debe ser numérico y tener exactamente 8 dígitos.'
        if clean_value[0] not in '9382':
            return 'El primer número del Teléfono debe ser 9, 3, 8 o 2.'
        if re.search(r'(.)\1{3,}', clean_value):  # Validar más de 4 números consecutivos repetidos
            return 'El campo Teléfono no debe tener más de 4 números repetidos consecutivos.'
    
    elif field_type == 'document':
        if not field_value.isdigit():
            return 'El campo Documento debe ser numérico.'
    
    return ''  # Devuelve una cadena vacía si no hay errores




@app_transportistas.route('/')
@check_permission('permiso_transportista')
def index_transportistas():
    return render_template('index_transportistas.html')

@app_transportistas.route('/transportistas')
@check_permission('permiso_transportista')
def transportistas():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if search_criteria and search_query:
        transportistas, total_count = search_transportistas(search_criteria, search_query, page, per_page)
    else:
        transportistas, total_count = get_transportista(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('transportistas.html', transportistas=transportistas, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_transportistas.route('/submit', methods=['POST'])
@check_permission('permiso_transportista')
def submit_transportista():
    nombre_empresa = request.form['nombre_empresa']
    telefono = request.form['Telefono']

    # Validaciones
    error_nombre = validate_input(nombre_empresa, 'text')
    error_telefono = validate_input(telefono, 'telefono')

    # Verificar si la empresa ya existe
    if empresa_existe(nombre_empresa):
        flash('El nombre de la empresa ya existe. Por favor, elige otro nombre.')
        return redirect(url_for('index_transportistas'))

    if error_nombre or error_telefono:
        flash(' '.join(filter(None, [error_nombre, error_telefono])))
        return redirect(url_for('index_transportistas'))

    # Inserta el transportista en la base de datos
    if insert_transportista(nombre_empresa, telefono):
        flash('Transportista insertado correctamente!')
    else:
        flash('Ocurrió un error al insertar el transportista.')

    return redirect(url_for('index_transportistas'))

@app_transportistas.route('/edit_transportista/<int:id_transportista>', methods=['GET', 'POST'])
@check_permission('permiso_transportista')
def edit_transportista(id_transportista):
    if request.method == 'POST':
        nombre_empresa = request.form['nombre_empresa']
        telefono = request.form['Telefono']

        # Validaciones
        error_nombre = validate_input(nombre_empresa, 'text')
        error_telefono = validate_input(telefono, 'telefono')

        # Verificar si el nuevo nombre ya existe, pero omitir el transportista actual
        transportista_actual = get_transportista_by_id(id_transportista)
        if transportista_actual and transportista_actual[1] != nombre_empresa and empresa_existe(nombre_empresa):
            flash('El nombre de la empresa ya existe. Por favor, elige otro nombre.')
            return redirect(url_for('edit_transportista', id_transportista=id_transportista))

        if error_nombre or error_telefono:
            flash(' '.join(filter(None, [error_nombre, error_telefono])))
            return redirect(url_for('edit_transportista', id_transportista=id_transportista))

        if update_transportista(id_transportista, nombre_empresa, telefono):
            flash('Transportista actualizado correctamente!')
        else:
            flash('Error al actualizar el transportista.')

        return redirect(url_for('transportistas'))

    transportista = get_transportista_by_id(id_transportista)
    if not transportista:
        flash('Transportista no encontrado.')
        return redirect(url_for('transportistas'))

    return render_template('edit_transportista.html', transportista=transportista)

@app_transportistas.route('/eliminar_transportista/<int:id_transportista>', methods=['GET', 'POST'])
@check_permission('permiso_transportista')
def eliminar_transportista(id_transportista):
    # Obtiene el transportista por ID para mostrarlo en la confirmación de eliminación
    transportista = get_transportista_by_id(id_transportista)
    
    if transportista is None:
        flash('Transportista no encontrado.')
        return redirect(url_for('transportistas'))

    if request.method == 'POST':
        if delete_transportista(id_transportista):  # Asumiendo que esta es la función que elimina el transportista
            flash('Transportista eliminado correctamente!')
        else:
            flash('Error al eliminar el transportista.')
        return redirect(url_for('transportistas'))

    return render_template('eliminar_transportista.html', transportista=transportista)

def get_todos_transportistas():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = "SELECT id_transportista, nombre_empresa, Telefono FROM transportistas"
    try:
        cursor.execute(query)
        transportistas = cursor.fetchall()
        return transportistas
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_transportistas.route('/descargar_excel')
@check_permission('permiso_transportista')
def descargar_excel():
    # Obtener todas las transportistas sin paginación
    transportistas = get_todos_transportistas()  # Función para obtener todas las transportistas

    if not transportistas:
        flash('No hay nada en el transportistas para descargar.')
        return redirect(url_for('transportistas'))  # Asegúrate de que la ruta 'transportistas' está bien definida

    # Definir las columnas correctas
    columnas = ['id_transportistas',' Nombre de Empresa','Telefono']

    # Crear un DataFrame con los datos de las transportistas
    df = pd.DataFrame(transportistas, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='transportistas', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['transportistas']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de transportistas' , bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='transportistas.xlsx')


# Ruta para generar el PDF
@app_transportistas.route('/descargar_transportistas_pdf')
@check_permission('permiso_transportista')
def descargar_transportistas_pdf():
    # Obtener todos los transportistas y dividir en páginas de 10
    transportistas = get_todos_transportistas()
    paginacion = [transportistas[i:i + 10] for i in range(0, len(transportistas), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, transportistas_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Transportistas")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Transportistas
        data = [["ID", "Nombre Empresa", "Teléfono"]]  # Encabezado de la tabla
        data += [[transportista[0], transportista[1], transportista[2]] for transportista in transportistas_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1.5 * inch, 3 * inch, 2 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Transportistas.pdf')


if __name__ == '__main__':
    app_transportistas.run(debug=True,port=5013)
