from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from mysql.connector import Error
import re


app_usuarios = Flask(__name__)
app_usuarios.secret_key = 'your_secret_key'

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

def insert_user(primer_nombre, primer_apellido, correo, password, id_sucursal, id_rol):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    INSERT INTO usuarios (primer_nombre, primer_apellido, correo, password, usuario_activo, super_usuario, id_sucursal, id_rol)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (primer_nombre, primer_apellido, correo, password, 1, 0, id_sucursal, id_rol)
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


def update_user(id_usuario, primer_nombre, primer_apellido, correo, password, usuario_activo, super_usuario, id_sucursal, id_rol):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = """
    UPDATE usuarios 
    SET primer_nombre = %s, primer_apellido = %s, correo = %s, password = %s, usuario_activo = %s, super_usuario = %s, id_sucursal = %s, id_rol = %s 
    WHERE id_usuario = %s
    """
    values = (primer_nombre, primer_apellido, correo, password, usuario_activo, super_usuario, id_sucursal, id_rol, id_usuario)
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


def delete_user(id_usuario):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM usuarios WHERE id_usuario = %s"
    try:
        cursor.execute(query, (id_usuario,))
        connection.commit()
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def get_usuarios(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = """
    SELECT u.id_usuario, u.primer_nombre, u.primer_apellido, u.correo, u.password, 
           u.usuario_activo, u.super_usuario, s.ciudad, COALESCE(r.nombre_rol, 'Sin rol') AS nombre_rol
    FROM usuarios u
    JOIN sucursales s ON u.id_sucursal = s.id_sucursal
    LEFT JOIN roles r ON u.id_rol = r.id_rol
    LIMIT %s OFFSET %s
    """
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

def get_roles():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_rol, nombre_rol,descripcion FROM roles"  # Suponiendo que la tabla se llama 'roles'
    cursor.execute(query)
    roles = cursor.fetchall()
    cursor.close()
    connection.close()
    return roles


def search_usuarios(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"""
    SELECT SQL_CALC_FOUND_ROWS u.*, s.ciudad
    FROM usuarios u
    JOIN sucursales s ON u.id_sucursal = s.id_sucursal
    WHERE {search_criteria} LIKE %s
    LIMIT %s OFFSET %s
    """
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        usuarios = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return usuarios, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_usuarios_by_id(id_usuario):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT u.id_usuario, u.primer_nombre, u.primer_apellido, u.correo, u.password, u.usuario_activo, u.super_usuario, u.id_sucursal, s.ciudad, u.id_rol
    FROM usuarios u
    JOIN sucursales s ON u.id_sucursal = s.id_sucursal
    WHERE u.id_usuario = %s
    """
    cursor.execute(query, (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    connection.close()
    return usuario


def get_sucursales():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_sucursal, ciudad FROM sucursales"
    cursor.execute(query)
    sucursales = cursor.fetchall()
    cursor.close()
    connection.close()
    return sucursales

def validate_user_data(primer_nombre, primer_apellido, correo, password):
    if not primer_nombre or not primer_apellido or not correo or not password:
        return False, 'Todos los campos son requeridos.'

    if len(primer_nombre) < 3 or len(primer_nombre) > 15 or len(primer_apellido) < 3 or len(primer_apellido) > 15:
        return False, 'Nombre y apellido deben tener entre 3 y 15 caracteres.'

    if re.search(r'[^A-Za-z]', primer_nombre) or re.search(r'[^A-Za-z]', primer_apellido):
        return False, 'Nombre y apellido deben contener solo letras.'

    if re.search(r'(.)\1{2,}', primer_nombre) or re.search(r'(.)\1{2,}', primer_apellido):
        return False, 'No se permiten tres letras repetidas consecutivamente.'

    if not re.match(r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+', correo):
        return False, 'Formato de correo inválido.'

    

    return True, 'Validación exitosa.'

@app_usuarios.route('/')
@check_permission('permiso_usuario')
def usuarios():
    search_criteria = request.args.get('search_criteria', 'ciudad')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    if search_query:
        usuarios, total_count = search_usuarios(search_criteria, search_query, page, per_page)
    else:
        usuarios, total_count = get_usuarios(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('usuarios.html', usuarios=usuarios, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_usuarios.route('/submit', methods=['POST'])
@check_permission('permiso_usuario')
def submit():
    primer_nombre = request.form['primer_nombre']
    primer_apellido = request.form['primer_apellido']
    correo = request.form['correo']
    password = request.form['password']
    id_sucursal = request.form['id_sucursal']
    id_rol = request.form['id_rol']  # Add this line

    valid, message = validate_user_data(primer_nombre, primer_apellido, correo, password)
    if not valid:
        flash(message)
        return redirect(url_for('usuarios'))  # Corregido aquí

    if insert_user(primer_nombre, primer_apellido, correo, password, id_sucursal, id_rol):  # Add id_rol here
        flash('Usuario ingresado exitosamente.')
    else:
        flash('Ocurrió un error al ingresar el usuario.')
    
    return redirect(url_for('usuarios'))  # Corregido aquí

@app_usuarios.route('/edit_usuarios/<int:id_usuario>', methods=['GET', 'POST'])
@check_permission('permiso_usuario')
def edit_usuarios(id_usuario):
    if request.method == 'POST':
        primer_nombre = request.form['primer_nombre']
        primer_apellido = request.form['primer_apellido']
        correo = request.form['correo']
        password = request.form['password']
        usuario_activo = request.form['usuario_activo']
        super_usuario = request.form['super_usuario']
        id_sucursal = request.form['id_sucursal']
        id_rol = request.form['id_rol']  # Add this line

        valid, message = validate_user_data(primer_nombre, primer_apellido, correo, password)
        if not valid:
            flash(message)
            return redirect(url_for('edit_usuarios', id_usuario=id_usuario))

        if update_user(id_usuario, primer_nombre, primer_apellido, correo, password, usuario_activo, super_usuario, id_sucursal, id_rol):
            flash('Usuario actualizado exitosamente.')
        else:
            flash('Ocurrió un error al actualizar el usuario.')

        return redirect(url_for('usuarios'))  # Corregido aquí

    else:
        usuario = get_usuarios_by_id(id_usuario)
        sucursales = get_sucursales()
        roles = get_roles()  # Fetch roles here
        if usuario:
            return render_template('edit_usuarios.html', usuario=usuario, sucursales=sucursales, roles=roles)
        else:
            flash('Usuario no encontrado.')
            return redirect(url_for('usuarios'))



@app_usuarios.route('/eliminar_usuarios/<int:id_usuario>', methods=['GET', 'POST'])
@check_permission('permiso_usuario')
def eliminar_usuarios(id_usuario):
    if request.method == 'POST':
        if delete_user(id_usuario):
            flash('¡usuarios eliminada exitosamente!')
            return redirect(url_for('usuarios'))
        else:
            flash('Ocurrió un error al eliminar el usuarios. Por favor, intente nuevamente.')
            return redirect(url_for('usuarios'))

    usuarios = get_usuarios_by_id(id_usuario)
    if usuarios is None:
        flash('usuarios no encontrada.')
        return redirect(url_for('usuarios'))

    return render_template('eliminar_usuarios.html', usuarios=usuarios)

if __name__ == "__main__":
    app_usuarios.run(debug=True, port=5034)
