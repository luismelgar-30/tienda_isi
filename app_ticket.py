from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import re
from mysql.connector import Error

app_ticket = Flask(__name__)
app_ticket.secret_key = 'your_secret_key'

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

def insert_ticket(nombre_cliente, correo, asunto, estado, fecha):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "INSERT INTO ticket (nombre_cliente, correo, asunto, estado, fecha) VALUES (%s, %s, %s, %s, %s)"
    values = (nombre_cliente, correo, asunto, estado, fecha)
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

def get_tickets(page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM ticket LIMIT %s OFFSET %s"
    try:
        cursor.execute(query, (per_page, offset))
        tickets = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_tickets = cursor.fetchone()[0]
        return tickets, total_tickets
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def get_ticket_by_id(id_ticket):
    connection = create_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    query = "SELECT * FROM ticket WHERE id_ticket = %s"
    try:
        cursor.execute(query, (id_ticket,))
        ticket = cursor.fetchone()
        return ticket
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return None
    finally:
        cursor.close()
        connection.close()

def update_ticket(id_ticket, nombre_cliente, correo, asunto, estado, fecha):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "UPDATE ticket SET nombre_cliente = %s, correo = %s, asunto = %s, estado = %s, fecha = %s WHERE id_ticket = %s"
    values = (nombre_cliente, correo, asunto, estado, fecha, id_ticket)
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

def delete_ticket(id_ticket):
    connection = create_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    query = "DELETE FROM ticket WHERE id_ticket = %s"
    try:
        cursor.execute(query, (id_ticket,))
        connection.commit()
        return True
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return False
    finally:
        cursor.close()
        connection.close()

def search_tickets_by_field(field, value, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page

    # Usar una coincidencia exacta para una búsqueda precisa
    query = f"""
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM ticket 
    WHERE {field} = %s
    LIMIT %s OFFSET %s
    """
    values = (value, per_page, offset)
    try:
        cursor.execute(query, values)
        tickets = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_tickets = cursor.fetchone()[0]
        return tickets, total_tickets
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def search_tickets(search_query, page, per_page):
    connection = create_connection()
    if connection is None:
        return [], 0
    cursor = connection.cursor()
    offset = (page - 1) * per_page
    
    # Usar una coincidencia parcial para buscar en todos los campos
    query = """
    SELECT SQL_CALC_FOUND_ROWS * 
    FROM ticket 
    WHERE nombre_cliente LIKE %s 
       OR correo LIKE %s 
       OR asunto LIKE %s 
       OR estado LIKE %s 
       OR fecha LIKE %s
    LIMIT %s OFFSET %s
    """
    values = (
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        f'%{search_query}%', 
        per_page, 
        offset
    )
    try:
        cursor.execute(query, values)
        tickets = cursor.fetchall()
        cursor.execute("SELECT FOUND_ROWS()")
        total_tickets = cursor.fetchone()[0]
        return tickets, total_tickets
    except Error as e:
        print(f"Error '{e}' ocurrió")
        return [], 0
    finally:
        cursor.close()
        connection.close()

def validar_campos(nombre_cliente, correo, asunto, estado):
    # Ningún campo permite números
    if any(char.isdigit() for char in nombre_cliente + asunto + estado):
        return False, 'Los campos no deben contener números.'

    # No permitir signos repetidos ni la misma letra repetida más de tres veces
    pattern = re.compile(r'(.)\1{2,}')
    if pattern.search(nombre_cliente + asunto + estado):
        return False, 'Los campos no deben contener signos repetidos ni la misma letra repetida más de tres veces.'

    # Mínimo 3 caracteres en cada campo
    if len(nombre_cliente) < 3 or len(asunto) < 8 or len(estado) < 8:
        return False, 'El nombre debe tener al menos 3 caracteres y el asunto y el estado deben tener al menos 8 caracteres.'

    # Máximo de 20 caracteres para el nombre y 100 para asunto y estado
    if len(nombre_cliente) > 20 or len(asunto) > 100 or len(estado) > 100:
        return False, 'El nombre debe tener un máximo de 20 caracteres y el asunto y el estado deben tener un máximo de 100 caracteres.'

    # El correo debe contener un @ y ser de 7 a 15 caracteres
    if len(correo) < 7 or len(correo) > 15 or '@' not in correo:
        return False, 'El correo debe contener un @ y tener entre 7 y 15 caracteres.'

    # El nombre no debe contener signos
    if re.search(r'[^\w\s]', nombre_cliente):
        return False, 'El nombre no debe contener signos.'

    return True, ''

@app_ticket.route('/')
def index_ticket():
    return render_template('index_ticket.html')

@app_ticket.route('/tickets')
def tickets():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    if search_query:
        if ':' in search_query:
            search_field, search_value = search_query.split(':', 1)
            if search_field in ["nombre_cliente", "correo", "asunto", "estado", "fecha"]:
                tickets, total_tickets = search_tickets_by_field(search_field, search_value, page, per_page)
            else:
                tickets, total_tickets = search_tickets(search_value, page, per_page)
        else:
            tickets, total_tickets = search_tickets(search_query, page, per_page)
    else:
        tickets, total_tickets = get_tickets(page, per_page)

    total_pages = (total_tickets + per_page - 1) // per_page
    return render_template('tickets.html', tickets=tickets, search_query=search_query, page=page, per_page=per_page, total_tickets=total_tickets, total_pages=total_pages)

@app_ticket.route('/submit', methods=['POST'])
def submit():
    nombre_cliente = request.form['nombre_cliente']
    correo = request.form['correo']
    asunto = request.form['asunto']
    estado = request.form['estado']
    fecha = request.form['fecha']

    if not nombre_cliente or not correo or not asunto or not estado or not fecha:
        flash('Todos los campos son requeridos!')
        return redirect(url_for('index_ticket'))

    is_valid, message = validar_campos(nombre_cliente, correo, asunto, estado)
    if not is_valid:
        flash(message)
        return redirect(url_for('index_ticket'))

    if insert_ticket(nombre_cliente, correo, asunto, estado, fecha):
        flash('Ticket insertado exitosamente!')
    else:
        flash('Ocurrió un error al insertar el ticket.')
    
    return redirect(url_for('index_ticket'))

@app_ticket.route('/edit_ticket/<int:id_ticket>', methods=['GET', 'POST'])
def edit_ticket(id_ticket):
    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente']
        correo = request.form['correo']
        asunto = request.form['asunto']
        estado = request.form['estado']
        fecha = request.form['fecha']

        if not nombre_cliente or not correo or not asunto or not estado or not fecha:
            flash('Todos los campos son requeridos!')
            return redirect(url_for('edit_ticket', id_ticket=id_ticket))

        is_valid, message = validar_campos(nombre_cliente, correo, asunto, estado)
        if not is_valid:
            flash(message)
            return redirect(url_for('edit_ticket', id_ticket=id_ticket))

        if update_ticket(id_ticket, nombre_cliente, correo, asunto, estado, fecha):
            flash('Ticket actualizado exitosamente!')
        else:
            flash('Ocurrió un error al actualizar el ticket.')
        
        return redirect(url_for('tickets'))

    ticket = get_ticket_by_id(id_ticket)
    if ticket is None:
        flash('Ticket no encontrado!')
        return redirect(url_for('tickets'))
    return render_template('edit_ticket.html', ticket=ticket)

@app_ticket.route('/eliminar_ticket/<int:id_ticket>', methods=['GET', 'POST'])
def eliminar_ticket(id_ticket):
    if request.method == 'POST':
        if delete_ticket(id_ticket):
            flash('Ticket eliminado exitosamente!')
        else:
            flash('Ocurrió un error al eliminar el ticket.')
        return redirect(url_for('tickets'))

    ticket = get_ticket_by_id(id_ticket)
    if ticket is None:
        flash('Ticket no encontrado!')
        return redirect(url_for('tickets'))
    return render_template('eliminar_ticket.html', ticket=ticket)

if __name__ == '__main__':
    app_ticket.run(debug=True, port=5008)
