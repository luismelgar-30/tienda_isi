from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re

app_proveedores = Flask(__name__)
app_proveedores.secret_key = 'your_secret_key'

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

def insert_user(Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca):
    connection = create_connection()
    if connection is None:
        return
    cursor = connection.cursor()
    query = "INSERT INTO proveedores (Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca)
    try:
        cursor.execute(query, values)
        connection.commit()
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def get_proveedor(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT * FROM proveedores LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        proveedores = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) FROM proveedores")
        total_count = cursor.fetchone()[0]
        return proveedores, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_proveedor_by_id(id_proveedor):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM proveedores WHERE id_proveedor = %s"
    try:
        cursor.execute(query, (id_proveedor,))
        proveedores = cursor.fetchone()
        return proveedores
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def update_user(id_proveedor, Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE proveedores
    SET Nombre_del_proveedor = %s, Contacto = %s, Producto_Servicio = %s, Historial_de_desempeño = %s, id_pedido = %s, id_marca = %s
    WHERE id_proveedor = %s
    """
    values = (Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca, id_proveedor)
    try:
        cursor.execute(query, values)
        connection.commit()
        print(f"Updated {cursor.rowcount} rows")  
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def delete_user(id_proveedor):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM proveedores WHERE id_proveedor = %s"
    try:
        cursor.execute(query, (id_proveedor,))
        connection.commit()
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def search_users(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"SELECT * FROM proveedores WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        proveedores = cursor.fetchall()
        count_query = f"SELECT COUNT(*) FROM proveedores WHERE {search_criteria} LIKE %s"
        cursor.execute(count_query, (f'%{search_query}%',))
        total_count = cursor.fetchone()[0]
        return proveedores, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()



def validate_input(field_value, field_type='text'):
    if not field_value:
        return False
    if field_type == 'text':
        if len(field_value) < 3 or len(field_value) > 20:
            return False
        if re.search(r'\d', field_value):
            return False
        if re.search(r'(.)\1{2,}', field_value):
            return False
        if all(char in "!?@#$%^&*()_+-=[]{};':\",.<>/?\\" for char in field_value):
            return False
    elif field_type == 'number':
        if not field_value.isdigit() or len(field_value) > 4:
            return False
    return True

@app_proveedores.route('/')
def index_proveedores():
    return render_template('index_proveedores.html')

@app_proveedores.route('/proveedores')
def proveedores():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query')
    page = int(request.args.get('page', 1))
    per_page = 10

    if search_criteria and search_query:
        proveedores, total_count = search_users(search_criteria, search_query, page, per_page)
    else:
        proveedores, total_count = get_proveedor(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('proveedores.html', proveedores=proveedores, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages)



@app_proveedores.route('/submit', methods=['POST'])
def submit():
    Nombre_del_proveedor = request.form['Nombre_del_proveedor']
    Contacto = request.form['Contacto']
    Producto_Servicio = request.form['Producto_Servicio']
    Historial_de_desempeño = request.form['Historial_de_desempeño']
    id_pedido = request.form['id_pedido']
    id_marca = request.form['id_marca']

    if not all(validate_input(field, 'text') for field in [Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño]) or \
       not all(validate_input(field, 'number') for field in [id_pedido, id_marca]):
        flash('OJO Todos los campos son necesarios. Los campos de texto deben tener entre 3 y 20 caracteres, no contener números, no repetir la misma letra tres veces seguidas ni contener solo signos. Los campos id_pedido e id_marca deben ser números y tener máximo 4 dígitos.')
        return redirect(url_for('index_proveedores'))

    if insert_user(Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca):
        flash('User inserted successfully!')
    else:
        flash('An error occurred while inserting the user.')

    return redirect(url_for('index_proveedores'))

@app_proveedores.route('/edit/<int:id_proveedor>', methods=['GET', 'POST'])
def edit_proveedores(id_proveedor):
    if request.method == 'POST':
        Nombre_del_proveedor = request.form['Nombre_del_proveedor']
        Contacto = request.form['Contacto']
        Producto_Servicio = request.form['Producto_Servicio']
        Historial_de_desempeño = request.form['Historial_de_desempeño']
        id_pedido = request.form['id_pedido']
        id_marca = request.form['id_marca']

        if not all(validate_input(field, 'text') for field in [Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño]) or \
           not all(validate_input(field, 'number') for field in [id_pedido, id_marca]):
            flash('Todos los campos son necesarios. Los campos de texto deben tener entre 3 y 20 caracteres, no contener números, no repetir la misma letra tres veces seguidas ni contener solo signos. Los campos id_pedido e id_marca deben ser números y tener máximo 4 dígitos.')
            return redirect(url_for('edit_proveedores', id_proveedor=id_proveedor))

        if update_user(id_proveedor, Nombre_del_proveedor, Contacto, Producto_Servicio, Historial_de_desempeño, id_pedido, id_marca):
            flash('User updated successfully!')
        else:
            flash('An error occurred while updating the user.')

        return redirect(url_for('proveedores'))

    proveedores = get_proveedor_by_id(id_proveedor)
    if proveedores is None:
        flash('Proveedor not found!')
        return redirect(url_for('proveedores'))
    return render_template('edit_proveedores.html', proveedores=proveedores)

@app_proveedores.route('/eliminar/<int:id_proveedor>', methods=['GET', 'POST'])
def eliminar_proveedores(id_proveedor):
    if request.method == 'POST':
        if delete_user(id_proveedor):
            flash('Product deleted successfully!')
        else:
            flash('An error occurred while deleting the product.')
        return redirect(url_for('proveedores'))

    proveedores = get_proveedor_by_id(id_proveedor)
    if proveedores is None:
        flash('Product not found!')
        return redirect(url_for('proveedor'))
    return render_template('eliminar_proveedores.html', proveedores=proveedores)

if __name__ == '__main__':
    app_proveedores.run(debug=True, port=5005)
