from functools import wraps
from io import BytesIO
import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import pandas as pd

app_pedido = Flask(__name__)
app_pedido.secret_key = 'your_secret_key'

LOGS_DIR = 'logs/pedidos_de_compra_cliente'

# Asegúrate de que el directorio de logs exista
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action, screen_name="pedidos_de_compra_cliente", details=None):
    """Función para registrar acciones en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-{action}-{timestamp}.log')
    with open(log_file, 'a') as f:
        # Escribe el tipo de acción y los detalles si están presentes
        f.write(f"{timestamp} - {action}\n")
        if details:
            f.write(f"Detalles: {details}\n")

def log_error(error_message, screen_name="pedidos_de_compra_cliente"):
    """Función para registrar errores en un archivo de log."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_file = os.path.join(LOGS_DIR, f'{screen_name}-error-{timestamp}.log')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - ERROR: {error_message}\n")

def pedidos_de_compra_cliente_exists(id_pedido):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM pedidos_de_compra_cliente WHERE id_pedido = %s"
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

def insertar_pedido(numero_factura, id_cliente, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado, id_empleado, id_sucursal):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
        INSERT INTO pedido_de_compra_cliente (numero_factura, id_cliente, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado, id_empleado, id_sucursal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (numero_factura, id_cliente, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado, id_empleado, id_sucursal)
    
    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"Factura: {numero_factura}, ID Cliente: {id_cliente}, Fecha Pedido: {fecha_pedido}, Fecha Entrega Estimada: {fecha_entrega_estimada}, Fecha Entrega: {fecha_entrega}, ID Método: {id_metodo}, ID Estado: {id_estado}, ID Empleado: {id_empleado}, ID Sucursal: {id_sucursal}"
        log_action('Inserted', screen_name='pedido_de_compra_cliente', details=details)  # Registro de log
        print("Pedido insertado correctamente.")
        return True
    except mysql.connector.Error as err:
        error_message = f"Error al insertar en la base de datos: {err}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()

def update_pedido(id_pedido, id_cliente, numero_factura, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = """
    UPDATE pedido_de_compra_cliente
    SET id_cliente = %s, numero_factura = %s, fecha_pedido = %s, fecha_entrega_estimada = %s, fecha_entrega = %s, 
        id_metodo = %s, id_estado = %s
    WHERE id_pedido = %s
    """
    values = (id_cliente, numero_factura, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado, id_pedido)

    try:
        cursor.execute(query, values)
        connection.commit()
        details = f"ID Pedido: {id_pedido}, ID Cliente: {id_cliente}, Factura: {numero_factura}, Fecha Pedido: {fecha_pedido}, Fecha Entrega Estimada: {fecha_entrega_estimada}, Fecha Entrega: {fecha_entrega}, ID Método: {id_metodo}, ID Estado: {id_estado}"
        log_action('Updated', screen_name='pedido_de_compra_cliente', details=details)  # Registro de log
        print("Pedido actualizado correctamente.")
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
        print("Error: No se pudo conectar a la base de datos.")
        return False
    
    cursor = connection.cursor()
    query = "DELETE FROM pedido_de_compra_cliente WHERE id_pedido = %s"
    
    try:
        cursor.execute(query, (id_pedido,))
        connection.commit()
        details = f"ID Pedido: {id_pedido}"
        log_action('Deleted', screen_name='pedido_de_compra_cliente', details=details)  # Registro de log
        print("Pedido eliminado correctamente.")
        return True
    except Error as e:
        error_message = f"Error al borrar en la base de datos: {e}"
        print(error_message)
        log_error(error_message)  # Registrar el error
        return False
    finally:
        cursor.close()
        connection.close()


def get_pedidos2(page, per_page, search_criteria=None, search_query=None):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar el search_criteria
    valid_criteria = ['id_pedido', 'id_cliente', 'numero_factura', 'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega', 'id_metodo', 'id_estado']
    if search_criteria not in valid_criteria:
        search_criteria = None

    # Consulta SQL con depuración
    if search_criteria and search_query:
        query = f"""
            SELECT SQL_CALC_FOUND_ROWS p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,
                p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, 
                m.nombre AS metodo_pago, e.nombre_estado, p.id_empleado, p.id_sucursal
            FROM pedido_de_compra_cliente p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
            JOIN estado e ON p.id_estado = e.id_estado
            WHERE p.{search_criteria} LIKE %s
            ORDER BY p.id_pedido DESC
            LIMIT %s OFFSET %s
        """
        values = (f'%{search_query}%', per_page, offset)
    else:
        query = """
           SELECT SQL_CALC_FOUND_ROWS p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,
                p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, 
                m.nombre AS metodo_pago, e.nombre_estado, p.id_empleado, p.id_sucursal
            FROM pedido_de_compra_cliente p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
            JOIN estado e ON p.id_estado = e.id_estado
            WHERE p.{search_criteria} LIKE %s
            ORDER BY p.id_pedido DESC
            LIMIT %s OFFSET %s
        """
        values = (per_page, offset)

    try:
        print(f"Executing query: {query}")
        print(f"Values: {values}")
        cursor.execute(query, values)
        pedidos = cursor.fetchall()
        
        # Contar el total depedidos
        if search_criteria and search_query:
            count_query = f"""
            SELECT COUNT(*) 
            FROM pedido_de_compra_cliente p
            JOIN cliente c ON p.id_cliente = c.id_cliente
            JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
            JOIN estado e ON p.id_estado = e.id_estado
            WHERE p.{search_criteria} LIKE %s
            """
            cursor.execute(count_query, (f'%{search_query}%',))
        else:
            count_query = "SELECT COUNT(*) FROM pedido_de_compra_cliente"
            cursor.execute(count_query)
        
        total_count = cursor.fetchone()[0]
        return pedidos, total_count
    except Error as e:
        print(f"The error '{e}' occurred")
        return [], 0
    finally:
        cursor.close()
        connection.close()


def get_ultimo_numero_factura():
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT numero_factura 
    FROM factu
    ORDER BY id_factura DESC
    LIMIT 1
    """
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def get_nombre_empleado():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id_empleado, nombre FROM empleados"
    try:
        cursor.execute(query)
        empleado_nombre = cursor.fetchall()
        return empleado_nombre
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()

def get_empleado():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id_empleado, nombre FROM pedido_de_compra_cliente"
    try:
        cursor.execute(query)
        empleado = cursor.fetchall()
        return empleado
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return []
    finally:
        cursor.close()
        connection.close()
        
def get_cai_ultimo_usuario():
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()

    query_ultimo_usuario = """
    SELECT u.id_sucursal 
    FROM usuarios u
    JOIN sucursales s ON u.id_sucursal = s.id_sucursal
    ORDER BY u.id_usuario DESC 
    LIMIT 1
    """
    
    try:
        # Obtener la sucursal del último usuario creado
        cursor.execute(query_ultimo_usuario)
        result = cursor.fetchone()
        if not result:
            return None
        
        id_sucursal = result[0]
        
        # Obtener el CAI correspondiente a esa sucursal
        query_cai = """
        SELECT s.cai 
        FROM sar s 
        WHERE s.id_sucursal = %s 
        ORDER BY s.fecha_emision DESC 
        LIMIT 1
        """
        cursor.execute(query_cai, (id_sucursal,))
        cai_result = cursor.fetchone()
        
        return cai_result[0] if cai_result else None
    
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()
  
def get_ultimo_sucursal():
    connection = create_connection()
    if connection is None:
        return None
    query = """
    SELECT id_sucursal 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = (
        SELECT MAX(id_pedido) 
        FROM pedido_de_compra_cliente
    )
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            ultimo_sucursal = cursor.fetchone()
            return ultimo_sucursal[0] if ultimo_sucursal else None
    except mysql.connector.Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        connection.close()

     
def get_ultimo_usuario():
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = """
    SELECT id_sucursal 
    FROM pedido_de_compra_cliente 
    ORDER BY fecha_pedido DESC 
    LIMIT 1
    """
    try:
        cursor.execute(query)
        ultimo_usuario = cursor.fetchone()
        return ultimo_usuario[0] if ultimo_usuario else None
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()
        
        
def get_rtn_ultimo_usuario():
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()

    query_ultimo_usuario = """
    SELECT u.id_sucursal 
    FROM usuarios u 
    ORDER BY u.id_usuario DESC 
    LIMIT 1
    """
    
    try:
        # Obtener la sucursal del último usuario creado
        cursor.execute(query_ultimo_usuario)
        result = cursor.fetchone()
        if not result:
            return None
        
        id_sucursal = result[0]
        
        # Obtener el CAI correspondiente a esa sucursal
        query_rtn = """
        SELECT s.rtn 
        FROM sar s 
        WHERE s.id_sucursal = %s 
        ORDER BY s.fecha_emision DESC 
        LIMIT 1
        """
        cursor.execute(query_rtn, (id_sucursal,))
        rtn_result = cursor.fetchone()
        
        return rtn_result[0] if rtn_result else None
    
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()
        
def get_numero_factura_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    
    # Consulta SQL para obtener el número de factura basado en el id_pedido
    query_numero_factura = """
    SELECT numero_factura 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = %s
    """
    try:
        cursor.execute(query_numero_factura, (id_pedido,))
        result = cursor.fetchone()
        
        if result:
            numero_factura = result[0]
            print(f"Número de Factura recuperado: {numero_factura}")  # Mensaje de depuración
            return numero_factura
        else:
            print(f"No se encontró el número de factura para el pedido con ID: {id_pedido}.")
            return None

    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración


def get_nombre_apellido_cliente_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    
    # Primero, obtenemos el id_cliente desde pedido_de_compra_cliente
    query_id_cliente = """
    SELECT id_cliente 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = %s
    """
    try:
        cursor.execute(query_id_cliente, (id_pedido,))
        id_cliente = cursor.fetchone()
        
        if id_cliente:
            id_cliente = id_cliente[0]
            print(f"ID del cliente recuperado: {id_cliente}")  # Mensaje de depuración

            # Luego, obtenemos el nombre y apellido del cliente desde la tabla cliente
            query_cliente = """
            SELECT nombre, apellido 
            FROM cliente 
            WHERE id_cliente = %s
            """
            cursor.execute(query_cliente, (id_cliente,))
            cliente = cursor.fetchone()
            
            if cliente:
                nombre, apellido = cliente
                print(f"Nombre del cliente recuperado: {nombre}, Apellido: {apellido}")  # Mensaje de depuración
                return {'nombre': nombre, 'apellido': apellido}
            else:
                print("No se encontró el nombre y apellido del cliente para el ID proporcionado.")
                return None
        else:
            print("No se encontró el ID del cliente para el pedido proporcionado.")
            return None

    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración

def get_nombre_apellido_empleado_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    
    # Primero, obtenemos el id_empleado desde pedido_de_compra_cliente
    query_id_empleado = """
    SELECT id_empleado 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = %s
    """
    try:
        cursor.execute(query_id_empleado, (id_pedido,))
        id_empleado = cursor.fetchone()
        
        if id_empleado:
            id_empleado = id_empleado[0]
            print(f"ID del empleado recuperado: {id_empleado}")  # Mensaje de depuración

            # Luego, obtenemos el nombre y apellido del empleado desde la tabla empleado
            query_empleado = """
            SELECT nombre, apellido 
            FROM empleados 
            WHERE id_empleado = %s
            """
            cursor.execute(query_empleado, (id_empleado,))
            empleado = cursor.fetchone()
            
            if empleado:
                nombre, apellido = empleado
                print(f"Nombre del empleado recuperado: {nombre}, Apellido: {apellido}")  # Mensaje de depuración
                return {'nombre': nombre, 'apellido': apellido}
            else:
                print("No se encontró el nombre y apellido del empleado para el ID proporcionado.")
                return None
        else:
            print("No se encontró el ID del empleado para el pedido proporcionado.")
            return None

    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración

def get_nombre_apellido_empleado_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    
    # Primero, obtenemos el id_empleado desde pedido_de_compra_cliente
    query_id_empleado = """
    SELECT id_empleado 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = %s
    """
    try:
        cursor.execute(query_id_empleado, (id_pedido,))
        id_empleado = cursor.fetchone()
        
        if id_empleado:
            id_empleado = id_empleado[0]
            print(f"ID del empleado recuperado: {id_empleado}")  # Mensaje de depuración

            # Luego, obtenemos el nombre y apellido del empleado desde la tabla empleado
            query_empleado = """
            SELECT nombre, apellido 
            FROM empleados 
            WHERE id_empleado = %s
            """
            cursor.execute(query_empleado, (id_empleado,))
            empleado = cursor.fetchone()
            
            if empleado:
                nombre, apellido = empleado
                print(f"Nombre del empleado recuperado: {nombre}, Apellido: {apellido}")  # Mensaje de depuración
                return {'nombre': nombre, 'apellido': apellido}
            else:
                print("No se encontró el nombre y apellido del empleado para el ID proporcionado.")
                return None
        else:
            print("No se encontró el ID del empleado para el pedido proporcionado.")
            return None

    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración

def get_ciudad_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()

    # Obtener el id_sucursal desde pedido_de_compra_cliente
    query_id_sucursal = """
    SELECT id_sucursal 
    FROM pedido_de_compra_cliente 
    WHERE id_pedido = %s
    """
    try:
        cursor.execute(query_id_sucursal, (id_pedido,))
        id_sucursal = cursor.fetchone()
        
        if id_sucursal:
            id_sucursal = id_sucursal[0]
            print(f"ID de la sucursal recuperado: {id_sucursal}")

            # Obtener la ciudad desde la tabla sucursales
            query_sucursal = """
            SELECT ciudad 
            FROM sucursales 
            WHERE id_sucursal = %s
            """
            cursor.execute(query_sucursal, (id_sucursal,))
            sucursal = cursor.fetchone()
            
            if sucursal:
                ciudad = sucursal[0]
                print(f"Ciudad recuperada: {ciudad}")
                return ciudad
            else:
                print("No se encontró la ciudad para el ID de sucursal proporcionado.")
                return None
        else:
            print("No se encontró el ID de la sucursal para el pedido proporcionado.")
            return None

    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")


def get_sucursales():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_sucursal, Ciudad FROM sucursales"
    try:
        cursor.execute(query)
        sucursales = cursor.fetchall()
        return sucursales
    except Error as e:
        print(f"Error '{e}' ocurrió")
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

def get_numero_factura():
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return None

    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el id_sucursal del usuario logueado desde la sesión
        id_sucursal = session.get('id_sucursal')
        if not id_sucursal:
            print("Error: No hay un id_sucursal en la sesión.")
            return None

        # Obtener el id_sar de la tabla sar donde id_sucursal coincide
        query_sar = """
        SELECT id_sar
        FROM sar
        WHERE id_sucursal = %s
        """
        cursor.execute(query_sar, (id_sucursal,))
        sar_record = cursor.fetchone()

        if not sar_record:
            print("No se encontró un SAR válido para la sucursal del usuario.")
            return None
        
        id_sar = sar_record['id_sar']

        # Obtener el numero_factura de la tabla factu donde id_sar coincide
        query_factu = """
        SELECT numero_factura
        FROM factu
        WHERE id_sar = %s
        """
        cursor.execute(query_factu, (id_sar,))
        factu_record = cursor.fetchone()

        if not factu_record:
            print("No se encontró un número de factura para el SAR especificado.")
            return None
        
        numero_factura = factu_record['numero_factura']

        # Guardar el numero_factura en la sesión
        session['numero_factura'] = numero_factura

        print(f"Número de factura guardado en la sesión: {numero_factura}")
        return numero_factura

    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()


def validar_numero_factura():
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el id_sucursal del usuario logueado desde la sesión
        id_sucursal = session.get('id_sucursal')
        if not id_sucursal:
            print("Error: No hay un id_sucursal en la sesión.")
            return None

        # Obtener el id_sar y rango_final de la tabla sar
        query_sar = """
        SELECT id_sar, rango_final
        FROM sar
        WHERE id_sucursal = %s
        """
        cursor.execute(query_sar, (id_sucursal,))
        sar_record = cursor.fetchone()

        if not sar_record:
            print("No se encontró un SAR válido para la sucursal del usuario.")
            return None
        
        id_sar = sar_record['id_sar']
        v_rango_final = sar_record['rango_final']

        # Obtener el numero_factura de la tabla factu
        query_factu = """
        SELECT numero_factura
        FROM factu
        WHERE id_sar = %s
        """
        cursor.execute(query_factu, (id_sar,))
        factu_record = cursor.fetchone()

        if not factu_record:
            print("No se encontró un número de factura para el SAR especificado.")
            return None
        
        v_numero_factura = factu_record['numero_factura']

        # Extraer los últimos 8 dígitos de numero_factura y rango_final
        v_ultimos_digitos_factura = v_numero_factura[-8:]
        v_ultimos_digitos_final = v_rango_final[-8:]

        # Comparar los últimos 8 dígitos
        if v_ultimos_digitos_factura == v_ultimos_digitos_final:
            flash('No se podrá seguir creando pedidos, porque el número de factura llegó a su rango final.')

            # Actualizar el estado a 'Inactivo' en la tabla sar para el id_sar dado
            query_update_sar = """
            UPDATE sar
            SET estado = 'Inactivo'
            WHERE id_sar = %s
            """
            cursor.execute(query_update_sar, (id_sar,))
            connection.commit()
            
            print(f"Estado del SAR con id {id_sar} ha sido actualizado a 'Inactivo'.")
            return None
        
        # Si no hay coincidencia, permite la inserción
        return {
            'id_sar': id_sar,
            'numero_factura': v_numero_factura
        }
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

@app_pedido.template_global()
def get_ver_pedido_apagado(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return False
    
    cursor = connection.cursor(dictionary=True)
    try:
        # Obtener el id_sucursal del usuario logueado desde la sesión
        id_sucursal_usuario = session.get('id_sucursal')
        if not id_sucursal_usuario:
            print("Error: No hay un id_sucursal en la sesión.")
            return False

        # Obtener el id_sar y el estado de la tabla sar
        query_sar = """
        SELECT id_sar, estado, id_sucursal
        FROM sar
        WHERE id_sucursal = %s
        """
        cursor.execute(query_sar, (id_sucursal_usuario,))
        sar_record = cursor.fetchone()

        if not sar_record:
            print("No se encontró un SAR válido para la sucursal del usuario.")
            return False
        
        id_sar = sar_record['id_sar']
        estado_sar = sar_record['estado']
        id_sucursal_sar = sar_record['id_sucursal']

        # Imprimir los valores de id_sucursal para depuración
        print(f"id_sucursal_sar: {id_sucursal_sar}, id_sucursal_usuario: {id_sucursal_usuario}")

        # Validar que id_sucursal de sar coincida con el id_sucursal del usuario
        if str(id_sucursal_sar).strip() != str(id_sucursal_usuario).strip():
            print("El id_sucursal de SAR no coincide con el id_sucursal del usuario.")
            return False
        
        # Validar que el id_sar de sar coincida con el id_sar de factu
        query_factu = """
        SELECT id_factura
        FROM factu
        WHERE id_sar = %s
        """
        cursor.execute(query_factu, (id_sar,))
        factu_record = cursor.fetchone()

        if not factu_record:
            print("El id_sar de SAR no coincide con el id_sar de factu.")
            return False
        
        # Validar que el id_estado de pedido_de_compra_cliente sea diferente de 5
        query_pedido = """
        SELECT id_estado
        FROM pedido_de_compra_cliente
        WHERE id_pedido = %s
        """
        cursor.execute(query_pedido, (id_pedido,))
        pedido_record = cursor.fetchone()

        if not pedido_record:
            print("No se encontró el pedido.")
            return False
        
        if pedido_record['id_estado'] != 5:
            print("El id_estado del pedido es diferente de 5.")
            return False
        
        # Validar que el estado de SAR no sea "Inactivo"
        if estado_sar == 'Inactivo':
            print("El estado de SAR es Inactivo.")
            return False
        
        # Si todas las validaciones pasan, retornar True para habilitar el botón
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def is_pedido_editable(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return False
    
    cursor = connection.cursor(dictionary=True)
    try:
        query_pedido = """
        SELECT id_estado
        FROM pedido_de_compra_cliente
        WHERE id_pedido = %s
        """
        cursor.execute(query_pedido, (id_pedido,))
        pedido_record = cursor.fetchone()

        if not pedido_record:
            print("No se encontró el pedido.")
            return False
        
        # Retorna True solo si el estado NO es 5
        return pedido_record['id_estado'] != 5
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

@app_pedido.route('/pedidos')
def listar_pedidos():
    connection = create_connection()
    cursor = connection.cursor()
    query =  """SELECT id_pedido, numero_factura, id_cliente, fecha_pedido, 
       fecha_entrega_estimada, fecha_entrega, id_metodo, 
       id_estado, id_empleado, id_sucursal FROM pedido_de_compra_cliente
"""
    cursor.execute(query)
    pedidos = cursor.fetchall()
    search_query = request.args.get('search', '')
    search_criteria = request.args.get('search_criteria', 'id_pedido')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    pedidos, total_count = get_pedidos2(page, per_page, search_criteria, search_query)
    total_pages = (total_count + per_page - 1) // per_page
    
    if search_query:
        pedidos, total_pedidos = search_pedidos(search_query, page, per_page)
    else:
        pedidos, total_pedidos = get_pedidos(page, per_page)

    total_pages = (total_pedidos + per_page - 1) // per_page

    # Generar una lista de estados editables
    editable_pedidos = {pedido[0]: is_pedido_editable(pedido[0]) for pedido in pedidos}

    return render_template('pedidos.html', pedidos=pedidos, editable_pedidos=editable_pedidos,page=page,total_pages=total_pages)






def get_sar_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    query = """
    SELECT sar.cai, sar.rtn, sar.fecha_vencimiento, sar.rango_inicial, sar.rango_final
    FROM sar
    INNER JOIN pedido_de_compra_cliente ON sar.id_sucursal = pedido_de_compra_cliente.id_sucursal
    WHERE pedido_de_compra_cliente.id_pedido = %s
    """
    print(f"Ejecutando consulta con id_pedido: {id_pedido}")  # Mensaje de depuración

    try:
        cursor.execute(query, (id_pedido,))
        sar = cursor.fetchone()
        if sar:
            cai, rtn, fecha_vencimiento, rango_inicial, rango_final = sar
            print(f"Datos recuperados - CAI: {cai}, RTN: {rtn}, Fecha Vencimiento: {fecha_vencimiento}, Rango Inicial: {rango_inicial}, Rango Final: {rango_final}")  # Mensaje de depuración
            return {
                'cai': cai,
                'rtn': rtn,
                'fecha_vencimiento': fecha_vencimiento,
                'rango_inicial': rango_inicial,
                'rango_final': rango_final
            }
        else:
            print("No se encontraron datos para el id_pedido proporcionado.")  # Mensaje de depuración
            return None
    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración

def get_nombre_cliente_by_pedido(id_pedido):
    connection = create_connection()
    if connection is None:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return None

    cursor = connection.cursor()
    query = """
    SELECT cliente.nombre
    FROM pedido_de_compra_cliente
    INNER JOIN cliente ON pedido_de_compra_cliente.id_cliente = cliente.id_cliente
    WHERE pedido_de_compra_cliente.id_pedido = %s
    """
    print(f"Ejecutando consulta con id_pedido: {id_pedido}")  # Mensaje de depuración

    try:
        cursor.execute(query, (id_pedido,))
        nombre_cliente = cursor.fetchone()
        if nombre_cliente:
            print(f"Nombre del cliente recuperado: {nombre_cliente[0]}")  # Mensaje de depuración
            return nombre_cliente[0]  # Retorna el nombre del cliente
        else:
            print("No se encontró el nombre del cliente para el id_pedido proporcionado.")  # Mensaje de depuración
            return None
    except Error as e:
        print(f"Se produjo un error al ejecutar la consulta: {e}")  # Mensaje de depuración
        return None
    finally:
        cursor.close()
        connection.close()
        print("Conexión cerrada.")  # Mensaje de depuración


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

def get_nombre_cliente():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_cliente, nombre FROM cliente"
    try:
        cursor.execute(query)
        clientes = cursor.fetchall()
        return clientes  # No necesitas procesar los resultados en este punto
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


def get_garantia():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = """SELECT duracion FROM garantia"""
    try:
        cursor.execute(query)
        garantia = cursor.fetchall()
        duracion = [garantia[0] for garantia in garantia]
        return duracion
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def get_pedidos(page, per_page):
    connection = create_connection()
    offset = (page - 1) * per_page
    
    query = """
       SELECT p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,
    p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, 
    m.nombre AS metodo_pago, e.nombre_estado,
    CONCAT(emp.nombre, ' ', emp.apellido) AS nombre_empleado, 
    s.ciudad AS ciudad_sucursal
    FROM pedido_de_compra_cliente p
    JOIN cliente c ON p.id_cliente = c.id_cliente
    JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
    JOIN estado e ON p.id_estado = e.id_estado
    JOIN empleados emp ON p.id_empleado = emp.id_empleado  -- Unión para obtener el nombre del empleado
    JOIN sucursales s ON p.id_sucursal = s.id_sucursal  -- Unión para obtener la ciudad de la sucursal
    
    LIMIT %s OFFSET %s
    """
    print("Consulta SQL:", query)
    print("Parámetros:", per_page, offset)

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (per_page, offset))
            pedidos = cursor.fetchall()
            cursor.execute("SELECT FOUND_ROWS()")
            total_pedidos = cursor.fetchone()[0]
        return pedidos, total_pedidos
    except Exception as e:
        print(f"ERROR durante la consulta: {e}")
        return None, None
    finally:
        connection.close()
        print("DEBUG: Conexión a la base de datos cerrada.")


def get_pedido_by_id(id_pedido):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    query = """
    SELECT id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_completo, p.numero_factura, p.fecha_pedido, 
    p.fecha_entrega_estimada, p.fecha_entrega, m.nombre AS metodo_pago, e.nombre_estado, p.id_empleado, p.id_sucursal
    FROM pedido_de_compra_cliente p
    JOIN cliente c ON p.id_cliente = c.id_cliente
    JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
    JOIN estado e ON p.id_estado = e.id_estado
    WHERE p.id_pedido = %s

    """
    try:
        cursor.execute(query, (id_pedido,))
        pedido = cursor.fetchone()
        return pedido
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def get_detalles_by_pedido_id(id_pedido):
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = """
    SELECT d.id_detalle, d.id_pedido, p.nombre AS nombre_producto, d.cantidad, d.precio_unitario, d.total, d.subtotal 
    FROM detalle_de_compra_cliente d
    JOIN producto p ON d.id_producto = p.id_producto
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
            

@app_pedido.route('/')
@check_permission('permiso_pedido_cliente')
def index_pedido():
    connection = create_connection()
    numero_factura = get_numero_factura()
    empleados = get_id_empleado()
    if connection is None:
        return render_template('index_pedido.html', clientes=[], metodos=[], estados=[])
    cursor = connection.cursor()

    cursor.execute("SELECT id_cliente, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM cliente")
    clientes = cursor.fetchall()
    
    cursor.execute("SELECT id_metodo, nombre FROM metodo_de_pago")
    metodos = cursor.fetchall()
    
    cursor.execute("SELECT id_estado, nombre_estado FROM estado")
    estados = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return render_template('index_pedido.html', clientes=clientes, metodos=metodos, estados=estados, empleados=empleados, numero_factura=numero_factura)

@app_pedido.route('/pedidos')
@check_permission('permiso_pedido_cliente')

def pedidos():
    search_query = request.args.get('search', '')
    search_criteria = request.args.get('search_criteria', 'id_pedido')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    pedidos, total_count = get_pedidos2(page, per_page, search_criteria, search_query)
    total_pages = (total_count + per_page - 1) // per_page
    
    if search_query:
        pedidos, total_pedidos = search_pedidos(search_query, page, per_page)
    else:
        pedidos, total_pedidos = get_pedidos(page, per_page)

    total_pages = (total_pedidos + per_page - 1) // per_page
    empleados = get_id_empleado()

    # Pass the get_ver_pedido_apagado function to the template
    return render_template('pedidos.html', 
                           empleados=empleados, 
                           pedidos=pedidos, 
                           search_query=search_query, 
                           search_criteria=search_criteria,
                           page=page, 
                           per_page=per_page, 
                           total_pedidos=total_pedidos, 
                           total_pages=total_pages,
                           listar_pedidos=listar_pedidos,
                           is_pedido_editable=is_pedido_editable,
                           get_ver_pedido_apagado=get_ver_pedido_apagado)


@app_pedido.route('/submit', methods=['POST'])
@check_permission('permiso_pedido_cliente')
def submit():
    # Capturar valores del formulario
    id_cliente = request.form.get('id_cliente')
    numero_factura = request.form.get('numero_factura')
    fecha_pedido = request.form.get('fecha_pedido')
    fecha_entrega_estimada = request.form.get('fecha_entrega_estimada')
    fecha_entrega = request.form.get('fecha_entrega')
    id_metodo = request.form.get('id_metodo')
    id_estado = request.form.get('id_estado')
    id_empleado = session.get('id_empleado')
    id_sucursal = session.get('id_sucursal')

    # Verificar si todos los campos obligatorios están presentes
    if not all([id_cliente, fecha_pedido, id_metodo, id_estado]):
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_pedido'))

    # Validar número de factura antes de insertar el pedido
    if not validar_numero_factura():
        return redirect(url_for('index_pedido'))

    # Intentar insertar el pedido
    if insertar_pedido(numero_factura, id_cliente, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado, id_empleado, id_sucursal):
        flash('Pedido insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el pedido.')
    
    return redirect(url_for('index_pedido'))

@app_pedido.route('/edit_pedido/<int:id_pedido>', methods=['GET', 'POST'])
@check_permission('permiso_pedido_cliente')
def edit_pedido(id_pedido):
    
    id_sucursal = session['id_sucursal']  # Asume que el id_sucursal se guarda en la sesión

    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        numero_factura = request.form['numero_factura']
        fecha_pedido = request.form['fecha_pedido']
        fecha_entrega_estimada = request.form['fecha_entrega_estimada']
        fecha_entrega = request.form['fecha_entrega']
        id_metodo = request.form['id_metodo']
        id_estado = request.form['id_estado']
       

        if not id_cliente or not fecha_pedido or not fecha_entrega or not id_metodo or not id_estado:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_pedido', id_pedido=id_pedido))

        if update_pedido(id_pedido, id_cliente, numero_factura, fecha_pedido, fecha_entrega_estimada, fecha_entrega, id_metodo, id_estado):
            flash('Pedido actualizado exitosamente!')
        else:
            flash('Ocurrió un error al actualizar el pedido.')
        
        return redirect(url_for('pedidos'))

    pedido = get_pedido_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado!')
        return redirect(url_for('pedidos'))
    
# Asegúrate de que los datos de clientes, métodos y estados se cargan correctamente
    clientes = get_nombre_cliente()  # Obtener clientes
    metodos = get_metodos()         # Obtener métodos de pago
    estados = get_estados()         # Obtener estados

    return render_template('edit_pedido.html', pedido=pedido, clientes=clientes, estados=estados, metodos=metodos)

@app_pedido.route('/eliminar_pedido/<int:id_pedido>', methods=['GET', 'POST'])
@check_permission('permiso_pedido_cliente')
def eliminar_pedido(id_pedido):
    if request.method == 'POST':
        if delete_pedido(id_pedido):
            flash('Pedido eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el pedido.')
        return redirect(url_for('pedidos'))

    pedido = get_pedido_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado!')
        return redirect(url_for('pedidos'))
    return render_template('eliminar_pedido.html', pedido=pedido)

def search_pedidos(search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    
    query = """
    SELECT SQL_CALC_FOUND_ROWS p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente, p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, m.nombre AS metodo_pago, e.nombre_estado
    FROM pedido_de_compra_cliente p
    JOIN cliente c ON p.id_cliente = c.id_cliente
    JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
    JOIN estado e ON p.id_estado = e.id_estado
    ORDER BY p.id_pedido DESC
    WHERE c.nombre LIKE %s
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, ('%' + search_query + '%', per_page, offset))
        pedidos = cursor.fetchall()
        
        cursor.execute("SELECT FOUND_ROWS()")
        total_count = cursor.fetchone()[0]
    except Error as e:
        print(f"Error '{e}' ocurrió")
        pedidos, total_count = [], 0
    finally:
        cursor.close()
        connection.close()
    
    return pedidos, total_count


@app_pedido.route('/ver_pedido/<int:id_pedido>')
@check_permission('permiso_pedido_cliente')
def ver_pedido(id_pedido):
    # Realizar las validaciones antes de mostrar el pedido
    if not get_ver_pedido_apagado(id_pedido):
        flash('El pedido no se puede ver debido a las restricciones de validación.')
        return redirect(url_for('pedidos'))

    pedido = get_pedido_by_id(id_pedido)
    if pedido is None:
        flash('Pedido no encontrado!')
        return redirect(url_for('pedidos'))

    # Continuar con la lógica si las validaciones son correctas
    empleados_nombre = get_nombre_empleado()
    detalles = get_detalles_by_pedido_id(id_pedido)
    empleados = get_id_empleado()
    empleado = get_empleado()
    cliente_info = get_nombre_apellido_cliente_by_pedido(id_pedido)
    empleado_info = get_nombre_apellido_empleado_by_pedido(id_pedido)
    sucursal_info = get_ciudad_by_pedido(id_pedido) 
    numero_factura = get_numero_factura_by_pedido(id_pedido)
    sar = get_sar_by_pedido(id_pedido)
    sucursales = get_sucursales()
    garantia = get_garantia()
    cai = get_cai_ultimo_usuario()
    rtn = get_rtn_ultimo_usuario()
    ultimo_usuario = get_ultimo_usuario()
    ultimo_sucursal = get_ultimo_sucursal()
    
    return render_template('ver_pedidos.html', 
                           empleados_nombre=empleados_nombre,
                           pedido=pedido,
                           detalles=detalles,
                           cliente_info=cliente_info,
                           empleado_info=empleado_info,
                           sucursal_info=sucursal_info,
                           numero_factura=numero_factura,
                           empleados=empleados,
                           empleado=empleado,
                           sar=sar,
                           sucursales=sucursales,
                           garantia=garantia,
                           cai=cai,
                           rtn=rtn,
                           ultimo_usuario=ultimo_usuario,
                           ultimo_sucursal=ultimo_sucursal)

# Nueva función para obtener todas las pedido sin límites
def get_todas_pedido():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    # Seleccionar todos los registros de la tabla 'pedido'
    query = """
    SELECT p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,
    p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, 
    m.nombre AS metodo_pago, e.nombre_estado,
    CONCAT(emp.nombre, ' ', emp.apellido) AS nombre_empleado, 
    s.ciudad AS ciudad_sucursal
    FROM pedido_de_compra_cliente p
    JOIN cliente c ON p.id_cliente = c.id_cliente
    JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
    JOIN estado e ON p.id_estado = e.id_estado
    JOIN empleados emp ON p.id_empleado = emp.id_empleado  -- Unión para obtener el nombre del empleado
    JOIN sucursales s ON p.id_sucursal = s.id_sucursal  -- Unión para obtener la ciudad de la sucursal
    ORDER BY p.id_pedido ASC
    """

    try:
        cursor.execute(query)
        pedido = cursor.fetchall()  # Obtener todas las filas
        return pedido
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

@app_pedido.route('/descargar_excel')
@check_permission('permiso_pedido_cliente')
def descargar_excel():
    # Obtener todas las pedido sin paginación
    pedido = get_todas_pedido()  # Función para obtener todas las pedido

    if not pedido:
        flash('No hay pedido para descargar.')
        return redirect(url_for('pedidos'))  # Asegúrate de que la ruta 'pedido' está bien definida

    # Definir las columnas correctas
    columnas = ['id_pedido', 'nombre_cliente', 'numero_factura', 'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega', 'metodo_pago', 'nombre_estado', 'nombre_empleado', 'ciudad_sucursal']

    # Crear un DataFrame con los datos de las pedido
    df = pd.DataFrame(pedido, columns=columnas)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtener los datos del usuario desde la sesión
    usuario = f"{session.get('primer_nombre', 'Usuario desconocido')} {session.get('primer_apellido', '')}"

    # Crear un archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Escribir los datos de la tabla
        df.to_excel(writer, sheet_name='pedido', index=False, startrow=4)  # Los datos comenzarán en la fila 5 (índice 4)

        # Obtener el workbook y worksheet para escribir los metadatos
        workbook = writer.book
        worksheet = writer.sheets['pedido']

        # Agregar metadatos en las primeras filas
        worksheet.write('A1', 'Listado de pedido')
        worksheet.write('A2', f'Fecha y hora: {fecha_hora_actual}')
        worksheet.write('A3', f'Impreso por: {usuario}')

        # Ajustar el ancho de las columnas
        worksheet.set_column(0, len(columnas) - 1, 20)

    # Preparar el archivo para descargar
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='pedido.xlsx')

def get_todos_pedidos():
    connection = create_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    query = """
       SELECT p.id_pedido, CONCAT(c.nombre, ' ', c.apellido) AS nombre_cliente,
    p.numero_factura, p.fecha_pedido, p.fecha_entrega_estimada, p.fecha_entrega, 
    m.nombre AS metodo_pago, e.nombre_estado,
    CONCAT(emp.nombre, ' ', emp.apellido) AS nombre_empleado, 
    s.ciudad AS ciudad_sucursal
    FROM pedido_de_compra_cliente p
    JOIN cliente c ON p.id_cliente = c.id_cliente
    JOIN metodo_de_pago m ON p.id_metodo = m.id_metodo
    JOIN estado e ON p.id_estado = e.id_estado
    JOIN empleados emp ON p.id_empleado = emp.id_empleado  -- Unión para obtener el nombre del empleado
    JOIN sucursales s ON p.id_sucursal = s.id_sucursal  -- Unión para obtener la ciudad de la sucursal
    """
    try:
        cursor.execute(query)
        pedidos = cursor.fetchall()
        return pedidos
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

@app_pedido.route('/descargar_pdf')
@check_permission('permiso_pedido_cliente')
def descargar_pdf():
    # Obtener todos los pedidos y dividir en páginas de 10
    pedidos = get_todos_pedidos()
    paginacion = [pedidos[i:i + 10] for i in range(0, len(pedidos), 10)]

    # Configuración de PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A3))
    ancho, alto =landscape (A3)

    # Ruta del logo
    logo_path = "static/logo.png"
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_empleado = f"{session.get('primer_nombre', 'Empleado desconocido')} {session.get('primer_apellido', '')}"

    for pagina, pedidos_pagina in enumerate(paginacion, start=1):
        # Encabezado
        c.drawImage(logo_path, 40, alto - 80, width=100, height=40)  # Logo en la esquina
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(ancho / 2, alto - 50, "Pedidos de Compra de Cliente")
        c.setFont("Helvetica", 10)
        c.drawCentredString(ancho / 2, alto - 70, f"Fecha y Hora: {fecha_hora_actual}")
        c.drawCentredString(ancho / 2, alto - 90, f"Impreso por: {nombre_empleado}")

        # Espacio antes de la tabla
        y = alto - 130

        # Cuerpo - Tabla de Pedidos
        data = [["ID Pedido", "Cliente", "N° Factura", "Fecha Pedido", "Fecha Entrega Estimada",
                 "Fecha Entrega", "ID Método", "ID Estado", "ID Empleado", "ID Sucursal"]]  # Encabezado de la tabla
        data += [[pedido[0], pedido[1], pedido[2], pedido[3], pedido[4], 
                  pedido[5], pedido[6], pedido[7], pedido[8], pedido[9]] for pedido in pedidos_pagina]

        # Configuración de la tabla
        table = Table(data, colWidths=[1.7 * inch, 1.5 * inch, 1.7 * inch, 1.5 * inch, 1.5 * inch, 
                                       1.5 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch, 1.7 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
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
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name='Pedidos_Compra_Cliente.pdf')



if __name__ == "__main__":
    app_pedido.run(debug=True,port=5010)
