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

app_puesto_de_trabajo = Flask(__name__)
app_puesto_de_trabajo.secret_key = 'your_secret_key'  # Cambia 'your_secret_key' por una clave secreta segura

LOGS_DIR = 'logs/puesto_de_trabajo'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="puesto_de_trabajo", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="puesto_de_trabajo"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def puesto_de_trabajo_exists(id_puesto):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM puesto_de_trabajo WHERE id_puesto = %s"
    cursor.execute(query, (id_puesto,))
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
    
def validate_salary(salario):
    try:
        salario_num = float(salario)
        if salario_num < 7000 or salario_num > 125000:
            return "El salario debe estar entre 7000 y 125000."
        return None
    except ValueError:
        return "El salario debe ser un número decimal válido."

def validate_time(hora):
    try:
        datetime.strptime(hora, '%H:%M')  # Asegúrate de que la hora tenga el formato correcto
        return None
    except ValueError:
        return "La hora debe estar en el formato HH:MM."


def validate_puesto_trabajo(puesto_trabajo):
    if not puesto_trabajo:
        return "El puesto de trabajo no puede estar vacío."
    
    if len(puesto_trabajo) < 3 or len(puesto_trabajo) > 20:
        return "El puesto de trabajo debe tener entre 3 y 20 caracteres."

    if not re.match("^[a-zA-Z\s]+$", puesto_trabajo):
        return "El puesto de trabajo solo debe contener letras y espacios."

    if re.search(r"(.)\1\1", puesto_trabajo):
        return "El puesto de trabajo no puede tener tres letras o espacios repetidos consecutivamente."

    if re.search(r"[aeiou]{2}", puesto_trabajo, re.IGNORECASE):
        return "El puesto de trabajo no puede tener dos vocales iguales consecutivas."

    return None
    
        

def get_puesto_de_trabajo(page, per_page, search_criteria=None, search_query=None):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    if search_criteria and search_query:
        query = f"""
            SELECT id_puesto, puesto_trabajo, hora_inicio, hora_fin, salario
            FROM puesto_de_trabajo
            WHERE {search_criteria} LIKE %s 
            LIMIT %s OFFSET %s
        """
        values = (f'%{search_query}%', per_page, offset)
    else:
        query = """
            SELECT id_puesto, puesto_trabajo, hora_inicio, hora_fin, salario
            FROM puesto_de_trabajo
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        cursor.execute(query, values)
        puesto_de_trabajo = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return puesto_de_trabajo, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def insert_puesto_de_trabajo(puesto_trabajo, hora_inicio, hora_fin, salario):
    conn = create_connection()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = conn.cursor()
    try:
        query = """INSERT INTO puesto_de_trabajo (puesto_trabajo, hora_inicio, hora_fin, salario) 
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (puesto_trabajo, hora_inicio, hora_fin, salario))
        conn.commit()
        details = f"Puesto: {puesto_trabajo}, Horario: {hora_inicio} - {hora_fin}, Salario: {salario}"
        log_action('Inserted', screen_name='puesto_de_trabajo', details=details)  # Registro de log
        print("Puesto de trabajo insertado con éxito")
        return True
    except Exception as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        conn.close()


def update_puesto_de_trabajo(id_puesto, puesto_trabajo, hora_inicio, hora_fin, salario):
    conn = create_connection()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = conn.cursor()
    try:
        query = """UPDATE puesto_de_trabajo 
                   SET puesto_trabajo=%s, hora_inicio=%s, hora_fin=%s, salario=%s 
                   WHERE id_puesto=%s"""
        cursor.execute(query, (puesto_trabajo, hora_inicio, hora_fin, salario, id_puesto))
        conn.commit()
        details = f"ID Puesto: {id_puesto}, Nuevo Puesto: {puesto_trabajo}, Horario: {hora_inicio} - {hora_fin}, Salario: {salario}"
        log_action('Updated', screen_name='puesto_de_trabajo', details=details)  # Registro de log
        print(f"Puesto {id_puesto} actualizado con éxito")
        return True
    except Exception as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        conn.close()


def delete_puesto_de_trabajo(id_puesto):
    conn = create_connection()
    if conn is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = conn.cursor()
    try:
        query = "DELETE FROM puesto_de_trabajo WHERE id_puesto=%s"
        cursor.execute(query, (id_puesto,))
        conn.commit()
        details = f"ID Puesto: {id_puesto}"
        log_action('Deleted', screen_name='puesto_de_trabajo', details=details)  # Registro de log
        print(f"Puesto {id_puesto} eliminado con éxito")
        return True
    except Exception as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        conn.close()



