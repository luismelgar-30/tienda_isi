from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import datetime
import pandas as pd
from io import BytesIO
from flask import send_file
from flask import Flask, session
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import io

app_producto = Flask(__name__)
app_producto.secret_key = 'your_secret_key'  # Cambia 'your_secret_key' por una clave secreta segura

LOGS_DIR = 'logs/productos'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="productos", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

#Bloqueo URL
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

def log_error(error_message, screen_name="productos"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def productos_exists(id_producto):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM productos WHERE id_producto = %s"
    cursor.execute(query, (id_producto,))
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

def get_producto(page, per_page, search_criteria=None, search_query=None):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar el search_criteria
    valid_criteria = ['id_producto', 'nombre', 'nombre_categoria', 'Nombre_del_proveedor', 'original_precio']
    if search_criteria not in valid_criteria:
        search_criteria = None

    # Construir la consulta SQL según el criterio de búsqueda
    if search_criteria and search_query:
        if search_criteria == 'nombre_categoria':
            query = f"""
                SELECT p.id_producto, p.nombre, p.id_categoria, p.id_proveedor, 
                       p.original_precio, p.id_impuesto, p.id_promocion, p.id_garantia, 
                       c.nombre_categoria AS nombre_categoria, pro.Nombre_del_proveedor, i.tasa_impuesto, prom.nombre, g.duracion
                FROM producto p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
                JOIN impuesto i ON p.id_impuesto = i.id_impuesto
                JOIN promocion prom ON p.id_promocion = prom.id_promocion
                JOIN garantia g ON p.id_garantia = g.id_garantia
                WHERE c.nombre_categoria LIKE %s
                ORDER BY p.id_producto
                LIMIT %s OFFSET %s
            """
        elif search_criteria == 'Nombre_del_proveedor':
            query = f"""
                SELECT p.id_producto, p.nombre, p.id_categoria, p.id_proveedor, 
                       p.original_precio, p.id_impuesto, p.id_promocion, p.id_garantia, 
                       c.nombre_categoria AS nombre_categoria, pro.Nombre_del_proveedor, i.tasa_impuesto, prom.nombre, g.duracion
                FROM producto p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
                JOIN impuesto i ON p.id_impuesto = i.id_impuesto
                JOIN promocion prom ON p.id_promocion = prom.id_promocion
                JOIN garantia g ON p.id_garantia = g.id_garantia
                WHERE pro.Nombre_del_proveedor LIKE %s
                ORDER BY p.id_producto
                LIMIT %s OFFSET %s
            """
        elif search_criteria == 'original_precio':
            query = f"""
                SELECT p.id_producto, p.nombre, p.id_categoria, p.id_proveedor, 
                       p.original_precio, p.id_impuesto, p.id_promocion, p.id_garantia, 
                       c.nombre_categoria AS nombre_categoria, pro.Nombre_del_proveedor, i.tasa_impuesto, prom.nombre, g.duracion
                FROM producto p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
                JOIN impuesto i ON p.id_impuesto = i.id_impuesto
                JOIN promocion prom ON p.id_promocion = prom.id_promocion
                JOIN garantia g ON p.id_garantia = g.id_garantia
                WHERE p.original_precio LIKE %s
                ORDER BY p.id_producto
                LIMIT %s OFFSET %s
            """
        else:  # Maneja búsqueda por 'id_producto' o 'nombre'
            query = f"""
                SELECT p.id_producto, p.nombre, p.id_categoria, p.id_proveedor, 
                       p.original_precio, p.id_impuesto, p.id_promocion, p.id_garantia, 
                       c.nombre_categoria AS nombre_categoria, pro.Nombre_del_proveedor, i.tasa_impuesto, prom.nombre, g.duracion
                FROM producto p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
                JOIN impuesto i ON p.id_impuesto = i.id_impuesto
                JOIN promocion prom ON p.id_promocion = prom.id_promocion
                JOIN garantia g ON p.id_garantia = g.id_garantia
                WHERE p.{search_criteria} LIKE %s
                ORDER BY p.id_producto
                LIMIT %s OFFSET %s
            """
        values = (f'%{search_query}%', per_page, offset)
    else:
        query = """
            SELECT p.id_producto, p.nombre, p.id_categoria, p.id_proveedor, 
                   p.original_precio, p.id_impuesto, p.id_promocion, p.id_garantia, 
                   c.nombre_categoria AS nombre_categoria, pro.Nombre_del_proveedor, i.tasa_impuesto, prom.nombre, g.duracion
            FROM producto p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
            JOIN impuesto i ON p.id_impuesto = i.id_impuesto
            JOIN promocion prom ON p.id_promocion = prom.id_promocion
            JOIN garantia g ON p.id_garantia = g.id_garantia
            ORDER BY p.id_producto
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        cursor.execute(query, values)
        producto = cursor.fetchall()
        
        # Contar el total de productos
        if search_criteria and search_query:
            count_query = f"""
                SELECT COUNT(*) 
                FROM producto p
                JOIN categorias c ON p.id_categoria = c.id_categoria
                JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
                JOIN impuesto i ON p.id_impuesto = i.id_impuesto
                JOIN promocion prom ON p.id_promocion = prom.id_promocion
                JOIN garantia g ON p.id_garantia = g.id_garantia
                WHERE p.{search_criteria} LIKE %s
            """
            cursor.execute(count_query, (f'%{search_query}%',))
        else:
            count_query = "SELECT COUNT(*) FROM producto"
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        return producto, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_categorias():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_categoria, nombre_categoria FROM categorias"
    try:
        cursor.execute(query)
        documento_empleado = cursor.fetchall()
        return documento_empleado
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
    query = "SELECT id_proveedor, Nombre_del_proveedor FROM proveedores"
    try:
        cursor.execute(query)
        documento_empleado = cursor.fetchall()
        return documento_empleado
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_impuesto():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_impuesto, tasa_impuesto FROM impuesto"
    try:
        cursor.execute(query)
        documento_empleado = cursor.fetchall()
        return documento_empleado
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()


def get_promocion():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_promocion, nombre FROM promocion"
    try:
        cursor.execute(query)
        documento_empleado = cursor.fetchall()
        return documento_empleado
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_garantia():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_garantia, duracion FROM garantia"
    try:
        cursor.execute(query)
        documento_empleado = cursor.fetchall()
        return documento_empleado
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def insert_producto(nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO producto (nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    values = (nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Nombre: {nombre}, ID Categoría: {id_categoria}, ID Proveedor: {id_proveedor}, Precio Original: {original_precio}, ID Impuesto: {id_impuesto}, ID Promoción: {id_promocion}, ID Garantía: {id_garantia}"
        log_action('Inserted', screen_name='producto', details=details)  # Registro de log
        print("Producto insertado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def update_producto(id_producto, nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE producto
    SET nombre = %s,
        id_categoria = %s,
        id_proveedor = %s,
        original_precio = %s,
        id_impuesto = %s,
        id_promocion = %s,
        id_garantia = %s
    WHERE id_producto = %s
    """
    try:
        cursor.execute(query, (nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia, id_producto))
        connection.commit()
        details = f"ID Producto: {id_producto}, Nombre: {nombre}, ID Categoría: {id_categoria}, ID Proveedor: {id_proveedor}, Precio Original: {original_precio}, ID Impuesto: {id_impuesto}, ID Promoción: {id_promocion}, ID Garantía: {id_garantia}"
        log_action('Updated', screen_name='producto', details=details)  # Registro de log
        print("Producto actualizado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def delete_producto(id_producto):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM producto WHERE id_producto = %s"
    
    try:
        cursor.execute(query, (id_producto,))
        connection.commit()
        details = f"ID Producto: {id_producto}"
        log_action('Deleted', screen_name='producto', details=details)  # Registro de log
        print("Producto eliminado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def get_producto_by_id(id_producto):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM producto WHERE id_producto = %s"
    try:
        cursor.execute(query, (id_producto,))
        producto = cursor.fetchone()
        return producto
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def get_historico_productos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM historicos_productos LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        historico_productos = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_historico_productos = cursor.fetchone()[0]
        return historico_productos, total_historico_productos
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

@app_producto.route('/historico_productos')
@check_permission('permiso_producto')
def historico_productos():
    page = request.args.get('page', 1, type=int)
    per_page = int(request.args.get('per_page', 10))
    historicos, total_historicos = get_historico_productos(page, per_page)

    total_pages = (total_historicos + per_page - 1) // per_page
    return render_template('historico_productos.html', historicos=historicos, page=page, per_page=per_page, total_historicos=total_historicos, total_pages=total_pages)


@app_producto.route('/')
@check_permission('permiso_producto')
def index_producto():
    categorias = get_categorias()
    proveedores = get_proveedores()
    impuesto = get_impuesto()
    promocion = get_promocion()
    garantia = get_garantia()

    return render_template('index_producto.html', categorias=categorias, proveedores=proveedores, impuesto=impuesto, promocion=promocion, garantia=garantia)

@app_producto.route('/submit', methods=['POST'])
@check_permission('permiso_producto')
def submit():
    nombre = request.form.get('nombre')
    id_categoria = request.form.get('id_categoria')  
    id_proveedor = request.form.get('id_proveedor')
    original_precio = request.form.get('original_precio')
    id_impuesto = request.form.get('id_impuesto')
    id_promocion = request.form.get('id_promocion')
    id_garantia = request.form.get('id_garantia')
    
    # Imprimir los datos para depuración
    print(f"nombre: {nombre}")
    print(f"id_categoria: {id_categoria}")
    print(f"id_proveedor: {id_proveedor}")
    print(f"original_precio: {original_precio}")
    print(f"id_impuesto: {id_impuesto}")
    print(f"id_promocion: {id_promocion}")
    print(f"id_garantia: {id_garantia}")
    
    try:
        original_precio_decimal = float(original_precio)  # Asegurarse de que el salario sea un número decimal
    except ValueError:
        flash('El salario debe ser un número decimal válido.')
        return redirect(url_for('index_producto'))
    
    if insert_producto(nombre, id_categoria, id_proveedor, original_precio_decimal, id_impuesto, id_promocion, id_garantia):
        flash('Producto agregado exitosamente!')
    else:
        flash('Error al agregar el Producto.')

    return redirect(url_for('index_producto'))


@app_producto.route('/producto')
@check_permission('permiso_producto')
def producto():
    search_query = request.args.get('search_query', '')
    search_criteria = request.args.get('search_criteria', 'id_producto')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    producto, total_count = get_producto(page, per_page, search_criteria, search_query)

    total_pages = (total_count + per_page - 1) // per_page  # Asegúrate de que el cálculo sea correcto

    return render_template(
        'producto.html',
        producto=producto,
        page=page,
        total_pages=total_pages,
        search_query=search_query,
        search_criteria=search_criteria,
        per_page=per_page
    )

@app_producto.route('/edit_producto/<int:id_producto>', methods=['GET', 'POST'])
@check_permission('permiso_producto')
def edit_producto(id_producto):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        original_precio = request.form.get('original_precio')
        id_categoria = request.form.get('id_categoria')
        id_proveedor = request.form.get('id_proveedor')
        id_impuesto = request.form.get('id_impuesto')
        id_promocion = request.form.get('id_promocion')
        id_garantia = request.form.get('id_garantia')

        if not nombre or not original_precio:
            flash('¡Todos los campos obligatorios deben ser completados!')
            return redirect(url_for('edit_producto', id_producto=id_producto))

        if update_producto(id_producto, nombre, id_categoria, id_proveedor, original_precio, id_impuesto, id_promocion, id_garantia):
            flash('Producto editado exitosamente!')
        else:
            flash('Error al editar el Producto.')

        return redirect(url_for('producto'))
    else:
        producto = get_producto_by_id(id_producto)
        categorias = get_categorias() 
        proveedores = get_proveedores()
        impuesto = get_impuesto()
        promocion = get_promocion()
        garantia = get_garantia()

        if producto:
            return render_template(
                'edit_producto.html', 
                producto=producto,
                categorias=categorias,
                proveedores=proveedores,
                impuesto=impuesto,
                promocion=promocion,
                garantia=garantia
            )
        else:
            flash('El Producto no existe.')
            return redirect(url_for('producto'))


        


@app_producto.route('/eliminar_producto/<int:id_producto>', methods=['GET', 'POST'])
@check_permission('permiso_producto')
def eliminar_producto(id_producto):
    if request.method == 'POST':
        if delete_producto(id_producto):
            flash('¡Producto eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el Producto.')
        return redirect(url_for('producto'))

    producto = get_producto_by_id(id_producto)
    if producto is None:
        flash('¡Producto no encontrado!')
        return redirect(url_for('producto'))
    
    return render_template('eliminar_producto.html', producto=producto)


def get_producto_data():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = """
        SELECT p.id_producto, p.nombre, p.original_precio, 
               c.nombre_categoria, pro.Nombre_del_proveedor, 
               i.tasa_impuesto, prom.nombre, g.duracion
        FROM producto p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
        JOIN impuesto i ON p.id_impuesto = i.id_impuesto
        JOIN promocion prom ON p.id_promocion = prom.id_promocion
        JOIN garantia g ON p.id_garantia = g.id_garantia
    """
    try:
        cursor.execute(query)
        productos = cursor.fetchall()
        return productos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_producto.route('/exportar_productos')
@check_permission('permiso_producto')
def exportar_productos():
    # Obtener todas las productos sin paginación
    productos = get_producto_data()  # Función para obtener todas las productos

    if not productos:
        flash('No hay productos para descargar.')
        return redirect(url_for('productos'))  # Asegúrate de que la ruta 'productos' está bien definida

    # Definir las columnas correctas
    columnas = ['ID Producto', 'Nombre', 'Precio Original', 'Categoría', 'Proveedor', 'Tasa Impuesto', 'Promoción', 'Duración']

    # Crear un DataFrame con los datos de las productos
    df = pd.DataFrame(productos, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='productos', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['productos']
        bold_format = workbook.add_format({'bold': True})
        
        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de productos', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='productos.xlsx')

def get_todos_productos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query =  """
                  SELECT p.id_producto, p.nombre, p.original_precio, 
               c.nombre_categoria, pro.Nombre_del_proveedor, 
               i.tasa_impuesto, prom.nombre, g.duracion
        FROM producto p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        JOIN proveedores pro ON p.id_proveedor = pro.id_proveedor
        JOIN impuesto i ON p.id_impuesto = i.id_impuesto
        JOIN promocion prom ON p.id_promocion = prom.id_promocion
        JOIN garantia g ON p.id_garantia = g.id_garantia
        ORDER BY p.id_producto
    """
    try:
        cursor.execute(query)
        productos = cursor.fetchall()
        return productos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_producto.route('/descargar_pdf')
@check_permission('permiso_producto')
def descargar_pdf():
    # Obtener todos los productos y dividir en páginas de 10
    productos = get_todos_productos()
    paginacion = [productos[i:i + 10] for i in range(0, len(productos), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto = landscape(A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primer_nombre = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, productos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Productos")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {primer_nombre}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Productos
        data = [["ID Producto", "Nombre", "Precio Original", "Categoria", "Proveedor", "Tasa Impuesto", "Descuento", "Duracion"]]  # Encabezado de la tabla
        data += [[prod[0], prod[1], prod[2], prod[3], prod[4], prod[5], prod[6], prod[7]] for prod in productos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[2 * inch, 2 * inch, 2* inch, 2 * inch, 2 * inch, 2* inch, 2 * inch, 2 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Productos.pdf')



if __name__ == '__main__':
    app_producto.run(debug=True,port=5017)
