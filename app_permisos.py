import datetime
from io import BytesIO
import os
from flask import Flask, jsonify, render_template, request, redirect, send_file, session, url_for, flash
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

app_permisos = Flask(__name__)
app_permisos.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/permisos'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="permisos", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="permisos"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def permisos_exists(nombre_permiso):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM permisos WHERE nombre_permiso = %s"
    cursor.execute(query, (nombre_permiso,))
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

def get_permisos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
        SELECT p.id_permiso, r.nombre_rol, p.permiso_crear, p.permiso_editar, p.permiso_eliminar, p.permiso_ver, np.nombre_pantalla
        FROM permisos p
        JOIN roles r ON p.id_rol = r.id_rol
        JOIN n_pantallas np ON p.id_permiso_pantalla = np.id_permiso_pantalla
        LIMIT %s OFFSET %s
    """
    
    try:
        cursor.execute(query, (per_page, offset))
        permisos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM permisos")
        total_count = cursor.fetchone()[0]

        return permisos, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_pantallas_permitidas(id_rol):
    connection = create_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor()
    query = """
        SELECT permiso_producto, permiso_empleado, permiso_inventario, permiso_capacitacion, 
               permiso_cliente, permiso_proveedor, permiso_sucursal, permiso_equipo,
               permiso_pedido_cliente, permiso_pedido_proveedor, permiso_devolucion_venta, 
               permiso_devolucion_compra, permiso_promocion, permiso_mantenimiento, 
               permiso_transportista, permiso_sar, permiso_usuario, permiso_categoria,
               permiso_distribucion, permiso_puesto_trabajo, permiso_impuesto, permiso_almacen
        FROM pantalla
        WHERE id_rol = %s
    """
    try:
        cursor.execute(query, (id_rol,))
        result = cursor.fetchone()  # Trae una sola fila con los permisos como columnas
        
        # Creamos una lista con los permisos que están activados (con valor True o 1)
        pantallas_permitidas = []
        if result:
            for index, permiso in enumerate(result):
                # Si el permiso está activo (por ejemplo, tiene valor True o 1), lo añadimos a la lista
                if permiso:  # Esto verifica si el permiso tiene un valor distinto de None o False
                    pantallas_permitidas.append({
                        'id_permiso_pantalla': index + 1,  # ID único basado en el índice
                        'nombre_pantalla': get_nombre_pantalla(index + 1)  # Función para obtener el nombre basado en el índice
                    })

        return pantallas_permitidas
    except Error as e:
        print(f"Error al obtener pantallas permitidas: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

# Función para obtener el nombre de la pantalla basado en el índice
def get_nombre_pantalla(id):
    nombres_pantallas = {
        1: "Producto", 2: "Empleado", 3: "Inventario", 4: "Capacitación",
        5: "Cliente", 6: "Proveedor", 7: "Sucursal", 8: "Equipo",
        9: "Pedido Cliente", 10: "Pedido Proveedor", 11: "Devolución Venta",
        12: "Devolución Compra", 13: "Promoción", 14: "Mantenimiento",
        15: "Transportista", 16: "SAR", 17: "Usuario", 18: "Categoría",
        19: "Distribución", 20: "Puesto de Trabajo", 21: "Impuesto", 22: "Almacén"
    }
    return nombres_pantallas.get(id, "Desconocido")

def get_permisos_by_id(id_permiso):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT id_permiso, id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf
    FROM permisos
    WHERE id_permiso = %s
    """
    try:
        cursor.execute(query, (id_permiso,))
        permisos = cursor.fetchone()
        return permisos
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()


