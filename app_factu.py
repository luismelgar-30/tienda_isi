import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app_factu = Flask(__name__)
app_factu.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/factu'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="factu", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="factu"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def factu_exists(id_factura):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM factu WHERE id_factura = %s"
    cursor.execute(query, (id_factura,))
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


def insert_factu(id_sar, numero_factura):
    connection = create_connection()
    if connection is None:
        raise Exception("Error de conexión a la base de datos")  # Lanzar una excepción en lugar de retornar False

    cursor = connection.cursor()
    query = "INSERT INTO factu (id_sar, numero_factura) VALUES (%s, %s)"
    values = (id_sar, numero_factura)

    try:
        cursor.execute(query, values)
        connection.commit()

        # Log de inserción
        log_query = "INSERT INTO logs (accion, descripcion, fecha) VALUES (%s, %s, NOW())"
        cursor.execute(log_query, ('INSERT', f'Factura creada: ID SAR {id_sar}, Número de Factura {numero_factura}'))
        connection.commit()  # Asegúrate de que el log también se guarde

        return True
    except Exception as e:  # Captura cualquier excepción
        error_message = f"Error al insertar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        raise  # Lanzar la excepción nuevamente para que la prueba pueda capturarla
    finally:
        cursor.close()
        connection.close()


def update_factu(id, nuevo_valor):
    connection = create_connection()
    if connection is None:
        raise Exception("Error de conexión a la base de datos")

    cursor = connection.cursor()
    query = "UPDATE factu SET valor = %s WHERE id = %s"
    values = (nuevo_valor, id)

    try:
        cursor.execute(query, values)
        connection.commit()

        # Log de actualización
        log_query = "INSERT INTO logs (accion, descripcion, fecha) VALUES (%s, %s, NOW())"
        cursor.execute(log_query, ('UPDATE', f'Factura actualizada: ID {id}, Nuevo Valor {nuevo_valor}'))
        connection.commit()  # Asegúrate de que el log también se guarde

        return True
    except Exception as e:
        error_message = f"Error al actualizar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        raise
    finally:
        cursor.close()
        connection.close()


def delete_factu(id_factura):
    connection = create_connection()
    if connection is None:
        raise Exception("Error de conexión a la base de datos")

    cursor = connection.cursor()
    query = "DELETE FROM factu WHERE id_factura = %s"
    
    try:
        cursor.execute(query, (id_factura,))
        connection.commit()

        # Log de eliminación
        log_query = "INSERT INTO logs (accion, descripcion, fecha) VALUES (%s, %s, NOW())"
        cursor.execute(log_query, ('DELETE', f'Factura eliminada: ID {id_factura}'))
        connection.commit()  # Asegúrate de que el log también se guarde

        return True
    except Exception as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        raise
    finally:
        cursor.close()
        connection.close()

