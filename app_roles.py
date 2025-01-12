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

app_roles = Flask(__name__)
app_roles.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/roles'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="roles", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="roles"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def roles_exists(nombre_rol):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM roles WHERE nombre_rol = %s"
    cursor.execute(query, (nombre_rol,))
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

def asignar_permisos(id_rol, id_permisos):
    connection = create_connection()
    if connection is None:
        return False
    
    cursor = connection.cursor()
    
    try:
        # Limpiar permisos actuales
        cursor.execute("DELETE FROM roles_permisos WHERE id_rol = %s", (id_rol,))
        
        # Asignar nuevos permisos
        for permiso_id in id_permisos:
            cursor.execute("INSERT INTO roles_permisos (id_rol, id_permiso) VALUES (%s, %s)", (id_rol, permiso_id))
        
        connection.commit()
        log_action('Permissions assigned', screen_name='roles', details=f"ID Rol: {id_rol}, Permisos: {id_permisos}")
        return True
    except Error as e:
        error_message = f"Error al asignar permisos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()


def get_roles(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT * FROM roles LIMIT %s OFFSET %s"
    
    try:
        # Execute the main query to fetch categories with pagination
        cursor.execute(query, (per_page, offset))
        roles = cursor.fetchall()

        # Execute the query to count total categories
        cursor.execute("SELECT COUNT(*) FROM roles")
        total_count = cursor.fetchone()[0]

        return roles, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()



def get_roles_by_id(id_rol):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM roles WHERE id_rol = %s"
    try:
        cursor.execute(query, (id_rol,))
        roles = cursor.fetchone()
        return roles
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_roles(nombre_rol, descripcion):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "INSERT INTO roles (nombre_rol, descripcion) VALUES (%s, %s)"
    values = (nombre_rol, descripcion)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la inserción
        details = f"Nombre: {nombre_rol}, Descripción: {descripcion}"
        log_action('Inserted', screen_name='roles', details=details)  # Registro de la acción de inserción

        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_roles(id_rol, nombre_rol, descripcion):   
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE roles
    SET nombre_rol = %s, descripcion = %s
    WHERE id_rol = %s
    """
    values = (nombre_rol, descripcion, id_rol)
    try:
        cursor.execute(query, values)
        connection.commit()

        # Registro en logs después de la actualización
        details = f"ID: {id_rol}, Nombre: {nombre_rol}, Descripción: {descripcion}"
        log_action('Updated', screen_name='roles', details=details)  # Registro de la acción de actualización

        print(f"Updated {cursor.rowcount} rows")  # Debugging line
        return True
    except Error as e:
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_roles(id_rol):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    # Obtener detalles de la categoría antes de eliminar para el log
    cursor.execute("SELECT nombre_rol, descripcion FROM roles WHERE id_rol = %s", (id_rol,))
    roles = cursor.fetchone()
    
    if not roles:
        print("Categoría no encontrada")
        return False

    nombre_rol, descripcion = roles
    query = "DELETE FROM roles WHERE id_rol = %s"
    try:
        cursor.execute(query, (id_rol,))
        connection.commit()

        # Registro en logs después de la eliminación
        details = f"ID: {id_rol}, Nombre: {nombre_rol}, Descripción: {descripcion}"
        log_action('Deleted', screen_name='roles', details=details)  # Registro de la acción de eliminación

        return True
    except Exception as e:  # Catching general exceptions can be more appropriate here
        error_message = f"Error al Actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def search_roles(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    if search_criteria not in ['nombre_rol', 'Descripcion']:
        search_criteria = 'nombre_rol'

    query = f"SELECT * FROM roles WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    
    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        roles = cursor.fetchall()

        cursor.execute(f"SELECT COUNT(*) FROM roles WHERE {search_criteria} LIKE %s", (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return roles, total_count
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


@app_roles.route('/')
def index_roles():
    return render_template('index_roles.html')

@app_roles.route('/roles')
def roles():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    if search_criteria and search_query:
        roles, total_count = search_roles(search_criteria, search_query, page, per_page)
    else:
        roles, total_count = get_roles(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('roles.html', roles=roles, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_roles.route('/submit', methods=['POST'])
def submit_roles():
    nombre_rol = request.form.get('nombre_rol')
    descripcion = request.form.get('Descripcion')

    # Validaciones
    nombre_error = validate_input(nombre_rol)
    descripcion_error = validate_input(descripcion)

    if nombre_error or descripcion_error:
        if nombre_error:
            flash(nombre_error)
        if descripcion_error:
            flash(descripcion_error)
        return redirect(url_for('index_roles'))

    # Inserta la categoría en la base de datos
    if insert_roles(nombre_rol, descripcion):
        flash('Categoría insertada correctamente!')
    else:
        flash('Ocurrió un error al insertar la categoría.')

    return redirect(url_for('index_roles'))

@app_roles.route('/edit_roles/<int:id_rol>', methods=['GET', 'POST'])
def edit_roles(id_rol):
    if request.method == 'POST':
        nombre_rol = request.form.get('nombre_rol')
        descripcion = request.form.get('Descripcion')

        # Validaciones
        nombre_error = validate_input(nombre_rol)
        descripcion_error = validate_input(descripcion)

        if nombre_error or descripcion_error:
            if nombre_error:
                flash(nombre_error)
            if descripcion_error:
                flash(descripcion_error)
            return redirect(url_for('edit_roles', id_rol=id_rol))

        if update_roles(id_rol, nombre_rol, descripcion):
            flash('Categoría actualizada correctamente!')
        else:
            flash('Error al actualizar la categoría.')
        return redirect(url_for('roles'))
    
    roles = get_roles_by_id(id_rol)
    return render_template('edit_roles.html', roles=roles)

@app_roles.route('/eliminar/<int:id_rol>', methods=['GET', 'POST'])
def eliminar_roles(id_rol):
    if request.method == 'POST':
        if delete_roles(id_rol):
            flash('Categoría eliminada exitosamente!')
        else:
            flash('Ocurrió un error al eliminar la categoría.')
        return redirect(url_for('roles'))

    roles = get_roles_by_id(id_rol)
    if roles is None:
        flash('Categoría no encontrada!')
        return redirect(url_for('roles'))
    
    return render_template('eliminar_roles.html', roles=roles)

if __name__ == '__main__':
    app_roles.run(debug=True, port=5038)