def get_n_pantallas():
    connection = create_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor()
    query = "SELECT id_permiso_pantalla	, nombre_pantalla FROM n_pantallas"
    try:
        cursor.execute(query)
        n_pantallas = cursor.fetchall()
        if not n_pantallas:
            print("No se encontraron n_pantallas en la base de datos.")
        return n_pantallas
    except Error as e:
        print(f"Error al obtener n_pantallas: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def get_roles():
    connection = create_connection()
    if connection is None:
        return []
    
    cursor = connection.cursor()
    query = "SELECT id_rol, nombre_rol FROM roles"
    try:
        cursor.execute(query)
        roles = cursor.fetchall()
        if not roles:
            print("No se encontraron roles en la base de datos.")
        return roles
    except Error as e:
        print(f"Error al obtener roles: {e}")
        return []
    finally:
        cursor.close()
        connection.close()



def insert_permisos(id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    INSERT INTO permisos (id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Rol ID: {id_rol}, Crear: {permiso_crear}, Editar: {permiso_editar}, Eliminar: {permiso_eliminar}, Ver: {permiso_ver}, Pantalla ID: {id_permiso_pantalla}, Buscador: {permiso_buscador}, Exportar Excel: {permiso_exportar_excel}, Exportar PDF: {permiso_exportar_pdf}"
        log_action('Inserted', screen_name='permisos', details=details)
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()


def update_permisos(id_permiso, id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE permisos
    SET id_rol = %s, permiso_crear = %s, permiso_editar = %s, permiso_eliminar = %s, permiso_ver = %s, id_permiso_pantalla = %s, permiso_buscador = %s, permiso_exportar_excel = %s, permiso_exportar_pdf = %s
    WHERE id_permiso = %s
    """
    values = (id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf, id_permiso)
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Permiso: {id_permiso}, Rol ID: {id_rol}, Crear: {permiso_crear}, Editar: {permiso_editar}, Eliminar: {permiso_eliminar}, Ver: {permiso_ver}, Pantalla ID: {id_permiso_pantalla}, Buscador: {permiso_buscador}, Exportar Excel: {permiso_exportar_excel}, Exportar PDF: {permiso_exportar_pdf}"
        log_action('Updated', screen_name='permisos', details=details)
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()


def delete_permisos(id_permiso):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    # Fetch details of the permission before deleting for logging
    cursor.execute("""
        SELECT id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla
        FROM permisos
        WHERE id_permiso = %s
    """, (id_permiso,))
    permiso = cursor.fetchone()
    
    if not permiso:
        print("Permiso no encontrado")
        return False

    id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla = permiso
    query = "DELETE FROM permisos WHERE id_permiso = %s"
    try:
        cursor.execute(query, (id_permiso,))
        connection.commit()

        # Log action after deletion
        details = f"ID Permiso: {id_permiso}, Rol ID: {id_rol}, Crear: {permiso_crear}, Editar: {permiso_editar}, Eliminar: {permiso_eliminar}, Ver: {permiso_ver}, Pantalla ID: {id_permiso_pantalla}"
        log_action('Deleted', screen_name='permisos', details=details)

        return True
    except Exception as e:
        error_message = f"Error al eliminar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)
        return False
    finally:
        cursor.close()
        connection.close()

def search_permisos(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar el criterio de búsqueda
    valid_criteria = ['id_rol', 'permiso_crear', 'permiso_editar', 'permiso_eliminar', 'permiso_ver']
    if search_criteria not in valid_criteria:
        search_criteria = 'id_rol'  # Predeterminar a 'id_rol' si el criterio es inválido

    # Construir la consulta con el criterio y paginación
    query = f"SELECT * FROM permisos WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    
    try:
        cursor.execute(query, (f'%{search_query}%', per_page, offset))
        permisos = cursor.fetchall()

        # Obtener el conteo total de resultados para el criterio de búsqueda
        cursor.execute(f"SELECT COUNT(*) FROM permisos WHERE {search_criteria} LIKE %s", (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]

        return permisos, total_count
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


@app_permisos.route('/', methods=['GET', 'POST'])
def index_permisos():
    # Obtener roles para mostrar en el formulario
    roles = get_roles()

    # Si el formulario fue enviado
    if request.method == 'POST':
        id_rol = request.form.get('id_rol')  # Obtener el rol elegido
        pantallas_permitidas = get_pantallas_permitidas(id_rol)  # Obtener las pantallas permitidas para el rol seleccionado
    else:
        pantallas_permitidas = []  # Si no se ha enviado el formulario, inicializar vacío

    return render_template('index_permisos.html', roles=roles, pantallas_permitidas=pantallas_permitidas)

@app_permisos.route('/obtener_pantallas/<int:id_rol>', methods=['GET'])
def obtener_pantallas(id_rol):
    # Obtén las pantallas permitidas para el rol
    pantallas_permitidas = get_pantallas_permitidas(id_rol)
    
    # Retorna las pantallas en formato JSON
    return jsonify(pantallas_permitidas)

@app_permisos.route('/permisos')
def permisos():
    # Obtener los parámetros de búsqueda y paginación
    search_criteria = request.args.get('search_criteria')  # Criterio de búsqueda
    search_query = request.args.get('search_query')  # Valor de búsqueda
    page = int(request.args.get('page', 1))  # Página actual
    per_page = int(request.args.get('per_page', 10))  # Número de resultados por página (10 por defecto)

    # Si hay criterios de búsqueda, buscar los permisos según el criterio
    if search_criteria and search_query:
        permisos, total_count = search_permisos(search_criteria, search_query, page, per_page)
    else:
        permisos, total_count = get_permisos(page, per_page)
    
    # Calcular el número total de páginas
    total_pages = (total_count + per_page - 1) // per_page  # Esto debería redondear hacia arriba

    # Verificar si el número de páginas es correcto
    print(f"Total de permisos: {total_count}, Páginas: {total_pages}")

    # Obtener roles y pantallas
    roles = get_roles()
    n_pantallas = get_n_pantallas()

    # Renderizar la plantilla con los datos y la paginación
    return render_template('permisos.html', permisos=permisos, search_criteria=search_criteria, 
                           search_query=search_query, page=page, total_pages=total_pages, 
                           per_page=per_page, roles=roles, n_pantallas=n_pantallas)

@app_permisos.route('/submit', methods=['POST'])
def submit_permisos():
    id_rol = request.form.get('id_rol')
    permiso_crear = 1 if request.form.get('permiso_crear') == 'on' else 0
    permiso_editar = 1 if request.form.get('permiso_editar') == 'on' else 0
    permiso_eliminar = 1 if request.form.get('permiso_eliminar') == 'on' else 0
    permiso_ver = 1 if request.form.get('permiso_ver') == 'on' else 0
    permiso_buscador = 1 if request.form.get('permiso_buscador') == 'on' else 0
    permiso_exportar_excel = 1 if request.form.get('permiso_exportar_excel') == 'on' else 0
    permiso_exportar_pdf = 1 if request.form.get('permiso_exportar_pdf') == 'on' else 0
    id_permiso_pantalla = request.form.get('id_permiso_pantalla')

    # Imprimir para depurar el valor de los permisos antes de guardarlos
    print(f"Formulario enviado: id_rol = {id_rol}, id_permiso_pantalla = {id_permiso_pantalla}, permisos: crear={permiso_crear}, editar={permiso_editar}, eliminar={permiso_eliminar}, ver={permiso_ver}, buscador={permiso_buscador}, excel={permiso_exportar_excel}, pdf={permiso_exportar_pdf}")

    # Inserción de permisos
    if insert_permisos(id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf):
        flash('Permiso insertado correctamente!')
    else:
        flash('Ocurrió un error al insertar el permiso.')

    return redirect(url_for('index_permisos'))


@app_permisos.route('/edit_permisos/<int:id_permiso>', methods=['GET', 'POST'])
def edit_permisos(id_permiso):
    if request.method == 'POST':
        id_rol = request.form.get('id_rol')
        permiso_crear = 1 if request.form.get('permiso_crear') == 'on' else 0
        permiso_editar = 1 if request.form.get('permiso_editar') == 'on' else 0
        permiso_eliminar = 1 if request.form.get('permiso_eliminar') == 'on' else 0
        permiso_ver = 1 if request.form.get('permiso_ver') == 'on' else 0
        permiso_buscador = 1 if request.form.get('permiso_buscador') == 'on' else 0
        permiso_exportar_excel = 1 if request.form.get('permiso_exportar_excel') == 'on' else 0
        permiso_exportar_pdf = 1 if request.form.get('permiso_exportar_pdf') == 'on' else 0
        id_permiso_pantalla = request.form.get('id_permiso_pantalla')

        # Imprimir para depurar el valor de los permisos antes de actualizarlos
        print(f"Formulario de edición enviado: id_rol = {id_rol}, id_permiso_pantalla = {id_permiso_pantalla}, permisos: crear={permiso_crear}, editar={permiso_editar}, eliminar={permiso_eliminar}, ver={permiso_ver}, buscador={permiso_buscador}, excel={permiso_exportar_excel}, pdf={permiso_exportar_pdf}")

        # Actualización de permisos
        if update_permisos(id_permiso, id_rol, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver, id_permiso_pantalla, permiso_buscador, permiso_exportar_excel, permiso_exportar_pdf):
            flash('Permiso actualizado correctamente!')
        else:
            flash('Error al actualizar el permiso.')

        return redirect(url_for('permisos'))

    # Si la solicitud es GET, obtener los permisos actuales y los roles
    permisos = get_permisos_by_id(id_permiso)
    roles = get_roles()
    n_pantallas = get_n_pantallas()

    return render_template('edit_permisos.html', permisos=permisos, roles=roles, n_pantallas=n_pantallas)

@app_permisos.route('/eliminar/<int:id_permiso>', methods=['GET', 'POST'])
def eliminar_permisos(id_permiso):
    if request.method == 'POST':
        if delete_permisos(id_permiso):
            flash('Permiso eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el permiso.')
        return redirect(url_for('permisos'))

    permisos = get_permisos_by_id(id_permiso)
    if permisos is None:
        flash('Permiso no encontrado!')
        return redirect(url_for('permisos'))
    
    return render_template('eliminar_permisos.html', permisos=permisos)


if __name__ == '__main__':
    app_permisos.run(debug=True, port=5036)
