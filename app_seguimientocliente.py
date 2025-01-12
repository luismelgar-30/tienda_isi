from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
from mysql.connector import Error

app_seguimiento = Flask(__name__)
app_seguimiento.secret_key = 'your_secret_key'

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

def insert_seguimiento(id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()

    query = """
    INSERT INTO seguimiento_de_envio (id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista)
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

def get_seguimientos(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0

    cursor = connection.cursor()
    offset = (page - 1) * per_page

    query = """
    SELECT s.id_seguimiento, p.id_pedido, s.fecha_envio, s.fecha_entrega_estimada, s.fecha_entrega_real, s.estado, t.nombre_empresa
    FROM seguimiento_de_envio s
    JOIN pedido_de_compra_cliente p ON s.id_pedido = p.id_pedido
    JOIN transportistas t ON s.id_transportista = t.id_transportista
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(query, (per_page, offset))
        seguimientos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM seguimiento_de_envio")
        total_count = cursor.fetchone()[0]

        return seguimientos, total_count
    except Exception as e:
        print(f"Error: {e}")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_seguimiento_by_id(id_seguimiento):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM seguimiento_de_envio WHERE id_seguimiento = %s"
    try:
        cursor.execute(query, (id_seguimiento,))
        seguimiento = cursor.fetchone()
        return seguimiento
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
    finally:
        cursor.close()
        connection.close()

def update_seguimiento(id_seguimiento, id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista):
    connection = create_connection()
    if connection is None:
        print("No se pudo conectar a la base de datos.")
        return False
    cursor = connection.cursor()
    query = """
    UPDATE seguimiento_de_envio
    SET id_pedido = %s, fecha_envio = %s, fecha_entrega_estimada = %s, fecha_entrega_real = %s, estado = %s, id_transportista = %s
    WHERE id_seguimiento = %s
    """
    values = (id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista, id_seguimiento)
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

def delete_seguimiento(id_seguimiento):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM seguimiento_de_envio WHERE id_seguimiento = %s"
    try:
        cursor.execute(query, (id_seguimiento,))
        connection.commit()
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()
        connection.close()

def get_pedidos():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_pedido FROM pedido_de_compra_cliente"
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

def get_transportistas():
    connection = create_connection()
    if connection is None:
        return []
    cursor = connection.cursor()
    query = "SELECT id_transportista, nombre_empresa FROM transportistas"
    try:
        cursor.execute(query)
        transportistas = cursor.fetchall()
        return transportistas
    except Error as e:
        print(f"The error '{e}' occurred")
        return []
    finally:
        cursor.close()
        connection.close()

def search_seguimientos(search_criteria, search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0

    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Validar criterios de búsqueda
    valid_criteria = ['s.id_seguimiento', 'p.id_pedido', 's.fecha_envio', 's.fecha_entrega_estimada', 's.fecha_entrega_real', 's.estado', 't.nombre_empresa']

    if search_criteria in valid_criteria:
        if search_criteria in ['s.fecha_envio', 's.fecha_entrega_estimada', 's.fecha_entrega_real']:
            search_query = search_query.replace('T', ' ') if search_query else None
            query = f"""
            SELECT s.id_seguimiento, p.id_pedido, s.fecha_envio, s.fecha_entrega_estimada, s.fecha_entrega_real, s.estado, t.nombre_empresa
            FROM seguimiento_de_envio s
            JOIN pedido_de_compra_cliente p ON s.id_pedido = p.id_pedido
            JOIN transportistas t ON s.id_transportista = t.id_transportista
            WHERE {search_criteria} LIKE %s
            LIMIT %s OFFSET %s
            """
        else:
            query = f"""
            SELECT s.id_seguimiento, p.id_pedido, s.fecha_envio, s.fecha_entrega_estimada, s.fecha_entrega_real, s.estado, t.nombre_empresa
            FROM seguimiento_de_envio s
            JOIN pedido_de_compra_cliente p ON s.id_pedido = p.id_pedido
            JOIN transportistas t ON s.id_transportista = t.id_transportista
            WHERE {search_criteria} LIKE %s
            LIMIT %s OFFSET %s
            """
        
        cursor.execute(query, (f"%{search_query}%", per_page, offset))
        seguimientos = cursor.fetchall()

        # Contar resultados
        count_query = f"""
        SELECT COUNT(*) FROM seguimiento_de_envio s
        JOIN pedido_de_compra_cliente p ON s.id_pedido = p.id_pedido
        JOIN transportistas t ON s.id_transportista = t.id_transportista
        WHERE {search_criteria} LIKE %s
        """
        cursor.execute(count_query, (f"%{search_query}%",))
        total_count = cursor.fetchone()[0]

    else:
        seguimientos = []
        total_count = 0

    connection.close()
    return seguimientos, total_count


@app_seguimiento.route('/')
def index_seguimiento():
    pedidos = get_pedidos()  # Obtiene la lista de pedidos
    transportistas = get_transportistas()  # Obtiene la lista de transportistas
    today = datetime.now().strftime('%Y-%m-%dT%H:%M')  # Formatea la fecha actual para el input datetime-local
    return render_template('index_seguimiento.html', pedidos=pedidos, transportistas=transportistas, today=today)

@app_seguimiento.route('/seguimientos', methods=['GET'])
def seguimientos():
    search_criteria = request.args.get('search_criteria', 's.id_seguimiento')
    search_query = request.args.get('search_query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    seguimientos, total_count = search_seguimientos(search_criteria, search_query, page, per_page)

    total_pages = (total_count + per_page - 1) // per_page

    return render_template('seguimientos.html', seguimientos=seguimientos, total_count=total_count, page=page, per_page=per_page, total_pages=total_pages, search_criteria=search_criteria, search_query=search_query)

@app_seguimiento.route('/submit', methods=['POST'])
def submit_seguimiento():
    id_pedido = request.form['id_pedido']
    fecha_envio = request.form['fecha_envio']
    fecha_entrega_estimada = request.form['fecha_entrega_estimada']
    fecha_entrega_real = request.form['fecha_entrega_real']
    estado = request.form['estado']
    id_transportista = request.form['id_transportista']

    # Validaciones
    errors = []
    try:
        # Convertir las fechas de entrada a objetos datetime
        fecha_entrega_estimada_dt = datetime.strptime(fecha_entrega_estimada, '%Y-%m-%d').date()
        if fecha_entrega_real:
            fecha_entrega_real_dt = datetime.strptime(fecha_entrega_real, '%Y-%m-%d').date()
        else:
            fecha_entrega_real_dt = None
    except ValueError:
        errors.append("Las fechas deben tener el formato correcto.")

    # Obtener la fecha actual
    now = datetime.now().date()
    if fecha_entrega_estimada_dt < now or (fecha_entrega_real_dt and fecha_entrega_real_dt < now):
        errors.append("Las fechas no pueden ser anteriores a la fecha actual.")

    if not errors and not insert_seguimiento(id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista):
        errors.append("Error al guardar el seguimiento en la base de datos.")
    
    if errors:
        for error in errors:
            flash(error)
        return redirect(url_for('index_seguimiento'))

    flash('Seguimiento guardado correctamente!')
    return redirect(url_for('index_seguimiento'))  



@app_seguimiento.route('/edit_seguimiento/<int:id_seguimiento>', methods=['GET', 'POST'])
def edit_seguimiento(id_seguimiento):
    if request.method == 'POST':
        id_pedido = request.form['id_pedido']
        fecha_envio = request.form['fecha_envio']
        fecha_entrega_estimada = request.form['fecha_entrega_estimada']
        fecha_entrega_real = request.form['fecha_entrega_real']
        estado = request.form['estado']
        id_transportista = request.form['id_transportista']

        # Validaciones
        errors = []
        try:
            if fecha_entrega_estimada:
                fecha_entrega_estimada_dt = datetime.strptime(fecha_entrega_estimada, '%Y-%m-%d').date()
            else:
                fecha_entrega_estimada_dt = None
            
            if fecha_entrega_real:
                fecha_entrega_real_dt = datetime.strptime(fecha_entrega_real, '%Y-%m-%d').date()
            else:
                fecha_entrega_real_dt = None
        except ValueError:
            errors.append("Las fechas deben tener el formato correcto (YYYY-MM-DD).")

        now = datetime.now().date()
        if fecha_entrega_estimada_dt and fecha_entrega_estimada_dt < now:
            errors.append("La fecha de entrega estimada no puede ser anterior a la fecha actual.")
        if fecha_entrega_real_dt and fecha_entrega_real_dt < now:
            errors.append("La fecha de entrega real no puede ser anterior a la fecha actual.")

        if not errors and not update_seguimiento(id_seguimiento, id_pedido, fecha_envio, fecha_entrega_estimada, fecha_entrega_real, estado, id_transportista):
            errors.append("Error al actualizar el seguimiento en la base de datos.")
        
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('edit_seguimiento', id_seguimiento=id_seguimiento))

        flash('Seguimiento actualizado correctamente!')
        return redirect(url_for('seguimientos'))

    seguimiento = get_seguimiento_by_id(id_seguimiento)
    if seguimiento is None:
        flash('Seguimiento no encontrado.')
        return redirect(url_for('seguimientos'))

    pedidos = get_pedidos()
    transportistas = get_transportistas()
    return render_template('edit_seguimiento.html', seguimiento=seguimiento, pedidos=pedidos, transportistas=transportistas)


@app_seguimiento.route('/eliminar/<int:id_seguimiento>', methods=['GET', 'POST'])
def eliminar_seguimiento(id_seguimiento):
    if request.method == 'POST':
        if delete_seguimiento(id_seguimiento):  # Asegúrate de que esta función se llame correctamente
            flash('Seguimiento eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el seguimiento.')
        return redirect(url_for('seguimientos'))

    seguimiento = get_seguimiento_by_id(id_seguimiento)
    if seguimiento is None:
        flash('Seguimiento no encontrado!')
        return redirect(url_for('seguimientos'))
    
    return render_template('eliminar_seguimiento.html', seguimiento=seguimiento)


if __name__ == '__main__':
    app_seguimiento.run(debug=True,port=5028)
