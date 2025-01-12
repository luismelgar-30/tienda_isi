from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app_detalles_compra = Flask(__name__)
app_detalles_compra.secret_key = 'your_secret_key'

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
            print("Conexión exitosa a la base de datos MySQL")
    except Error as e:
        print(f"Error '{e}' ocurrió")
    return connection

def insert_detalle(id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    query = """
        INSERT INTO detalle_de_compra_cliente
        (id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total))
        connection.commit()
        return True  # Return True on successful insert
    except Exception as e:  # Catching general exceptions here
        print(f"Error '{e}' occurred")
        return False  # Return False on error
    finally:
        cursor.close()
        connection.close()


def get_precio(id_producto):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return {'precio_unitario': 0}, 500

    cursor = connection.cursor()
    query = """
    SELECT original_precio
    FROM producto
    WHERE id_producto = %s
    """
    try:
        cursor.execute(query, (id_producto,))
        result = cursor.fetchone()
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return {'precio_unitario': 0}, 500
    finally:
        cursor.close()
        connection.close()

    if result:
        return {'precio_unitario': result[0]}, 200
    else:
        return {'precio_unitario': 0}, 404

def get_detalles(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
    SELECT SQL_CALC_FOUND_ROWS d.id_detalle, p.id_pedido, e.nombre AS nombre_empleado, pr.nombre AS nombre_producto, 
           d.cantidad, d.precio_unitario, d.subtotal, i.tasa_impuesto, d.total
    FROM detalle_de_compra_cliente d
    JOIN pedido_de_compra_cliente p ON d.id_pedido = p.id_pedido
    JOIN empleados e ON d.id_empleado = e.id_empleado
    JOIN producto pr ON d.id_producto = pr.id_producto
    JOIN impuesto i ON d.id_impuesto = i.id_impuesto
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (per_page, offset))
        detalles = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_detalles = cursor.fetchone()[0]
        return detalles, total_detalles
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_detalle_by_id(id_detalle):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT d.id_detalle, d.id_pedido, d.id_empleado, d.id_producto, d.cantidad, d.precio_unitario, 
           d.subtotal, d.id_impuesto, d.total
    FROM detalle_de_compra_cliente d
    WHERE d.id_detalle = %s
    """
    try:
        cursor.execute(query, (id_detalle,))
        detalle = cursor.fetchone()
        return detalle
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def update_detalle(id_detalle, id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE detalle_de_compra_cliente
    SET id_pedido = %s, id_empleado = %s, id_producto = %s, cantidad = %s, precio_unitario = %s, 
        subtotal = %s, id_impuesto = %s, total = %s
    WHERE id_detalle = %s
    """
    values = (id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total, id_detalle)
    try:
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return False
    finally:
        cursor.close()
        connection.close()

def delete_detalle(id_detalle):
    connection = create_connection()  # Create a database connection
    if connection is None:
        return False  # If the connection failed, return False

    cursor = connection.cursor()  # Create a cursor to execute SQL queries
    query = "DELETE FROM detalle_de_compra_cliente WHERE id_detalle = %s"
    try:
        cursor.execute(query, (id_detalle,))  # Execute the delete query
        connection.commit()  # Commit the changes
        return True  # Return True on successful deletion
    except Exception as e:
        print(f"Error '{e}' occurred")  # Print any error that occurs
        return False  # Return False if an error occurred
    finally:
        cursor.close()  # Ensure the cursor is closed
        connection.close()  # Ensure the connection is closed


@app_detalles_compra.route('/get_stock/<int:id_producto>', methods=['GET'])
def get_stock(id_producto):
    connection = create_connection()
    if connection is None:
        return {'stock': 'N/A'}, 500
    
    cursor = connection.cursor()
    query = """
    SELECT cantidad_en_stock, stock_minimo, stock_maximo
    FROM inventario
    WHERE id_producto = %s
    """
    cursor.execute(query, (id_producto,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if result:
        cantidad_en_stock, stock_minimo, stock_maximo = result
        return {'stock': cantidad_en_stock, 'stock_minimo': stock_minimo, 'stock_maximo': stock_maximo}, 200
    else:
        return {'stock': 0, 'stock_minimo': 0, 'stock_maximo': 1000}, 404


@app_detalles_compra.route('/')
def index_detalles():
    connection = create_connection()
    if connection is None:
        return render_template('index_detalles.html', pedidos=[], empleados=[], productos=[], impuestos=[])
    
    cursor = connection.cursor()

    cursor.execute("SELECT id_pedido FROM pedido_de_compra_cliente")
    pedidos = cursor.fetchall()

    cursor.execute("SELECT id_empleado, nombre FROM empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre, original_precio FROM producto")
    productos = cursor.fetchall()

    cursor.execute("SELECT id_impuesto, tasa_impuesto FROM impuesto")
    impuestos = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('index_detalles.html', pedidos=pedidos, empleados=empleados, productos=productos, impuestos=impuestos)

@app_detalles_compra.route('/detalles_compra')
def detalles_compra():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    detalles, total_detalles = get_detalles(page, per_page)
    total_pages = (total_detalles + per_page - 1) // per_page
    return render_template('detalles_compra.html', detalles=detalles, page=page, per_page=per_page, total_detalles=total_detalles, total_pages=total_pages)

@app_detalles_compra.route('/submit_detalle', methods=['POST'])
def submit_detalle():
    id_pedido = request.form['id_pedido']
    id_empleado = request.form['id_empleado']
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']
    precio_unitario = request.form['precio_unitario']
    subtotal = request.form['subtotal']
    id_impuesto = request.form['id_impuesto']
    total = request.form['total']

    if not id_pedido or not id_empleado or not id_producto or not cantidad or not precio_unitario or not id_impuesto:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_detalles'))

    if insert_detalle(id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
        flash('Detalle insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el detalle.')
    
    return redirect(url_for('index_detalles'))

@app_detalles_compra.route('/edit_detalle/<int:id_detalle>', methods=['GET', 'POST'])
def edit_detalle(id_detalle):
    if request.method == 'POST':
        id_pedido = request.form['id_pedido']
        id_empleado = request.form['id_empleado']
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        precio_unitario = request.form['precio_unitario']
        subtotal = request.form['subtotal']
        id_impuesto = request.form['id_impuesto']
        total = request.form['total']

        # Depuración: Verifica los valores recibidos
        print(f"Actualizar detalle: {id_detalle}, Precio Unitario: {precio_unitario}")

        if not id_pedido or not id_empleado or not id_producto or not cantidad or not precio_unitario or not id_impuesto:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_detalle', id_detalle=id_detalle))

        if update_detalle(id_detalle, id_pedido, id_empleado, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
            flash('Detalle actualizado exitosamente!')
        else:
            flash('Ocurrió un error al actualizar el detalle.')
        
        return redirect(url_for('detalles_compra'))

    detalle = get_detalle_by_id(id_detalle)
    if detalle is None:
        flash('Detalle no encontrado!')
        return redirect(url_for('detalles_compra'))

    # Depuración: Verifica el detalle recuperado
    print(f"Detalle encontrado: {detalle}")

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id_pedido FROM pedido_de_compra_cliente")
    pedidos = cursor.fetchall()

    cursor.execute("SELECT id_empleado, nombre FROM empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre FROM producto")
    productos = cursor.fetchall()

    cursor.execute("SELECT id_impuesto, tasa_impuesto FROM impuesto")
    impuestos = cursor.fetchall()
    
    precio= get_precio(id_producto)

    cursor.close()
    connection.close()

    return render_template('edit_detalle.html', detalle=detalle,precio=precio, pedidos=pedidos, empleados=empleados, productos=productos, impuestos=impuestos)

@app_detalles_compra.route('/get_precio/<int:id_producto>', methods=['GET'])
def get_precio(id_producto):
    connection = create_connection()
    if connection is None:
        return {'precio_unitario': 0}, 500

    cursor = connection.cursor()
    query = """
    SELECT original_precio
    FROM producto
    WHERE id_producto = %s
    """
    try:
        cursor.execute(query, (id_producto,))
        result = cursor.fetchone()
        print(f"Resultado de la consulta: {result}")  # Mensaje de depuración
    except Error as e:
        print(f"Error al ejecutar la consulta: {e}")
        return {'precio_unitario': 0}, 500
    finally:
        cursor.close()
        connection.close()

    if result:
        return {'precio_unitario': result[0]}, 200
    else:
        print(f"No se encontró el producto con ID: {id_producto}")  # Mensaje de depuración
        return {'precio_unitario': 0}, 404


@app_detalles_compra.route('/delete_detalle/<int:id_detalle>')
def eliminar_detalle(id_detalle):  # Cambié el nombre aquí
    if delete_detalle(id_detalle):  # Esta es la función que elimina el detalle de la base de datos
        flash('Detalle eliminado exitosamente!')
    else:
        flash('Ocurrió un error al eliminar el detalle.')
    return redirect(url_for('detalles_compra'))



if __name__ == '__main__':
    app_detalles_compra.run(debug=True,port=5023)
