from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from datetime import datetime, date
from mysql.connector import Error
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import pandas as pd

app_capacitacion = Flask(__name__)
app_capacitacion.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/capacitaciones'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="capacitaciones", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="capacitacion"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def capacitacion_exists(tema, fecha_capacitacion, id_empleado):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM capacitacion WHERE tema = %s AND fecha_capacitacion = %s AND id_empleado = %s"
    cursor.execute(query, (tema, fecha_capacitacion, id_empleado))
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

def validate_text_field(text):
    # Check length
    if len(text) < 3 or len(text) > 20:
        return False, "El campo debe tener entre 3 y 20 caracteres."
    
    # Check for digits
    if any(char.isdigit() for char in text):
        return False, "El campo no puede contener números."

    # Check for special characters
    if not re.match("^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$", text):
        return False, "El campo no puede contener caracteres especiales."

    return True, ""

def insert_capacitacion(id_empleado, tema, fecha_capacitacion, duracion, resultado):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()

    query = """
    INSERT INTO capacitacion (id_empleado, tema, fecha_capacitacion, duracion, resultado)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (id_empleado, tema, fecha_capacitacion, duracion, resultado)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la inserción
        details = f"Empleado ID: {id_empleado}, Tema: {tema}, Fecha: {fecha_capacitacion}, Duración: {duracion}, Resultado: {resultado}"
        log_action('Inserted', screen_name='capacitacion', details=details)  # Registro de la acción de inserción

        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def get_capacitaciones(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = """
    SELECT c.id_capacitacion, e.nombre, c.tema, c.fecha_capacitacion, c.duracion, c.resultado
    FROM capacitacion c
    JOIN empleados e ON c.id_empleado = e.id_empleado
    LIMIT %s OFFSET %s
    """
    
    try:
        cursor.execute(query, (per_page, offset))
        capacitaciones = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM capacitacion")
        total_count = cursor.fetchone()[0]

        return capacitaciones, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_capacitacion_by_id(id_capacitacion):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM capacitacion WHERE id_capacitacion = %s"
    try:
        cursor.execute(query, (id_capacitacion,))
        capacitacion = cursor.fetchone()
        return capacitacion
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def update_capacitacion(id_capacitacion, id_empleado, tema, fecha_capacitacion, duracion, resultado):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = """
            UPDATE capacitacion
            SET id_empleado = %s, tema = %s, fecha_capacitacion = %s, duracion = %s, resultado = %s
            WHERE id_capacitacion = %s
        """
        values = (id_empleado, tema, fecha_capacitacion, duracion, resultado, id_capacitacion)
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"Capacitación ID: {id_capacitacion}, Empleado ID: {id_empleado}, Tema: {tema}, Fecha: {fecha_capacitacion}, Duración: {duracion}, Resultado: {resultado}"
        log_action('Updated', screen_name='capacitacion', details=details)  # Registro de la acción de actualización

        return True
    except Exception as e:
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_capacitacion(id_capacitacion):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Obtener detalles de la capacitación antes de eliminar para el log
        cursor.execute("SELECT id_empleado, tema, fecha_capacitacion, duracion, resultado FROM capacitacion WHERE id_capacitacion = %s", (id_capacitacion,))
        capacitacion = cursor.fetchone()
        
        if not capacitacion:
            print("Capacitación no encontrada")
            return False

        query = "DELETE FROM capacitacion WHERE id_capacitacion = %s"
        cursor.execute(query, (id_capacitacion,))
        connection.commit()

        # Registro en logs después de la eliminación
        id_empleado, tema, fecha_capacitacion, duracion, resultado = capacitacion
        details = f"Capacitación ID: {id_capacitacion}, Empleado ID: {id_empleado}, Tema: {tema}, Fecha: {fecha_capacitacion}, Duración: {duracion}, Resultado: {resultado}"
        log_action('Deleted', screen_name='capacitacion', details=details)  # Registro de la acción de eliminación

        return True
    except Exception as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()
        
def get_empleados():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_empleado, nombre FROM empleados"
    try:
        cursor.execute(query)
        empleados = cursor.fetchall()
        print("Empleados obtenidos:", empleados)  # Verificar datos obtenidos
        return empleados
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()



def search_capacitaciones(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Ajusta la consulta para incluir el campo nombre del empleado
    query = f"""
    SELECT c.id_capacitacion, e.nombre, c.tema, c.fecha_capacitacion, c.duracion, c.resultado
    FROM capacitacion c
    JOIN empleados e ON c.id_empleado = e.id_empleado
    WHERE {search_criteria} LIKE %s 
    LIMIT %s OFFSET %s
    """
    
    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        capacitaciones = cursor.fetchall()

        # Ajusta el conteo total para considerar la búsqueda en la tabla de empleados
        count_query = f"""
        SELECT COUNT(*)
        FROM capacitacion c
        JOIN empleados e ON c.id_empleado = e.id_empleado
        WHERE {search_criteria} LIKE %s
        """
        cursor.execute(count_query, (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return capacitaciones, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()



@app_capacitacion.route('/')
@check_permission('permiso_capacitacion')
def index_capacitacion():
    empleados = get_empleados()  # Obtiene la lista de empleados
    today = datetime.now().strftime('%Y-%m-%dT%H:%M')  # Formatea la fecha actual para el input datetime-local
    return render_template('index_capacitacion.html', empleados=empleados, today=today)

@app_capacitacion.route('/capacitaciones')
@check_permission('permiso_capacitacion')
def capacitaciones():
    search_query = request.args.get('search_query')
    search_criteria = request.args.get('search_criteria', 'tema')  # Aquí puedes definir un criterio predeterminado, como 'tema'
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if search_query:
        capacitaciones, total_count = search_capacitaciones(search_criteria, search_query, page, per_page)
    else:
        capacitaciones, total_count = get_capacitaciones(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('capacitaciones.html', capacitaciones=capacitaciones, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_capacitacion.route('/submit', methods=['POST'])
@check_permission('permiso_capacitacion')
def submit_capacitacion():
    id_empleado = request.form['id_empleado']
    tema = request.form['tema']
    fecha_capacitacion = request.form['fecha_capacitacion']
    duracion = request.form['duracion']
    resultado = request.form['resultado']

    # Validaciones
    errors = []
    if not tema or not re.match(r'^[a-zA-Z\s]+$', tema):
        errors.append('El tema debe ser texto sin números ni símbolos.')
    
    if not resultado.isdigit():
        errors.append('El resultado debe ser un número entero.')

    try:
        # Ajustar el formato a 'YYYY-MM-DDTHH:MM' para datetime-local
        fecha = datetime.strptime(fecha_capacitacion, '%Y-%m-%dT%H:%M')
        if fecha < datetime.now():
            errors.append('La fecha de capacitación no puede ser en el pasado.')
    except ValueError:
        errors.append('El formato de la fecha es incorrecto.')

    if errors:
        flash(' '.join(errors))
        return redirect(url_for('index_capacitacion'))

    # Inserta la capacitación en la base de datos
    if insert_capacitacion(id_empleado, tema, fecha_capacitacion, duracion, resultado):
        flash('Capacitación insertada correctamente!')
    else:
        flash('Ocurrió un error al insertar la capacitación.')

    return redirect(url_for('index_capacitacion'))


@app_capacitacion.route('/edit/<int:id_capacitacion>', methods=['GET', 'POST'])
@check_permission('permiso_capacitacion')
def edit_capacitacion(id_capacitacion):
    if request.method == 'POST':
        id_empleado = request.form['id_empleado']
        tema = request.form['tema']
        fecha_capacitacion = request.form['fecha_capacitacion']
        duracion = request.form['duracion']
        resultado = request.form['resultado']

        # Validaciones
        errors = []
        if not tema or not re.match(r'^[a-zA-Z\s]+$', tema):
            errors.append('El tema debe ser texto sin números ni símbolos.')
        
        if not resultado.isdigit():
            errors.append('El resultado debe ser un número entero.')

        try:
            fecha = datetime.strptime(fecha_capacitacion, '%Y-%m-%dT%H:%M')
            if fecha < datetime.now():
                errors.append('La fecha de capacitación no puede ser en el pasado.')
        except ValueError:
            errors.append('El formato de la fecha es incorrecto.')

        if errors:
            flash(' '.join(errors))
            return redirect(url_for('edit_capacitacion', id_capacitacion=id_capacitacion))

        if update_capacitacion(id_capacitacion, id_empleado, tema, fecha_capacitacion, duracion, resultado):
            flash('Capacitación actualizada correctamente!')
        else:
            flash('Ocurrió un error al actualizar la capacitación.')
        return redirect(url_for('capacitaciones'))

    capacitacion = get_capacitacion_by_id(id_capacitacion)
    empleados = get_empleados()
    today = datetime.now().strftime('%Y-%m-%dT%H:%M')

    # Asegúrate de que los datos sean correctos
    if not capacitacion:
        flash('Capacitación no encontrada!')
        return redirect(url_for('capacitaciones'))

    return render_template('edit_capacitacion.html', capacitacion=capacitacion, empleados=empleados, today=today)

@app_capacitacion.route('/eliminar/<int:id_capacitacion>', methods=['GET', 'POST'])
@check_permission('permiso_capacitacion')
def eliminar_capacitacion(id_capacitacion):
    if request.method == 'POST':
        if delete_capacitacion(id_capacitacion):
            flash('Capacitación eliminada exitosamente!')
        else:
            flash('Ocurrió un error al eliminar la capacitación.')
        return redirect(url_for('capacitaciones'))

    capacitacion = get_capacitacion_by_id(id_capacitacion)
    if capacitacion is None:
        flash('Capacitación no encontrada!')
        return redirect(url_for('capacitaciones'))
    
    return render_template('eliminar_capacitacion.html', capacitacion=capacitacion)

@app_capacitacion.route('/descargar_excel')
@check_permission('permiso_capacitacion')
def descargar_excel():
    # Obtener todas las capacitacion sin paginación
    capacitacion = get_todas_capacitaciones()  # Función para obtener todas las capacitacion

    if not capacitacion:
        flash('No hay capacitacion para descargar.')
        return redirect(url_for('capacitacion'))  # Asegúrate de que la ruta 'capacitacion' está bien definida

    # Definir las columnas correctas
    columnas = ['id_capacitacion','id_empleado',' tema',' fecha_capacitacion',' duracion', 'resultado']

    # Crear un DataFrame con los datos de las capacitacion
    df = pd.DataFrame(capacitacion, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='capacitacion', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['capacitacion']
        bold_format = workbook.add_format({'bold': True})

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de capacitacion', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='capacitacion.xlsx')


# Nueva función para obtener todas las capacitacion sin límites
def get_todas_capacitaciones():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'capacitacion'
    query = "SELECT id_empleado, tema, fecha_capacitacion, duracion, resultado FROM capacitacion"

    try:
        cursor.execute(query)
        capacitacion = cursor.fetchall()  # Obtener todas las filas
        return capacitacion
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_todas_capacitaciones():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """ SELECT c.id_capacitacion, e.nombre, c.tema, c.fecha_capacitacion, c.duracion, c.resultado
    FROM capacitacion c
    JOIN empleados e ON c.id_empleado = e.id_empleado"""
    try:
        cursor.execute(query)
        capacitaciones = cursor.fetchall()
        return capacitaciones
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_capacitacion.route('/descargar_pdf')
@check_permission('permiso_capacitacion')
def descargar_pdf():
    # Obtener todos los transportistas y dividir en páginas de 10
    capacitaciones2 = get_todas_capacitaciones()
    paginacion = [capacitaciones2[i:i + 10] for i in range(0, len(capacitaciones2), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    ancho, alto = A4

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, capacitaciones_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Capacitaciones")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Transportistas
        data = [["ID", "Empleado", "Tema","Fecha/hora","Duracion","Resultado"]]  # Encabezado de la tabla
        data += [[capacitacionesC[0], capacitacionesC[1], capacitacionesC[2], capacitacionesC[3], capacitacionesC[4], capacitacionesC[5]] for capacitacionesC in capacitaciones_pagina]

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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Capacitacion.pdf')



if __name__ == '__main__':
    app_capacitacion.run(debug=True,port=5021)
