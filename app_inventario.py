from functools import wraps
import os
from flask import Flask, render_template, request, redirect, url_for, flash,session,send_file
import mysql.connector
from mysql.connector import Error
import re
import pandas as pd
from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from io import BytesIO


app_inventario = Flask(__name__)
app_inventario.secret_key = 'your_secret_key'  # Cambia 'your_secret_key' por una clave secreta segura

LOGS_DIR = 'logs/inventario'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="inventario", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")




def log_error(error_message, screen_name="inventario"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def inventario_exists(id_inventario):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM inventario WHERE id_inventario = %s"
    cursor.execute(query, (id_inventario,))
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

def validate_text_field(value, field_name, min_length=3, max_length=20):
    if not value or len(value) < min_length or len(value) > max_length:
        return f'{field_name} debe tener entre {min_length} y {max_length} caracteres.'
    if re.search(r'[0-9]', value):
        return f'{field_name} no debe contener números.'
    if re.search(r'[!@#$%^&*()_+={}\[\]:;"\'<>,.?/\\|`~]', value):
        return f'{field_name} no debe contener caracteres especiales.'
    if re.search(r'(.)\1{2,}', value):
        return f'{field_name} no debe contener tres o más letras repetidas consecutivamente.'
    return None

def validate_numeric_field(value, field_name):
    if not value.isdigit():
        return f'{field_name} debe ser un número entero.'
    return None

def get_inventario(page, per_page, search_criteria=None, search_query=None, order_by='id_inventario'):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar el search_criteria
    valid_criteria = ['id_inventario', 'cantidad_en_stock', 'stock_minimo', 'stock_maximo', 'nombre_producto', 'nombre_categoria']
    if search_criteria == 'nombre_producto':
        search_criteria = 'p.nombre'  # Ajustar el nombre del campo en la consulta
    elif search_criteria not in valid_criteria:
        search_criteria = None

    # Validar el order_by
    valid_order_by_columns = ['id_inventario', 'cantidad_en_stock', 'stock_minimo', 'stock_maximo']
    if order_by not in valid_order_by_columns:
        order_by = 'id_inventario'  # Valor predeterminado en caso de que order_by sea inválido

    # Consulta SQL con depuración
    if search_criteria and search_query:
        query = f"""
            SELECT i.id_inventario, i.id_producto, i.id_categoria, i.cantidad_en_stock, 
                   i.stock_minimo, i.stock_maximo, 
                   p.nombre AS nombre_producto, c.nombre_categoria
            FROM inventario i
            JOIN producto p ON i.id_producto = p.id_producto
            JOIN categorias c ON i.id_categoria = c.id_categoria
            WHERE {search_criteria} LIKE %s 
            ORDER BY {order_by} ASC
            LIMIT %s OFFSET %s
        """
        values = (f'%{search_query}%', per_page, offset)
    else:
        query = f"""
            SELECT i.id_inventario, i.id_producto, i.id_categoria, i.cantidad_en_stock, 
                   i.stock_minimo, i.stock_maximo, 
                   p.nombre AS nombre_producto, c.nombre_categoria
            FROM inventario i
            JOIN producto p ON i.id_producto = p.id_producto
            JOIN categorias c ON i.id_categoria = c.id_categoria
            ORDER BY {order_by} ASC
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        print(f"Executing query: {query}")
        print(f"Values: {values}")
        cursor.execute(query, values)
        inventario = cursor.fetchall()
        
        # Contar el total de inventarios
        if search_criteria and search_query:
            count_query = f"""
                SELECT COUNT(*) 
                FROM inventario i
                JOIN producto p ON i.id_producto = p.id_producto
                JOIN categorias c ON i.id_categoria = c.id_categoria
                WHERE {search_criteria} LIKE %s
            """
            cursor.execute(count_query, (f'%{search_query}%',))
        else:
            count_query = "SELECT COUNT(*) FROM inventario"
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        return inventario, total_count
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
        categorias = cursor.fetchall()
        return categorias
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_producto():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_producto, nombre FROM producto"
    try:
        cursor.execute(query)
        producto = cursor.fetchall()
        return producto
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def insert_inventario(id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO inventario (id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo) 
               VALUES (%s, %s, %s, %s, %s)"""
    values = (id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Producto: {id_producto}, ID Categoría: {id_categoria}, Cantidad en Stock: {cantidad_en_stock}, Stock Mínimo: {stock_minimo}, Stock Máximo: {stock_maximo}"
        log_action('Inserted', screen_name='inventario', details=details)  # Registro de log
        print("Inventario insertado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_inventario(id_inventario, id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE inventario
    SET id_producto = %s,
        id_categoria = %s,
        cantidad_en_stock = %s,
        stock_minimo = %s,
        stock_maximo = %s
    WHERE id_inventario = %s
    """
    try:
        cursor.execute(query, (id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo, id_inventario))
        connection.commit()
        details = f"ID Inventario: {id_inventario}, ID Producto: {id_producto}, ID Categoría: {id_categoria}, Cantidad en Stock: {cantidad_en_stock}, Stock Mínimo: {stock_minimo}, Stock Máximo: {stock_maximo}"
        log_action('Updated', screen_name='inventario', details=details)  # Registro de log
        print("Inventario actualizado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def delete_inventario(id_inventario):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM inventario WHERE id_inventario = %s"
    
    try:
        cursor.execute(query, (id_inventario,))
        connection.commit()
        details = f"ID Inventario: {id_inventario}"
        log_action('Deleted', screen_name='inventario', details=details)  # Registro de log
        print("Inventario eliminado exitosamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def get_inventario_by_id(id_inventario):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM inventario WHERE id_inventario = %s"
    try:
        cursor.execute(query, (id_inventario,))
        inventario = cursor.fetchone()
        return inventario
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

@app_inventario.route('/')
@check_permission('permiso_inventario')
def index_inventario():
    categorias = get_categorias()
    productos = get_producto()
    return render_template('index_inventario.html', categorias=categorias, productos=productos)

@app_inventario.route('/submit', methods=['POST'])
@check_permission('permiso_inventario')
def submit():
    id_producto = request.form.get('id_producto')
    id_categoria = request.form.get('id_categoria')
    cantidad_en_stock = request.form.get('cantidad_en_stock')
    stock_minimo = request.form.get('stock_minimo')
    stock_maximo = request.form.get('stock_maximo')
    
    error_message = None
    error_message = validate_text_field(id_producto, 'Producto')
    if error_message is None:
        error_message = validate_text_field(id_categoria, 'Categoría')
    if error_message is None:
        error_message = validate_numeric_field(cantidad_en_stock, 'Cantidad en Stock')
    if error_message is None:
        error_message = validate_numeric_field(stock_minimo, 'Stock Mínimo')
    if error_message is None:
        error_message = validate_numeric_field(stock_maximo, 'Stock Máximo')

    if error_message:
        flash(error_message)
        return redirect(url_for('index_inventario'))

    if insert_inventario(id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo):
        flash('Inventario agregado exitosamente!')
    else:
        flash('Error al agregar el inventario.')

    return redirect(url_for('index_inventario'))

@app_inventario.route('/inventario')
@check_permission('permiso_inventario')
def inventario():
    search_query = request.args.get('search_query', '')
    search_criteria = request.args.get('search_criteria', 'id_inventario')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    order_by = request.args.get('order_by', 'id_inventario')  # Por defecto, ordena por 'id_inventario'

    inventario, total_count = get_inventario(page, per_page, search_criteria, search_query, order_by)

    # Calcular el número total de páginas
    total_pages = (total_count + per_page - 1) // per_page

    # Convertir a lista de tuplas con nombres de productos y categorías
    inventario_con_categorias = [
        (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
        for item in inventario
    ]

    return render_template(
        'inventario.html',
        inventario=inventario_con_categorias,
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages,
        search_query=search_query,
        order_by=order_by
    )


@app_inventario.route('/edit_inventario/<int:id_inventario>', methods=['GET', 'POST'])
@check_permission('permiso_inventario')
def edit_inventario(id_inventario):
    if request.method == 'POST':
        id_producto = request.form.get('id_producto')
        id_categoria = request.form.get('id_categoria')
        cantidad_en_stock = request.form.get('cantidad_en_stock')
        stock_minimo = request.form.get('stock_minimo')
        stock_maximo = request.form.get('stock_maximo')
        
        # Imprimir los valores recibidos para depuración
        print(f"id_producto: {id_producto}, id_categoria: {id_categoria}, cantidad_en_stock: {cantidad_en_stock}, stock_minimo: {stock_minimo}, stock_maximo: {stock_maximo}")
        
        # Validar que los campos sean numéricos
        if not (cantidad_en_stock.isdigit() and stock_minimo.isdigit() and stock_maximo.isdigit()):
            flash('Todos los campos deben contener valores numéricos.')
            return redirect(url_for('edit_inventario', id_inventario=id_inventario))

        if update_inventario(id_inventario, id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo):
            flash('Inventario actualizado exitosamente!')
        else:
            flash('Error al actualizar el inventario.')

        return redirect(url_for('inventario'))

    inventario = get_inventario_by_id(id_inventario)
    if inventario is None:
        flash('Inventario no encontrado.')
        return redirect(url_for('inventario'))

    categorias = get_categorias()
    productos = get_producto()

    return render_template('edit_inventario.html', inventario=inventario, categorias=categorias, productos=productos)



@app_inventario.route('/eliminar_inventario/<int:id_inventario>', methods=['POST'])
@check_permission('permiso_inventario')
def eliminar_inventario(id_inventario):
    if delete_inventario(id_inventario):
        flash('Inventario eliminado exitosamente!')
    else:
        flash('Error al eliminar el inventario.')

    return redirect(url_for('inventario'))

def get_todos_inventarios():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """SELECT i.id_inventario, p.nombre AS nombre_producto, c.nombre_categoria, i.cantidad_en_stock, 
                   i.stock_minimo, i.stock_maximo
            FROM inventario i
            JOIN producto p ON i.id_producto = p.id_producto
            JOIN categorias c ON i.id_categoria = c.id_categoria"""
    try:
        cursor.execute(query)
        inventarios = cursor.fetchall()
        return inventarios
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_inventario.route('/descargar_excel')
@check_permission('permiso_inventario')
def descargar_excel():
    # Obtener todas las inventario sin paginación
    inventario = get_todos_inventarios()  # Función para obtener todas las inventario

    if not inventario:
        flash('No hay nada en el inventario para descargar.')
        return redirect(url_for('inventario'))  # Asegúrate de que la ruta 'inventario' está bien definida

    # Definir las columnas correctas
    columnas = ['id_inventario',' Nombre de producto','Categoria','cantidad en stock','stock Minimo','stock Maximo']

    # Crear un DataFrame con los datos de las inventario
    df = pd.DataFrame(inventario, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='inventario', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['inventario']
        bold_format = workbook.add_format({'bold': True})


        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de inventario', bold_format)
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='inventario.xlsx')



@app_inventario.route('/descargar_pdf')
@check_permission('permiso_inventario')
def descargar_pdf():
    # Obtener todos los inventarios y dividir en páginas de 10
    inventarios = get_todos_inventarios()
    paginacion = [inventarios[i:i + 10] for i in range(0, len(inventarios), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A3)
    ancho, alto = A3

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    primer_nombre = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, inventarios_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Inventario")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {primer_nombre}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Inventario
        data = [["ID Inventario", "ID Producto", "ID Categoría", "Cantidad en Stock", "Stock Mínimo", "Stock Máximo"]]  # Encabezado de la tabla
        data += [[inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]] for inv in inventarios_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Inventario.pdf')



if __name__ == '__main__':
    app_inventario.run(debug=True,port=5001)
