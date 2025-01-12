import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_cliente import insert_user, get_cliente, get_cliente_by_id, update_user, delete_user, search_users

# Validar nombre con las reglas solicitadas
def validar_nombre(nombre):
    if not nombre:
        return False, "El nombre no puede estar vacío."
    if len(nombre) < 3:
        return False, "El nombre debe tener al menos 3 caracteres."
    if len(nombre) > 50:
        return False, "El nombre no puede tener más de 50 caracteres."
    if not re.match("^[A-Za-zÀ-ÿ '-]+$", nombre):
        return False, "El nombre contiene caracteres inválidos."
    if re.search(r'(.)\1\1', nombre):
        return False, "El nombre no puede tener más de dos caracteres idénticos consecutivos."
    if re.search(r'([aeiouAEIOU])\1', nombre):
        return False, "El nombre no puede tener dos vocales iguales consecutivas."
    return True, ""

# Validar email con formato correcto
def validar_email(email):
    if not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$", email):
        return False, "El email no tiene un formato válido."
    return True, ""

# Modificar insert_user para usar las validaciones
def insert_user_validated(nombre, apellido, email, telefono):
    # Validar nombre
    valid, msg = validar_nombre(nombre)
    if not valid:
        return False, msg
    # Validar email
    valid, msg = validar_email(email)
    if not valid:
        return False, msg
    
    # Agregar valores predeterminados para los otros parámetros
    fecha_nacimiento = None  # O algún valor adecuado
    direccion = None         # O algún valor adecuado
    fecha_registro = None    # O algún valor adecuado
    tipo = None              # O algún valor adecuado
    documento = None         # O algún valor adecuado

    return insert_user(nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento), ""

# Prueba de la función insert_user usando un mock
# @patch('app_cliente.create_connection')
# def test_insert_user(mock_create_connection):
#     # Simular una conexión exitosa
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()

#     mock_create_connection.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Simular una ejecución exitosa de la consulta
#     mock_cursor.execute.return_value = None
#     mock_conn.commit.return_value = None

#     result, msg = insert_user_validated('Juan', 'Perez', 'juan.perez@example.com', '12345678')

#     # Verificar que la función retorne True al completar con éxito
#     assert result == True

#     # Verificar que el cursor ejecutó la consulta SQL correcta
#     mock_cursor.execute.assert_called_once_with(
#         "INSERT INTO cliente (nombre, apellido, fecha_nacimiento, email, telefono, direccion, fecha_registro, tipo, documento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
#         ('Juan', 'Perez', None, 'juan.perez@example.com', '12345678', None, None, None, None)
#     )

#     # Verificar que se haya llamado a commit
#     mock_conn.commit.assert_called_once()

# Prueba de validación de nombre vacío
@patch('app_cliente.create_connection')
def test_insert_user_nombre_vacio(mock_create_connection):
    result, msg = insert_user_validated('', 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre no puede estar vacío."

# Prueba de validación de nombre con caracteres especiales
@patch('app_cliente.create_connection')
def test_insert_user_nombre_caracteres_especiales(mock_create_connection):
    result, msg = insert_user_validated('Ju@n!', 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre contiene caracteres inválidos."

# Prueba de validación de nombre con longitud máxima de 50 caracteres
@patch('app_cliente.create_connection')
def test_insert_user_nombre_max_caracteres(mock_create_connection):
    nombre_largo = 'a' * 51
    result, msg = insert_user_validated(nombre_largo, 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre no puede tener más de 50 caracteres."

# Prueba de validación de nombre con longitud mínima de 3 caracteres
@patch('app_cliente.create_connection')
def test_insert_user_nombre_min_caracteres(mock_create_connection):
    result, msg = insert_user_validated('Ju', 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre debe tener al menos 3 caracteres."

# Prueba de validación de más de dos caracteres consecutivos iguales
@patch('app_cliente.create_connection')
def test_insert_user_nombre_caracteres_consecutivos(mock_create_connection):
    result, msg = insert_user_validated('Juaaan', 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre no puede tener más de dos caracteres idénticos consecutivos."

# Prueba de validación de dos vocales iguales consecutivas
@patch('app_cliente.create_connection')
def test_insert_user_nombre_vocales_consecutivas(mock_create_connection):
    result, msg = insert_user_validated('Juaan', 'Perez', 'juan.perez@example.com', '12345678')
    assert result == False
    assert msg == "El nombre no puede tener dos vocales iguales consecutivas."

# Prueba de validación de email con formato incorrecto
@patch('app_cliente.create_connection')
def test_insert_user_email_invalido(mock_create_connection):
    result, msg = insert_user_validated('Juan', 'Perez', 'juan.perez.com', '12345678')
    assert result == False
    assert msg == "El email no tiene un formato válido."

# Prueba de la función get_cliente
@patch('app_cliente.create_connection')
def test_get_cliente(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchall.return_value = [
        (1, 'Juan', 'Perez', 'juan.perez@example.com', '12345678')  # Ajusta según tus datos de prueba
    ]

    result = get_cliente()

    assert result == [
        (1, 'Juan', 'Perez', 'juan.perez@example.com', '12345678')
    ]
    mock_cursor.execute.assert_called_once_with("SELECT * FROM cliente")

# Prueba de la función get_cliente_by_id
@patch('app_cliente.create_connection')
def test_get_cliente_by_id(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchone.return_value = (1, 'Juan', 'Perez', 'juan.perez@example.com', '12345678')

    result = get_cliente_by_id(1)

    assert result == (1, 'Juan', 'Perez', 'juan.perez@example.com', '12345678')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM cliente WHERE id_cliente = %s", (1,))

# Prueba de la función update_user
# @patch('app_cliente.create_connection')
# def test_update_user(mock_create_connection):
#     # Simular una conexión exitosa
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()

#     mock_create_connection.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Simular una ejecución exitosa de la actualización
#     mock_cursor.execute.return_value = None
#     mock_conn.commit.return_value = None

#     # Agregar valores predeterminados para los otros parámetros
#     fecha_nacimiento = None  # O algún valor adecuado
#     direccion = None         # O algún valor adecuado
#     fecha_registro = None    # O algún valor adecuado
#     tipo = None              # O algún valor adecuado
#     documento = None         # O algún valor adecuado

#     result = update_user(1, 'Juan', 'Gomez', fecha_nacimiento, 'juan.gomez@example.com', '87654321', direccion, fecha_registro, tipo, documento)

#     # Verificar que la función retorne True al completar con éxito
#     assert result == True
#     mock_cursor.execute.assert_called_once_with