def get_puesto_de_trabajo_by_id(id_puesto):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM puesto_de_trabajo WHERE id_puesto=%s"
        cursor.execute(query, (id_puesto,))
        puesto = cursor.fetchone()
        if puesto:
            print(f"Puesto encontrado: {puesto}")
            return puesto
        else:
            print(f"No se encontró el puesto con ID {id_puesto}")
            return None
    except Exception as e:
        print(f"Error al obtener el puesto de trabajo: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


@app_puesto_de_trabajo.route('/')
@check_permission('permiso_puesto_trabajo')
def index_puesto_de_trabajo():
    return render_template('index_puesto_de_trabajo.html')

@app_puesto_de_trabajo.route('/submit', methods=['POST'])
@check_permission('permiso_puesto_trabajo')
def submit():
    puesto_trabajo = request.form.get('puesto_trabajo')
    hora_inicio = request.form.get('hora_inicio')
    hora_fin = request.form.get('hora_fin')
    salario = request.form.get('salario')

    # Validaciones
    validation_errors = []
    
    puesto_trabajo_error = validate_puesto_trabajo(puesto_trabajo)
    if puesto_trabajo_error:
        validation_errors.append(puesto_trabajo_error)

    hora_inicio_error = validate_time(hora_inicio)
    if hora_inicio_error:
        validation_errors.append(hora_inicio_error)

    hora_fin_error = validate_time(hora_fin)
    if hora_fin_error:
        validation_errors.append(hora_fin_error)

    salario_error = validate_salary(salario)
    if salario_error:
        validation_errors.append(salario_error)

    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect(url_for('index_puesto_de_trabajo'))

    try:
        salario_decimal = float(salario)  # Asegúrate de que el salario sea un número decimal
    except ValueError:
        flash('El salario debe ser un número decimal válido.')
        return redirect(url_for('index_puesto_de_trabajo'))
    
    if insert_puesto_de_trabajo(puesto_trabajo, hora_inicio, hora_fin, salario_decimal):
        flash('Puesto de trabajo agregado exitosamente!')
    else:
        flash('Error al agregar el puesto de trabajo.')

    return redirect(url_for('index_puesto_de_trabajo'))

@app_puesto_de_trabajo.route('/puesto_de_trabajo', methods=['GET'])
@check_permission('permiso_puesto_trabajo')
def puesto_de_trabajo():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Recoge el número de registros por página
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    
    puesto_de_trabajo, total_count = get_puesto_de_trabajo(page, per_page, search_criteria, search_query)
    
    # Calcular el total de páginas
    total_pages = (total_count + per_page - 1) // per_page
    
    return render_template(
        'puesto_de_trabajo.html',
        puesto_de_trabajo=puesto_de_trabajo,
        total_pages=total_pages,
        current_page=page,
        per_page=per_page  # Pasamos el número de registros por página a la plantilla
    )


@app_puesto_de_trabajo.route('/edit/<int:id_puesto>', methods=['GET', 'POST'])
@check_permission('permiso_puesto_trabajo')
def edit_puesto_de_trabajo(id_puesto):
    if request.method == 'POST':
        hora_inicio = request.form.get('hora_inicio')
        hora_fin = request.form.get('hora_fin')
        puesto_trabajo = request.form.get('puesto_trabajo')
        salario = request.form.get('salario')

        validation_errors = []
        
        hora_inicio_error = validate_time(hora_inicio)
        if hora_inicio_error:
            validation_errors.append(hora_inicio_error)

        hora_fin_error = validate_time(hora_fin)
        if hora_fin_error:
            validation_errors.append(hora_fin_error)

        salario_error = validate_salary(salario)
        if salario_error:
            validation_errors.append(salario_error)

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect(url_for('edit_puesto_de_trabajo', id_puesto=id_puesto))

        try:
            salario_decimal = float(salario)  # Asegúrate de que el salario sea un número decimal
        except ValueError:
            flash('El salario debe ser un número decimal válido.')
            return redirect(url_for('edit_puesto_de_trabajo', id_puesto=id_puesto))
        
        if update_puesto_de_trabajo(id_puesto, hora_inicio, hora_fin, puesto_trabajo, salario_decimal):
            flash('Puesto de trabajo actualizado exitosamente!')
        else:
            flash('Error al actualizar el puesto de trabajo.')
        
        return redirect(url_for('puesto_de_trabajo'))

    puesto_de_trabajo = get_puesto_de_trabajo_by_id(id_puesto)
    if puesto_de_trabajo is None:
        flash('Puesto de trabajo no encontrado.')
        return redirect(url_for('puesto_de_trabajo'))

    return render_template('edit_puesto_de_trabajo.html', puesto_de_trabajo=puesto_de_trabajo)

@app_puesto_de_trabajo.route('/delete/<int:id_puesto>', methods=['GET', 'POST'])
@check_permission('permiso_puesto_trabajo')
def delete_puesto_de_trabajo_route(id_puesto):
    # Verificar si el método es POST
    if request.method == 'POST':
        if delete_puesto_de_trabajo(id_puesto):
            flash('Puesto de trabajo eliminado exitosamente!')
        else:
            flash('Error al eliminar el puesto de trabajo.')
        return redirect(url_for('puesto_de_trabajo'))

    # Si el método no es POST, verificar si el puesto existe
    puesto_de_trabajo = get_puesto_de_trabajo_by_id(id_puesto)
    if puesto_de_trabajo is None:
        flash('Puesto de trabajo no encontrado.')
        return redirect(url_for('puesto_de_trabajo'))

    return render_template('eliminar_puesto_de_trabajo.html', puesto_de_trabajo=puesto_de_trabajo)

@app_puesto_de_trabajo.route('/descargar_excel')
@check_permission('permiso_puesto_trabajo')
def descargar_excel():
    # Obtener todas las puesto_de_trabajo sin paginación
    puesto_de_trabajo = get_todas_puesto_de_trabajos()  # Función para obtener todas las puesto_de_trabajo

    if not puesto_de_trabajo:
        flash('No hay puesto_de_trabajo para descargar.')
        return redirect(url_for('puesto_de_trabajo'))  # Asegúrate de que la ruta 'puesto_de_trabajo' está bien definida

    # Definir las columnas correctas
    columnas = ['id_puesto', 'puesto_trabajo', 'hora_inicio', 'hora_fin', 'salario']

    # Crear un DataFrame con los datos de las puesto_de_trabajo
    df = pd.DataFrame(puesto_de_trabajo, columns=columnas)

    # Imprimir los tipos de datos de las columnas hora
    print(df['hora_inicio'].dtype)
    print(df['hora_fin'].dtype)

    # Si hora_inicio y hora_fin son timedelta, convertimos a string en formato de hora
    if pd.api.types.is_timedelta64_dtype(df['hora_inicio']):
        df['hora_inicio'] = df['hora_inicio'].dt.total_seconds()  # convertir a segundos
        df['hora_inicio'] = pd.to_datetime(df['hora_inicio'], unit='s').dt.time  # convertir a tiempo

    if pd.api.types.is_timedelta64_dtype(df['hora_fin']):
        df['hora_fin'] = df['hora_fin'].dt.total_seconds()  # convertir a segundos
        df['hora_fin'] = pd.to_datetime(df['hora_fin'], unit='s').dt.time  # convertir a tiempo

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='puesto_de_trabajo', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['puesto_de_trabajo']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de puesto_de_trabajo', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='puesto_de_trabajo.xlsx')


# Nueva función para obtener todas las puesto_de_trabajo sin límites
def get_todas_puesto_de_trabajos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'puesto_de_trabajo'
    query = "SELECT id_puesto, puesto_trabajo, hora_inicio, hora_fin, salario FROM puesto_de_trabajo"

    try:
        cursor.execute(query)
        puesto_de_trabajo = cursor.fetchall()  # Obtener todas las filas
        return puesto_de_trabajo
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


@app_puesto_de_trabajo.route('/descargar_pdf')
@check_permission('permiso_puesto_trabajo')
def descargar_pdf():
    # Obtener todos los puestos y dividir en páginas de 10
    puestos = get_todos_los_puestos_pdf()
    paginacion = [puestos[i:i + 10] for i in range(0, len(puestos), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, puestos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Puestos de Trabajo")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Puestos
        data = [["ID Puesto", "Puesto", "Hora Inicio", "Hora Fin", "Salario"]]  # Encabezado de la tabla
        data += [[puesto[0], puesto[1], puesto[2], puesto[3], puesto[4]] for puesto in puestos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Puestos_de_Trabajo.pdf')

def get_todos_los_puestos_pdf():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = "SELECT id_puesto, puesto_trabajo, hora_inicio, hora_fin, salario FROM puesto_de_trabajo"
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


if __name__ == '__main__':
    app_puesto_de_trabajo.run(debug=True,port=5007)
