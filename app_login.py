import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import re

app_login = Flask(__name__)
app_login.secret_key = 'your_secret_key'

# Diccionario para almacenar intentos fallidos
failed_attempts = {}

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

    if len(password) < 6 or len(password) > 20:
        return False, 'La contraseña debe tener entre 6 y 20 caracteres.'

    return True, 'Validación exitosa.'

def verify_user(correo, password):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False

    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT id_usuario, primer_nombre, primer_apellido, correo, password, usuario_activo, super_usuario, id_sucursal, id_rol
        FROM usuarios
        WHERE correo = %s
    """
    values = (correo,)
    try:
        cursor.execute(query, values)
        user = cursor.fetchone()

        if user:
            # Imprimir para verificar si se recuperó el usuario correctamente
            print(f"Usuario encontrado: {user['correo']}")
            print(f"Contraseña ingresada: {password}")
            print(f"Contraseña almacenada (hash): {user['password']}")

            # Verificar si la contraseña ingresada coincide con el hash almacenado
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                print("Contraseña correcta.")
                
                if user['usuario_activo'] == 0:
                    print("El usuario está inactivo.")
                    return False
                
                # Limpiar los intentos fallidos si la contraseña es correcta
                if correo in failed_attempts:
                    del failed_attempts[correo]
                return user
            else:
                print("Contraseña incorrecta.")
                # Manejo de intentos fallidos
                if correo not in failed_attempts:
                    failed_attempts[correo] = 0
                failed_attempts[correo] += 1
                if failed_attempts[correo] >= 3:
                    cursor.execute("UPDATE usuarios SET usuario_activo = 0 WHERE correo = %s", (correo,))
                    connection.commit()
                return False
        else:
            print("No se encontró un usuario con ese correo.")
        return False
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()



def get_permissions_for_role_by_screen(id_rol):
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT id_permiso_pantalla, permiso_crear, permiso_editar, permiso_eliminar, permiso_ver,permiso_buscador,permiso_exportar_pdf,permiso_exportar_excel
        FROM permisos
        WHERE id_rol = %s
    """
    try:
        cursor.execute(query, (id_rol,))
        permissions = cursor.fetchall()
        return permissions if permissions else []
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()


def get_module_permissions_for_role(id_rol):
    connection = create_connection()
    if connection is None:
        return {}
    cursor = connection.cursor(dictionary=True)
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
        module_permissions = cursor.fetchone()
        return module_permissions if module_permissions else {}
    except Error as e:
        print(f"The error '{e}' occurred")
        return {}
    finally:
        cursor.close()
        connection.close()

@app_login.route('/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    correo = request.form['correo']
    password = request.form['password']
    user = verify_user(correo, password)
    
    if user:
        if user['usuario_activo'] == 0:
            flash('Usuario está bloqueado, por favor comuníquese con el administrador.')
            return redirect(url_for('index_login'))
        else:
            # Obtener permisos de acción y de módulos para el rol del usuario
            action_permissions = get_permissions_for_role_by_screen(user['id_rol'])
            module_permissions = get_module_permissions_for_role(user['id_rol'])
            
            # Guardar la información básica del usuario en la sesión
            session['primer_nombre'] = user['primer_nombre']
            session['primer_apellido'] = user['primer_apellido']
            session['super_usuario'] = user['super_usuario']
            session['correo'] = user['correo']
            session['id_sucursal'] = user['id_sucursal']
            session['id_rol'] = user['id_rol']
            
            # Guardar los permisos de acción en la sesión
            if action_permissions:
                # Asignar permisos de acción por pantalla
                for perm in action_permissions:
                    screen_id = perm['id_permiso_pantalla']
                    session[f'permiso_crear_{screen_id}'] = perm.get('permiso_crear', 0)
                    session[f'permiso_editar_{screen_id}'] = perm.get('permiso_editar', 0)
                    session[f'permiso_eliminar_{screen_id}'] = perm.get('permiso_eliminar', 0)
                    session[f'permiso_ver_{screen_id}'] = perm.get('permiso_ver', 0)
                    session[f'permiso_buscador_{screen_id}'] = perm.get('permiso_buscador', 0)
                    session[f'permiso_exportar_pdf_{screen_id}'] = perm.get('permiso_exportar_pdf', 0)
                    session[f'permiso_exportar_excel_{screen_id}'] = perm.get('permiso_exportar_excel', 0)
            
            # Guardar los permisos de módulo en la sesión
            if module_permissions:
                session['permiso_producto'] = module_permissions.get('permiso_producto', 0)
                session['permiso_empleado'] = module_permissions.get('permiso_empleado', 0)
                session['permiso_inventario'] = module_permissions.get('permiso_inventario', 0)
                session['permiso_capacitacion'] = module_permissions.get('permiso_capacitacion', 0)
                session['permiso_cliente'] = module_permissions.get('permiso_cliente', 0)
                session['permiso_proveedor'] = module_permissions.get('permiso_proveedor', 0)
                session['permiso_sucursal'] = module_permissions.get('permiso_sucursal', 0)
                session['permiso_equipo'] = module_permissions.get('permiso_equipo', 0)
                session['permiso_pedido_cliente'] = module_permissions.get('permiso_pedido_cliente', 0)
                session['permiso_pedido_proveedor'] = module_permissions.get('permiso_pedido_proveedor', 0)
                session['permiso_devolucion_venta'] = module_permissions.get('permiso_devolucion_venta', 0)
                session['permiso_devolucion_compra'] = module_permissions.get('permiso_devolucion_compra', 0)
                session['permiso_promocion'] = module_permissions.get('permiso_promocion', 0)
                session['permiso_mantenimiento'] = module_permissions.get('permiso_mantenimiento', 0)
                session['permiso_transportista'] = module_permissions.get('permiso_transportista', 0)
                session['permiso_sar'] = module_permissions.get('permiso_sar', 0)
                session['permiso_usuario'] = module_permissions.get('permiso_usuario', 0)
                session['permiso_categoria'] = module_permissions.get('permiso_categoria', 0)
                session['permiso_distribucion'] = module_permissions.get('permiso_distribucion', 0)
                session['permiso_puesto_trabajo'] = module_permissions.get('permiso_puesto_trabajo', 0)
                session['permiso_impuesto'] = module_permissions.get('permiso_impuesto', 0)
                session['permiso_almacen'] = module_permissions.get('permiso_almacen', 0)
                
            flash('Usuario encontrado exitosamente.')
            return redirect(url_for('index_principal'))
    else:
        flash('Correo o contraseña incorrectos.')
        return redirect(url_for('index_login'))

    
@app_login.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Elimina toda la información de la sesión
    flash('Sesión cerrada exitosamente.')
    return redirect(url_for('index_login'))

@app_login.route('/index_principal')
def index_principal():
    if 'primer_nombre' not in session:  # Si no hay sesión, redirige al login
        flash('Debes iniciar sesión para acceder a esta página.')
        return redirect(url_for('index_login'))
    
    primer_nombre = session.get('primer_nombre')  
    primer_apellido = session.get('primer_apellido')
    correo = session.get('correo')
    id_sucursal = session.get('id_sucursal')
    return render_template('index.html', primer_nombre=primer_nombre, primer_apellido=primer_apellido, correo=correo, id_sucursal=id_sucursal)



@app_login.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app_login.route('/')
def index_login():
    return render_template('index_login.html')

@app_login.route('/registro')
def index_registro():
    return render_template('index_registro.html')

if __name__ == '__main__':
    app_login.run(debug=True, port=5030)
