import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_transportistas import insert_transportista, get_transportista, get_transportista_by_id, update_transportista, eliminar_transportista  # Ajusta las importaciones según tu estructura

# Función auxiliar para validar nombre_empresa
def validar_nombre_empresa(nombre_empresa):
    # No caracteres especiales
    if not re.match(r'^[A-Za-z\s]+$', nombre_empresa):
        return False, "El nombre de la empresa no puede contener caracteres especiales ni números."
    
    # No más de dos caracteres iguales consecutivos
    if re.search(r'(.)\1{2,}', nombre_empresa):
        return False, "El nombre de la empresa no puede tener más de dos caracteres iguales consecutivos."
    
    # No dos vocales iguales consecutivas
    if re.search(r'[aeiouAEIOU]{2}', nombre_empresa):
        return False, "El nombre de la empresa no puede tener dos vocales iguales consecutivas."
    
    return True, ""

# Función auxiliar para validar teléfono
def validar_telefono(telefono):
    if re.search(r'[a-zA-Z]', telefono):
        return False, "El número de teléfono no puede contener letras."
    return True, ""

# Prueba de la función insert_transportista usando un mock
@patch('app_transportistas.create_connection')
def test_insert_transportista(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Validaciones
    nombre_empresa = 'CompuTec S.A.'
    telefono = '12345678'

    valido_nombre, error_nombre = validar_nombre_empresa(nombre_empresa)
    assert valido_nombre, error_nombre

    valido_telefono, error_telefono = validar_telefono(telefono)
    assert valido_telefono, error_telefono

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = insert_transportista(nombre_empresa, telefono)

    # Verificar que la función retorne True al completar con éxito
    assert result == True

    # Verificar que el cursor ejecutó la consulta SQL correcta
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO transportistas (nombre_empresa, Telefono) VALUES (%s, %s)",
        (nombre_empresa, '1234-5678')
    )

    # Verificar que se haya llamado a commit
    mock_conn.commit.assert_called_once()

# Prueba de la función get_transportista
@patch('app_transportistas.create_connection')
def test_get_transportista(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchall.return_value = [
        ('CompuTec S.A.', '12345678')  # Ajusta según tus datos de prueba
    ]

    result, total_count = get_transportista(1, 10)

    assert result == [
        ('CompuTec S.A.', '12345678')
    ]
    assert total_count == 1
    mock_cursor.execute.assert_called_once_with("SELECT * FROM transportistas LIMIT %s OFFSET %s", (10, 0))

# Prueba de la función get_transportista_by_id
@patch('app_transportistas.create_connection')
def test_get_transportista_by_id(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchone.return_value = ('CompuTec S.A.', '12345678')

    result = get_transportista_by_id(1)

    assert result == ('CompuTec S.A.', '12345678')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM transportistas WHERE id_transportista = %s", (1,))

# Prueba de la función update_transportista
@patch('app_transportistas.create_connection')
def test_update_transportista(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Validaciones
    nombre_empresa = 'CompuTec S.A.'
    telefono = '12345678'

    valido_nombre, error_nombre = validar_nombre_empresa(nombre_empresa)
    assert valido_nombre, error_nombre

    valido_telefono, error_telefono = validar_telefono(telefono)
    assert valido_telefono, error_telefono

    # Simular una ejecución exitosa de la actualización
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = update_transportista(1, nombre_empresa, telefono)

    # Verificar que la función retorne True al completar con éxito
    assert result == True
    mock_cursor.execute.assert_called_once_with(
        """
        UPDATE transportistas
        SET nombre_empresa = %s, Telefono = %s
        WHERE id_transportista = %s
        """,
        (nombre_empresa, '12345678', 1)
    )

    mock_conn.commit.assert_called_once()

# Prueba de la función eliminar_transportista
@patch('app_transportistas.create_connection')
def test_eliminar_transportista(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulación de la eliminación exitosa
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = eliminar_transportista(1)

    assert result == True
    mock_cursor.execute.assert_called_once_with("DELETE FROM transportistas WHERE id_transportista = %s", (1,))
    mock_conn.commit.assert_called_once()

# Prueba cuando ocurre un error en insert_transportista
@patch('app_transportistas.create_connection')
def test_insert_transportista_error(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular que ocurre un error durante la ejecución
    mock_cursor.execute.side_effect = Exception('Database error')

    result = insert_transportista('CompuTec S.A.', '12345678')

    # Verificar que la función retorne False cuando ocurre un error
    assert result == False
