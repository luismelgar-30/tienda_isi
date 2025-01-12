from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import mysql.connector
from mysql.connector import Error
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from io import BytesIO
import re
import pandas as pd

app_pedidos_compra_p = Flask(__name__)
app_pedidos_compra_p.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/pedidos_de_compra_p'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="pedidos_de_compra_p", details=None):
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

def log_error(error_message, screen_name="pedidos_de_compra_p"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def pedidos_de_compra_p_exists(id_pedido):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM pedidos_de_compra_p WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
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

# Paso 1 :Para que sean seleccionables 
def get_estados():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_estado, nombre_estado FROM estado"
    try:
        cursor.execute(query)
        estados = cursor.fetchall()
        return estados
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_detalles_by_pedido_id(id_pedido):
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query ="""
    SELECT d.id_detalle, d.id_pedido, p.nombre AS nombre_producto, d.cantidad, d.precio_unitario, i.tasa_impuesto, d.subtotal, d.total
    FROM detalle_de_compra_proveedor d
    JOIN producto p ON d.id_producto = p.id_producto
    JOIN impuesto i ON d.id_impuesto = i.id_impuesto  -- Agrega este JOIN para obtener la tasa_impuesto
    WHERE d.id_pedido = %s
    """
    try:
        cursor.execute(query, (id_pedido,))
        detalles = cursor.fetchall()
        return detalles
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()


def get_metodos():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_metodo, nombre FROM metodo_de_pago"
    try:
        cursor.execute(query)
        metodos = cursor.fetchall()
        return metodos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_proveedores():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_proveedor, nombre_compañia FROM proveedores"
    try:
        cursor.execute(query)
        proveedores = cursor.fetchall()
        return proveedores
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()


def get_id_empleado():
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return None  # En caso de fallo en la conexión, retorna None
    cursor = connection.cursor(dictionary=True)  # Usamos dictionary=True para obtener los resultados como un diccionario
    query = "SELECT * FROM empleados WHERE email = %s"

    try:
        # Obtenemos el correo del usuario logueado desde la sesión
        correo_usuario = session.get('correo')
        if not correo_usuario:
            print("Error: No hay un usuario logueado.")
            return None  # Si no hay un usuario logueado, retorna None
        
        # Ejecutamos la consulta
        cursor.execute(query, (correo_usuario,))
        empleados = cursor.fetchone()  # Obtenemos el empleado que coincide con el correo

        if empleados:
            # Guardamos el id_empleado y otros valores relevantes en la sesión
            session['id_empleado'] = empleados.get('id_empleado')
            session['nombre_empleado'] = empleados.get('nombre')
            session['apellido_empleado'] = empleados.get('apellido')
            session['id_sucursal'] = empleados.get('id_sucursal')
            
            # Depuración: Imprimir los valores almacenados
            print("Empleado encontrado y guardado en la sesión:")
            print(f"id_empleado: {session.get('id_empleado')}")
            print(f"nombre_empleado: {session.get('nombre_empleado')}")
            print(f"apellido_empleado: {session.get('apellido_empleado')}")
            print(f"id_sucursal: {session.get('id_sucursal')}")

            return empleados  # Retorna el empleado encontrado
        else:
            print("No se encontró ningún empleado con ese correo.")
            return None  # Si no se encontró ningún empleado, retorna None
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def get_pedidos_compra_p(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Obtener el total de registros
    count_query = """
        SELECT COUNT(*) FROM pedido_de_compra_proveedor
        JOIN proveedores pr ON pedido_de_compra_proveedor.id_proveedor = pr.id_proveedor
        JOIN metodo_de_pago mp ON pedido_de_compra_proveedor.id_metodo = mp.id_metodo
        JOIN estado e ON pedido_de_compra_proveedor.id_estado = e.id_estado
    """
    try:
        cursor.execute(count_query)
        total_pedidos_compra_p = cursor.fetchone()[0]

        # Obtener los registros para la página actual
        query = """
            SELECT p.id_pedido, pr.nombre_compañia, p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, mp.nombre, e.nombre_estado, p.id_empleado
            FROM pedido_de_compra_proveedor p
            JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
            JOIN metodo_de_pago mp ON p.id_metodo = mp.id_metodo
            JOIN estado e ON p.id_estado = e.id_estado
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        pedidos_compra_p = cursor.fetchall()
        
        return pedidos_compra_p, total_pedidos_compra_p
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_pedidos_compra_p_by_id(id_pedido):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
         SELECT p.id_pedido, p.id_proveedor, p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, p.id_metodo, p.id_estado
        FROM pedido_de_compra_proveedor p
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        WHERE id_pedido = %s
    """
    try:
        cursor.execute(query, (id_pedido,))
        pedido = cursor.fetchone()
        return pedido
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_user(id_proveedor, numero_factura, id_empleado, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
    connection = create_connection()
    if connection is None:
        print("Error: No connection to database.")
        return False
    
    cursor = connection.cursor()

    # Verificar si el número de factura ya existe
    check_query = "SELECT COUNT(*) FROM pedido_de_compra_proveedor WHERE numero_factura = %s"
    cursor.execute(check_query, (numero_factura,))
    factura_exists = cursor.fetchone()[0]

    if factura_exists > 0:
        print("Error: El número de factura ya existe.")
        flash("Error: El número de factura ya existe. Por favor, usa un número diferente.")
        return False

    # Insertar el nuevo pedido
    query = """
        INSERT INTO pedido_de_compra_proveedor 
        (id_proveedor, numero_factura, id_empleado, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (id_proveedor, numero_factura if numero_factura else None, id_empleado, fecha_pedido, 
              fecha_entrega_estimada if fecha_entrega_estimada else None, fecha_entrega if fecha_entrega else None, 
              id_metodo, id_estado)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Proveedor: {id_proveedor}, Factura: {numero_factura}, ID Empleado: {id_empleado}, Fecha Pedido: {fecha_pedido}, Fecha Entrega Estimada: {fecha_entrega_estimada}, Fecha Entrega: {fecha_entrega}, ID Método: {id_metodo}, ID Estado: {id_estado}"
        log_action('Inserted', screen_name='pedido_de_compra_proveedor', details=details)  # Registro de log
        print("Insert successful.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def update_user(id_pedido, numero_factura, id_proveedor, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
    connection = create_connection()
    if connection is None:
        print("Error: No connection to database.")
        return False
    
    cursor = connection.cursor()
    query = """
        UPDATE pedido_de_compra_proveedor 
        SET id_proveedor = %s, numero_factura = %s, fecha_pedido = %s, fecha_entrega_estimada = %s, fecha_entrega = %s, id_metodo = %s, id_estado = %s 
        WHERE id_pedido = %s
    """
    values = (id_proveedor, numero_factura, fecha_pedido, fecha_entrega_estimada if fecha_entrega_estimada else None, 
              fecha_entrega if fecha_entrega else None, id_metodo, id_estado, id_pedido)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Pedido: {id_pedido}, ID Proveedor: {id_proveedor}, Factura: {numero_factura}, Fecha Pedido: {fecha_pedido}, Fecha Entrega Estimada: {fecha_entrega_estimada}, Fecha Entrega: {fecha_entrega}, ID Método: {id_metodo}, ID Estado: {id_estado}"
        log_action('Updated', screen_name='pedido_de_compra_proveedor', details=details)  # Registro de log
        print("Update successful.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def delete_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No connection to database.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM pedido_de_compra_proveedor WHERE id_pedido = %s"
    
    try:
        cursor.execute(query, (id_pedido,))
        connection.commit()
        details = f"ID Pedido: {id_pedido}"
        log_action('Deleted', screen_name='pedido_de_compra_proveedor', details=details)  # Registro de log
        print("Delete successful.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def search_users(search_query, search_field, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"""
        SELECT p.id_pedido, pr.nombre_compañia,p.numero_factura, p.fecha_pedido, p.fecha_entrega, mp.nombre, e.nombre_estado,p.id_empleado
        FROM pedido_de_compra_proveedor p
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        JOIN metodo_de_pago mp ON p.id_metodo = mp.id_metodo
        JOIN estado e ON p.id_estado = e.id_estado
        WHERE {search_field} LIKE %s
        LIMIT %s OFFSET %s
    """
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        pedidos_compra_p = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_pedidos_compra_p = cursor.fetchone()[0]
        return pedidos_compra_p, total_pedidos_compra_p
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_pedidos_compra_p(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    
    query = f"""
        SELECT SQL_CALC_FOUND_ROWS p.id_pedido, pr.nombre_compañia, p.numero_factura, p.fecha_pedido, 
               p.fecha_entrega_estimada, p.fecha_entrega, mp.nombre, e.nombre_estado,p.id_empleado
        FROM pedido_de_compra_proveedor p
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        JOIN metodo_de_pago mp ON p.id_metodo = mp.id_metodo
        JOIN estado e ON p.id_estado = e.id_estado
        WHERE {search_criteria} LIKE %s
        LIMIT %s OFFSET %s
    """
    
    values = (f'%{search_query}%', per_page, offset)
    
    try:
        cursor.execute(query, values)
        pedidos_compra_p = cursor.fetchall()
        
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        
        return pedidos_compra_p, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def is_valid(text):
    if re.search(r'[^a-zA-Z0-9 ]', text):  # Caracteres especiales
        return False
    if re.search(r'(.)\1\1', text):  # Mismo carácter repetido más de dos veces
        return False
    if len(text) < 3:  # Longitud mínima de 3 caracteres
        return False
    if re.search(r'([aeiouAEIOU])\1', text):  # Misma vocal repetida dos veces consecutivas
        return False
    return True

def get_usuarios(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS id_pedido, id_proveedor, numero_factura, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado FROM pedido_de_compra_proveedor LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        usuarios = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_usuarios = cursor.fetchone()[0]
        return usuarios, total_usuarios
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

#Paso 2 para que sean seleccionables
@app_pedidos_compra_p.route('/')
@check_permission('permiso_pedido_proveedor')
def index_pedidos_compra_p():
    estados = get_estados()
    metodos = get_metodos()
    proveedores= get_proveedores()
    empleados = get_id_empleado()

    return render_template('index_pedidos_compra_p.html', estados=estados, metodos=metodos, proveedores=proveedores, empleados= empleados)

@app_pedidos_compra_p.route('/pedidos_compra_pv')
@check_permission('permiso_pedido_proveedor')
def pedidos_compra_pv():
    search_criteria = request.args.get('search_criteria', 'id_pedido')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    if search_query:
        pedidos_compra_p, total_count = search_pedidos_compra_p(search_criteria, search_query, page, per_page)
    else:
        pedidos_compra_p, total_count = get_pedidos_compra_p(page, per_page)

    total_pages = (total_count + per_page - 1) // per_page

    return render_template('pedidos_compra_pv.html', pedidos_compra_p=pedidos_compra_p, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_pedidos_compra_p.route('/submit', methods=['POST'])
@check_permission('permiso_pedido_proveedor')
def submit():
    id_proveedor = request.form['id_proveedor']
    numero_factura=request.form['numero_factura']
    id_empleado = session.get('id_empleado')
    fecha_pedido = request.form['fecha_pedido']
    fecha_entrega_estimada = request.form['fecha_entrega_estimada']
    fecha_entrega = request.form['fecha_entrega'] or None  # Set to None if empty
    id_metodo = request.form['id_metodo']
    id_estado = request.form['id_estado']
    
    if not id_proveedor or not fecha_pedido or not id_metodo or not id_estado:
        flash('All fields are required except Fecha Entrega and Fecha Entrega Estimada!')
        return redirect(url_for('index_pedidos_compra_p'))
       
    if insert_user(id_proveedor,numero_factura,id_empleado ,fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
        flash('Pedido inserted successfully!')
    else:
        flash('An error occurred while inserting the pedido.')
    
    return redirect(url_for('index_pedidos_compra_p'))

    

@app_pedidos_compra_p.route('/edit_pedidos_compra_p/<int:id_pedido>', methods=['GET', 'POST'])
@check_permission('permiso_pedido_proveedor')
def edit_pedidos_compra_p(id_pedido):
    if request.method == 'POST':
        id_proveedor = request.form['id_proveedor']
        numero_factura = request.form.get('numero_factura', '').strip()
        fecha_pedido = request.form['fecha_pedido']
        fecha_entrega_estimada = request.form['fecha_entrega_estimada']
        fecha_entrega = request.form['fecha_entrega'] or None
        id_metodo = request.form['id_metodo']
        id_estado = request.form['id_estado']

        # Validar campos obligatorios
        if not id_proveedor or not numero_factura or not fecha_pedido or not id_metodo or not id_estado:
            flash('Todos los campos son obligatorios excepto "Fecha Entrega".')
            return redirect(url_for('edit_pedidos_compra_p', id_pedido=id_pedido))

        # Verificar si el número de factura ya existe (excepto el que se está editando)
        if numero_factura and existe_numero_factura(numero_factura, id_pedido):
            flash('El número de factura ya existe y no puede ser editado.', 'error')
            return redirect(url_for('edit_pedidos_compra_p', id_pedido=id_pedido))

        # Validar el campo numero_factura
        if not numero_factura:
            flash('El número de factura es obligatorio.')
            return redirect(url_for('edit_pedidos_compra_p', id_pedido=id_pedido))

        # Llamar a la función de actualización, pasar los parámetros correctos
        if update_user(id_pedido, numero_factura, id_proveedor, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
            flash('Pedido actualizado exitosamente', 'success')
            return redirect(url_for('pedidos_compra_pv'))
        else:
            flash('Ocurrió un error al actualizar el pedido.')
            return redirect(url_for('edit_pedidos_compra_p', id_pedido=id_pedido))

    # Para el método GET, cargar los detalles del pedido y mostrar el formulario
    pedido = get_pedidos_compra_p_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado.')
        return redirect(url_for('pedidos_compra_pv'))
    
    estados = get_estados()
    metodos = get_metodos()
    proveedores = get_proveedores()
    
    return render_template('edit_pedidos_compra_p.html', pedido=pedido, estados=estados, metodos=metodos, proveedores=proveedores)

def existe_numero_factura(numero_factura, id_pedido):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 1 FROM pedido_de_compra_proveedor
            WHERE numero_factura = %s AND id_pedido != %s
        """, (numero_factura, id_pedido))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


@app_pedidos_compra_p.route('/eliminar_pedidos_compra_p/<int:id_pedido>', methods=['GET', 'POST'])
@check_permission('permiso_pedido_proveedor')
def eliminar_pedido(id_pedido):  
    if request.method == 'POST':
        if delete_pedido(id_pedido):
            flash('¡Pedido eliminado exitosamente!')
            return redirect(url_for('pedidos_compra_pv'))
        else:
            flash('Ocurrió un error al eliminar el pedido. Por favor, intente nuevamente.')
            return redirect(url_for('pedidos_compra_pv'))

    pedido = get_pedidos_compra_p_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado.')
        return redirect(url_for('pedidos_compra_pv'))
    estados = get_estados()
    metodos = get_metodos()
    proveedores = get_proveedores()

    return render_template('eliminar_pedidos_compra_p.html', pedido=pedido, estados=estados, metodos=metodos, proveedores=proveedores)

@app_pedidos_compra_p.route('/ver_pedido_p/<int:id_pedido>')
@check_permission('permiso_pedido_proveedor')
def ver_pedido(id_pedido):
    pedido = get_pedidos_compra_p_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado!')
        return redirect(url_for('pedidos'))

    detalles = get_detalles_by_pedido_id(id_pedido)
    return render_template('ver_pedido_p.html', pedido=pedido, detalles=detalles)

def get_todos_los_pedidos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT p.id_pedido, pr.nombre_compañia, p.numero_factura, p.fecha_pedido, 
               p.fecha_entrega_estimada, p.fecha_entrega, mp.nombre, e.nombre_estado
        FROM pedido_de_compra_proveedor p
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        JOIN metodo_de_pago mp ON p.id_metodo = mp.id_metodo
        JOIN estado e ON p.id_estado = e.id_estado
    """
    try:
        cursor.execute(query)
        pedidos_compra_ps = cursor.fetchall()
        return pedidos_compra_ps
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_pedidos_compra_p.route('/descargar_excel')
@check_permission('permiso_pedido_proveedor')
def descargar_excel():
    # Obtener todas las pedidos_compra_p sin paginación
    pedidos_compra_p = get_todos_pedidos()  # Asegúrate de que el nombre de la función es correcto

    if not pedidos_compra_p:
        flash('No hay nada en el pedidos_compra_p para descargar.')
        return redirect(url_for('pedidos_compra_pv'))  # Asegúrate de que la ruta 'pedidos_compra_p' está bien definida

    # Definir las columnas correctas (sin espacios en los nombres)
    columnas = ['id_pedidos_compra_p', 'nombre_compañia','nombre_Empleado', 'numero_factura', 'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega', 'nombre', 'nombre_estado']

    
    # Crear un DataFrame con los datos de las pedidos_compra_p
    df = pd.DataFrame(pedidos_compra_p, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los metadatos en las primeras filas
        worksheet = writer.book.add_worksheet('pedidos_compra_p')
        worksheet.write('A1', 'Listado de pedidos_compra_p')
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='pedidos_compra_p', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='pedidos_compra_p.xlsx')

def get_todos_pedidos():
    connection = create_connection()  # Asegúrate de que esta función esté definida
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
        SELECT p.id_pedido, 
               pr.nombre_compañia,
               CONCAT(emp.nombre, ' ', emp.apellido) AS nombre_completo,  -- Concatenar nombre y apellido
               p.numero_factura, 
               p.fecha_pedido, 
               p.fecha_entrega_estimada, 
               p.fecha_entrega, 
               mp.nombre AS metodo_pago, 
               est.nombre_estado  -- Alias para la tabla estado
        FROM pedido_de_compra_proveedor p
        JOIN empleados emp ON p.id_empleado = emp.id_empleado  -- Cambié el alias a 'emp'
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
        JOIN metodo_de_pago mp ON p.id_metodo = mp.id_metodo
        JOIN estado est ON p.id_estado = est.id_estado  -- Cambié el alias a 'est'
    """
    try:
        cursor.execute(query)
        pedidos_compra_pv = cursor.fetchall()
        return pedidos_compra_pv
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_pedidos_compra_p.route('/descargar_pedidos_pdf')
@check_permission('permiso_pedido_proveedor')
def descargar_pedidos_pdf():
    # Obtener todos los pedidos y dividir en páginas de 10
    pedidos_compra_pv = get_todos_pedidos()
    paginacion = [pedidos_compra_pv[i:i + 10] for i in range(0, len(pedidos_compra_pv), 10)]

    # Configuración de PDF en orientación horizontal
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto = landscape(A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, pedidos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Pedidos Compra Proveedor")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

# Cuerpo - Tabla de Pedidos
        data = [["ID Pedido", "Proveedor", "Empleado", "Número de Factura", "Fecha Pedido", "Fecha Entrega Estimada", "Fecha de Recepción", "Método", "Estado"]]  # Encabezado de la tabla
        data += [[pedido[0], pedido[1], pedido[2], pedido[3], pedido[4], pedido[5], pedido[6], pedido[7], pedido[8]] for pedido in pedidos_pagina]

        # Configuración de la tabla
        table = Table(
            data,
            colWidths=[
                0.8 * inch,   # ID Pedido
                1.7 * inch,   # Proveedor
                1.7 * inch,   # Empleado
                1.4 * inch,   # Número de Factura
                1.2 * inch,   # Fecha Pedido
                1.7 * inch,   # Fecha Entrega Estimada
                1.5 * inch,   # Fecha de Recepción
                1.2 * inch,   # Método
                1 * inch      # Estado
            ]
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Pedidos_Proveedor.pdf')
    
    
if __name__ == '__main__':

    app_pedidos_compra_p.run(debug=True, port=5015)
