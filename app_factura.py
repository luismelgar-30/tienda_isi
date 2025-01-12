from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app_factura = Flask(__name__)
app_factura.secret_key = 'your_secret_key'

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

def insert_factura(id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    INSERT INTO factura (id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total)
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

def get_facturas(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
    SELECT SQL_CALC_FOUND_ROWS f.id_factura, s.cai, e.nombre, c.documento, p.id_pedido, pr.nombre, 
           f.cantidad, f.precio_unitario, f.subtotal, i.tasa_impuesto, f.total
    FROM factura f
    JOIN sar s ON f.id_sar = s.id_sar
    JOIN empleados e ON f.nombre = e.id_empleado
    JOIN cliente c ON f.documento = c.documento
    JOIN pedido_de_compra_cliente p ON f.id_pedido = p.id_pedido
    JOIN producto pr ON f.id_producto = pr.id_producto
    JOIN impuesto i ON f.id_impuesto = i.id_impuesto
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (per_page, offset))
        facturas = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_facturas = cursor.fetchone()[0]
        return facturas, total_facturas
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()
        

def get_factura_by_id(id_factura):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT f.id_factura, f.id_sar, f.nombre, f.documento, f.id_pedido, f.id_producto, f.cantidad, 
           f.precio_unitario, f.subtotal, f.id_impuesto, f.total
    FROM factura f
    WHERE f.id_factura = %s
    """
    try:
        cursor.execute(query, (id_factura,))
        factura = cursor.fetchone()
        return factura
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def update_factura(id_factura, id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE factura
    SET id_sar = %s, nombre = %s, documento = %s, id_pedido = %s, id_producto = %s, cantidad = %s, 
        precio_unitario = %s, subtotal = %s, id_impuesto = %s, total = %s
    WHERE id_factura = %s
    """
    values = (id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total, id_factura)
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

def delete_factura(id_factura):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM factura WHERE id_factura = %s"
    try:
        cursor.execute(query, (id_factura,))
        connection.commit()
        return True
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return False
    finally:
        cursor.close()
        connection.close()

@app_factura.route('/')
def index_factura():
    connection = create_connection()
    if connection is None:
        return render_template('index_factura.html', sar=[], empleados=[], clientes=[], pedidos=[], productos=[], impuestos=[])

    cursor = connection.cursor()

    cursor.execute("SELECT id_sar, cai FROM sar")
    sar = cursor.fetchall()

    cursor.execute("SELECT id_empleado, nombre FROM empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT documento FROM cliente")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_pedido FROM pedido_de_compra_cliente")
    pedidos = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre, original_precio FROM producto")
    productos = cursor.fetchall()

    cursor.execute("SELECT id_impuesto, tasa_impuesto FROM impuesto")
    impuestos = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('index_factura.html', sar=sar, empleados=empleados, clientes=clientes, pedidos=pedidos, productos=productos, impuestos=impuestos)



@app_factura.route('/facturas')
def facturas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    facturas, total_facturas = get_facturas(page, per_page)
    total_pages = (total_facturas + per_page - 1) // per_page
    return render_template('facturas.html', facturas=facturas, page=page, per_page=per_page, total_facturas=total_facturas, total_pages=total_pages)

@app_factura.route('/submit_factura', methods=['POST'])
def submit_factura():
    id_sar = request.form['id_sar']
    nombre = request.form['nombre']
    documento = request.form['documento']
    id_pedido = request.form['id_pedido']
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']
    precio_unitario = request.form['precio_unitario']
    subtotal = request.form['subtotal']
    id_impuesto = request.form['id_impuesto']
    total = request.form['total']

    if not id_sar or not nombre or not documento or not id_pedido or not id_producto or not cantidad or not precio_unitario or not id_impuesto:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_factura'))

    if insert_factura(id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
        flash('Factura insertada exitosamente!')
    else:
        flash('Ocurrió un error al insertar la factura.')
    
    return redirect(url_for('index_factura'))

@app_factura.route('/edit_factura/<int:id_factura>', methods=['GET', 'POST'])
def edit_factura(id_factura):
    if request.method == 'POST':
        id_sar = request.form['id_sar']
        nombre = request.form['nombre']
        documento = request.form['documento']
        id_pedido = request.form['id_pedido']
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        precio_unitario = request.form['precio_unitario']
        subtotal = request.form['subtotal']
        id_impuesto = request.form['id_impuesto']
        total = request.form['total']

        if not id_sar or not nombre or not documento or not id_pedido or not id_producto or not cantidad or not precio_unitario or not id_impuesto:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_factura', id_factura=id_factura))

        if update_factura(id_factura, id_sar, nombre, documento, id_pedido, id_producto, cantidad, precio_unitario, subtotal, id_impuesto, total):
            flash('Factura actualizada exitosamente!')
        else:
            flash('Ocurrió un error al actualizar la factura.')
        
        return redirect(url_for('facturas'))

    factura = get_factura_by_id(id_factura)
    if factura is None:
        flash('Factura no encontrada!')
        return redirect(url_for('facturas'))

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id_sar, cai FROM sar")
    sar = cursor.fetchall()

    cursor.execute("SELECT id_empleado, nombre FROM empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT documento FROM cliente")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id_pedido FROM detalle_de_compra_cliente")
    pedidos = cursor.fetchall()

    cursor.execute("SELECT id_producto, nombre FROM producto")
    productos = cursor.fetchall()

    cursor.execute("SELECT id_impuesto, tasa_impuesto FROM impuesto")
    impuestos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('edit_factura.html', factura=factura, sar=sar, empleados=empleados, clientes=clientes, pedidos=pedidos, productos=productos, impuestos=impuestos)

@app_factura.route('/eliminar_factura/<int:id_factura>', methods=['POST'])
def eliminar_factura(id_factura):
    if delete_factura(id_factura):
        flash('Factura eliminada exitosamente!')
    else:
        flash('Ocurrió un error al eliminar la factura.')
    
    return redirect(url_for('facturas'))

if __name__ == '__main__':
    app_factura.run(port=5000, debug=True)