def get_factu(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS id_factura, id_sar, numero_factura FROM factu LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        factu = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_factu = cursor.fetchone()[0]
        return factu, total_factu
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_factu(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = f"SELECT SQL_CALC_FOUND_ROWS * FROM factu WHERE {search_criteria} LIKE %s LIMIT %s OFFSET %s"
    values = (f'%{search_query}%', per_page, offset)
    try:
        cursor.execute(query, values)
        factu = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
        return factu, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_factu_by_id(id_factura):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT id_factura, id_sar, numero_factura FROM factu WHERE id_factura = %s"
    cursor.execute(query, (id_factura,))
    factu = cursor.fetchone()
    cursor.close()
    connection.close()
    return factu

def get_sar():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_sar FROM sar"
    try:
        cursor.execute(query)
        sar = cursor.fetchall()
        return [s[0] for s in sar]
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_next_numero_factura(id_sar):
    connection = create_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor()
    
    # Obtener el último número de factura generado para el id_sar específico
    query = "SELECT numero_factura FROM factu WHERE id_sar = %s ORDER BY numero_factura DESC LIMIT 1"
    cursor.execute(query, (id_sar,))
    last_factura = cursor.fetchone()

    # Obtener datos de la tabla SAR para el id_sar seleccionado
    query_sar = "SELECT secuencial, rango_inicial, rango_final FROM sar WHERE id_sar = %s"
    cursor.execute(query_sar, (id_sar,))
    sar_data = cursor.fetchone()

    if not sar_data:
        return None

    secuencial, rango_inicial, rango_final = sar_data
    
    # Formatear las primeras partes del número de factura
    parte1 = secuencial
    parte2 = rango_inicial[-3:]  # Últimos tres dígitos de rango_inicial
    parte3 = rango_final[:2]  # Primeros dos dígitos de rango_final
    
    # Determinar los últimos 8 dígitos
    if last_factura:
        # Incrementar el último número
        ultimo_xxxxxxxxx = int(last_factura[0].split('-')[-1]) + 1
    else:
        # Usar el segundo dígito en adelante del rango_inicial
        ultimo_xxxxxxxxx = int(rango_inicial[1:9])  # Segundo dígito hasta el noveno
    
    parte4 = f"{ultimo_xxxxxxxxx:08d}"  # Asegurar que siempre tenga 8 dígitos

    # Concatenar todas las partes para formar el número de factura
    numero_factura = f"{parte1}-{parte2}-{parte3}-{parte4}"
    
    cursor.close()
    connection.close()
    
    return numero_factura
        
        
def get_sar_details(id_sar):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT secuencial, rango_inicial, rango_final 
    FROM sar 
    WHERE id_sar = %s
    """
    cursor.execute(query, (id_sar,))
    sar_details = cursor.fetchone()
    cursor.close()
    connection.close()
    return sar_details


        
@app_factu.route('/crear_factura_pdf/<int:id_sar>', methods=['POST'])
def crear_factura_pdf(id_sar):
    # Obtener el siguiente número de factura
    numero_factura = get_next_numero_factura(id_sar)
    
    if numero_factura is None:
        flash('Error al generar el número de factura.')
        return redirect(url_for('index_factu'))
    
    # Insertar el nuevo registro en la base de datos
    if insert_factu(id_sar, numero_factura):
        flash(f'Factura con número {numero_factura} creada exitosamente.')
    else:
        flash('Error al crear la factura.')
    
    return redirect(url_for('ver_pedido', id_sar=id_sar))  # Ajusta la redirección según tu necesidad


def get_pedido_by_id(id_pedido):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT id_pedido, id_sar FROM pedido_de_compra_cliente WHERE id_pedido = %s"
    cursor.execute(query, (id_pedido,))
    pedido = cursor.fetchone()
    cursor.close()
    connection.close()
    return pedido


        
        
@app_factu.route('/get_factura_format/<int:id_sar>')
def get_factura_format(id_sar):
    sar_details = get_sar_details(id_sar)
    if not sar_details:
        return '', 400
    
    secuencial, rango_inicial, rango_final = sar_details
    
    # Asegúrate de que rango_inicial tenga al menos 8 dígitos
    last_8_digits = rango_inicial[-8:].rjust(8, '0')
    
    formato = f"{secuencial}-{rango_inicial[-3:]}-{rango_final[:2]}-{last_8_digits}"
    return formato



@app_factu.route('/')
def index_factu():
    sar_list = get_sar()  # Obtener la lista de IDs de SAR
    return render_template('index_factu.html', sar_list=sar_list)


@app_factu.route('/factu')
def factu():
    search_criteria = request.args.get('search_criteria')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    if search_query:
        factu, total_count = search_factu(search_criteria, search_query, page, per_page)
    else:
        factu, total_count = get_factu(page, per_page)
    
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('factu.html', factu=factu, search_criteria=search_criteria, search_query=search_query, page=page, total_pages=total_pages, per_page=per_page)

@app_factu.route('/submit', methods=['POST'])
def submit():
    id_sar = request.form['id_sar']
    numero_factura = request.form['numero_factura']
    
    if insert_factu(id_sar, numero_factura):
        flash('Factura ingresada exitosamente.')
    else:
        flash('Ocurrió un error al ingresar la factura.')
    
    return redirect(url_for('factu'))

@app_factu.route('/edit_factu/<int:id_factura>', methods=['GET', 'POST'])
def edit_factu(id_factura):
    if request.method == 'POST':
        id_sar = request.form['id_sar']
        numero_factura = request.form['numero_factura']

        if update_factu(id_factura, id_sar, numero_factura):
            flash('Factura actualizada exitosamente.')
        else:
            flash('Ocurrió un error al actualizar la factura.')
        
        return redirect(url_for('factu'))

    factu = get_factu_by_id(id_factura)
    if factu is None:
        flash('Factura no encontrada.')
        return redirect(url_for('factu'))
    return render_template('edit_factu.html', factu=factu, sar_list=get_sar())

@app_factu.route('/eliminar_factu/<int:id_factura>', methods=['GET', 'POST'])
def eliminar_factu(id_factura):
    if request.method == 'POST':
        if delete_factu(id_factura):
            flash('Factura eliminada exitosamente!')
            return redirect(url_for('factu'))
        else:
            flash('Ocurrió un error al eliminar la factura. Por favor, intente nuevamente.')
            return redirect(url_for('factu'))

    factu = get_factu_by_id(id_factura)
    if factu is None:
        flash('Factura no encontrada.')
        return redirect(url_for('factu'))

    return render_template('eliminar_factu.html', factu=factu)

if __name__ == '__main__':
    app_factu.run(debug=True, port=5033)
