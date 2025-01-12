from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re

app_inventario_almacenes = Flask(__name__)
app_inventario_almacenes.secret_key = 'your_secret_key'  # Cambia 'your_secret_key' por una clave secreta segura

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="proyecto_is1"
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

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

def insert_inventario_almacen(id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """INSERT INTO inventario_almacenes (id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo) VALUES (%s, %s, %s, %s, %s)"""
    values = (id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Inventario en almacén insertado exitosamente.")
        return True
    except Error as e:
        print(f"Error al insertar el inventario en almacén: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def get_inventario_almacen(page, per_page, search_criteria=None, search_query=None):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return [], 0

    cursor = connection.cursor()
    offset = (page - 1) * per_page

    if search_criteria and search_query:
        query = f"""
            SELECT ia.id_inventario_almacenes, a.nombre AS nombre_almacen, p.nombre AS nombre_producto, 
                   ia.cantidad_en_stock, ia.stock_minimo, ia.stock_maximo, ia.fecha_ultima_actualizacion
            FROM inventario_almacenes ia
            JOIN almacenes a ON ia.id_almacenes = a.id_almacenes
            JOIN producto p ON ia.id_producto = p.id_producto
            WHERE {search_criteria} LIKE %s 
            LIMIT %s OFFSET %s
        """
        values = (f'%{search_query}%', per_page, offset)
    else:
        query = """
            SELECT ia.id_inventario_almacenes, a.nombre AS nombre_almacen, p.nombre AS nombre_producto, 
                   ia.cantidad_en_stock, ia.stock_minimo, ia.stock_maximo, ia.fecha_ultima_actualizacion
            FROM inventario_almacenes ia
            JOIN almacenes a ON ia.id_almacenes = a.id_almacenes
            JOIN producto p ON ia.id_producto = p.id_producto
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        cursor.execute(query, values)
        inventario_almacen = cursor.fetchall()

        # Get the total count of records
        count_query = """
            SELECT COUNT(*) 
            FROM inventario_almacenes ia
            JOIN almacenes a ON ia.id_almacenes = a.id_almacenes
            JOIN producto p ON ia.id_producto = p.id_producto
        """
        if search_criteria and search_query:
            count_query += f" WHERE {search_criteria} LIKE %s"
            cursor.execute(count_query, (f'%{search_query}%',))
        else:
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        return inventario_almacen, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_categorias():
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
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
        print("Error: No se pudo conectar a la base de datos.")
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

def update_inventario_almacen(id_inventario_almacenes, id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE inventario_almacenes
    SET id_almacenes = %s,
        id_producto = %s,
        cantidad_en_stock = %s,
        stock_minimo = %s,
        stock_maximo = %s
    WHERE id_inventario_almacenes = %s
    """
    
    try:
        cursor.execute(query, (id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo, id_inventario_almacenes))
        connection.commit()
        print("Inventario en almacén actualizado exitosamente.")
        return True
    except Error as e:
        print(f"Error al actualizar el inventario en almacén: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def delete_inventario_almacen(id_inventario_almacenes):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM inventario_almacenes WHERE id_inventario_almacenes = %s"
    
    try:
        cursor.execute(query, (id_inventario_almacenes,))
        connection.commit()
        print("Inventario en almacén eliminado exitosamente.")
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def get_inventario_almacen_by_id(id_inventario_almacenes):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return None
    
    cursor = connection.cursor()
    query = "SELECT * FROM inventario_almacenes WHERE id_inventario_almacenes = %s"
    
    try:
        cursor.execute(query, (id_inventario_almacenes,))
        inventario_almacen = cursor.fetchone()
        return inventario_almacen
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

@app_inventario_almacenes.route('/')
def index_inventario():
    categorias = get_categorias()
    productos = get_producto()
    return render_template('index_inventario_almacenes.html', categorias=categorias, productos=productos)

@app_inventario_almacenes.route('/submit', methods=['POST'])
def submit():
    id_almacenes = request.form.get('id_almacenes')
    id_producto = request.form.get('id_producto')
    cantidad_en_stock = request.form.get('cantidad_en_stock')
    stock_minimo = request.form.get('stock_minimo')
    stock_maximo = request.form.get('stock_maximo')
    
    error_message = None
    error_message = validate_numeric_field(id_almacenes, 'Almacén')
    if error_message is None:
        error_message = validate_numeric_field(id_producto, 'Producto')
    if error_message is None:
        error_message = validate_numeric_field(cantidad_en_stock, 'Cantidad en Stock')
    if error_message is None:
        error_message = validate_numeric_field(stock_minimo, 'Stock Mínimo')
    if error_message is None:
        error_message = validate_numeric_field(stock_maximo, 'Stock Máximo')

    if error_message:
        flash(error_message)
        return redirect(url_for('index_inventario'))

    if insert_inventario_almacen(id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo):
        flash('Inventario en almacén agregado exitosamente!')
    else:
        flash('Error al agregar el inventario en almacén.')

    return redirect(url_for('index_inventario'))

@app_inventario_almacenes.route('/inventario_almacen')
def inventario_almacen():
    search_query = request.args.get('search_query', '')
    search_criteria = request.args.get('search_criteria', 'id_inventario_almacenes')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))  # Ensure per_page is an integer

    inventario_almacen, total_count = get_inventario_almacen(page, per_page, search_criteria, search_query)

    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('inventario_almacenes.html', 
                           inventario_almacen=inventario_almacen, 
                           total_count=total_count, 
                           search_query=search_query, 
                           search_criteria=search_criteria, 
                           page=page, 
                           per_page=per_page, 
                           total_pages=total_pages)


@app_inventario_almacenes.route('/edit/<int:id_inventario_almacenes>', methods=['GET', 'POST'])
def edit(id_inventario_almacenes):
    inventario = get_inventario_almacen_by_id(id_inventario_almacenes)
    if request.method == 'POST':
        id_almacenes = request.form.get('id_almacenes')
        id_producto = request.form.get('id_producto')
        cantidad_en_stock = request.form.get('cantidad_en_stock')
        stock_minimo = request.form.get('stock_minimo')
        stock_maximo = request.form.get('stock_maximo')

        if update_inventario_almacen(id_inventario_almacenes, id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo):
            flash('Inventario en almacén actualizado exitosamente!')
            return redirect(url_for('inventario_almacen'))
        else:
            flash('Error al actualizar el inventario en almacén.')

    categorias = get_categorias()
    productos = get_producto()
    return render_template('edit_inventario_almacenes.html', inventario=inventario, categorias=categorias, productos=productos)

@app_inventario_almacenes.route('/delete/<int:id_inventario_almacenes>', methods=['POST'])
def delete(id_inventario_almacenes):
    if delete_inventario_almacen(id_inventario_almacenes):
        flash('Inventario en almacén eliminado exitosamente!')
    else:
        flash('Error al eliminar el inventario en almacén.')
    return redirect(url_for('inventario_almacen'))

if __name__ == '__main__':
    app_inventario_almacenes.run(debug=True,port=5035)
