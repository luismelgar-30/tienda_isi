import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Importar la librería para validaciones de expresiones regulares

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_sucursales import insert_sucursal, get_sucursal_by_id, update_sucursal, delete_sucursal, get_sucursales  # Ajusta las importaciones según tu estructura

# Función para validar "Ciudad"
def validar_ciudad(ciudad):
    # No debe tener caracteres especiales
    if re.search(r'[^a-zA-Z\s]', ciudad):
        return False
    # No más de dos caracteres iguales consecutivos
    if re.search(r'(.)\1{2,}', ciudad):
        return False
    # No dos vocales iguales consecutivas
    if re.search(r'[aeiou]{2}', ciudad, re.IGNORECASE):
        return False
    # No números
    if re.search(r'\d', ciudad):
        return False
    return True

# Función para validar "Teléfono"
def validar_telefono(telefono):
    # No debe aceptar letras
    if re.search(r'[a-zA-Z]', telefono):
        return False
    return True

# Prueba de la función insert_sucursal
@patch('app_sucursales.create_connection')
def test_insert_sucursal(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    ciudad_valida = 'Tegucigalpa'
    telefono_valido = '1234-5678'

    # Validar "Ciudad"
    assert validar_ciudad(ciudad_valida) == True
    # Validar "Teléfono"
    assert validar_telefono(telefono_valido) == True

    result, errors = insert_sucursal(ciudad_valida, telefono_valido)

    # Verificar que la función retorne "success"
    assert result == "success"
    # Verificar que el cursor ejecutó la consulta SQL correcta
    mock_cursor.execute.assert_called_with(
        "INSERT INTO sucursales (ciudad, telefono) VALUES (%s, %s)",
        (ciudad_valida, telefono_valido)
    )
    mock_conn.commit.assert_called_once()

# Prueba de la función get_sucursal_by_id
@patch('app_sucursales.create_connection')
def test_get_sucursal_by_id(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchone.return_value = (1, 'Tegucigalpa', '1234-5678')

    result = get_sucursal_by_id(1)

    assert result == (1, 'Tegucigalpa', '1234-5678')
    mock_cursor.execute.assert_called_once_with("SELECT id_sucursal, ciudad, telefono FROM sucursales WHERE id_sucursal = %s", (1,))

# Prueba de la función update_sucursal
@patch('app_sucursales.create_connection')
def test_update_sucursal(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular una ejecución exitosa de la actualización
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    ciudad_valida = 'San Pedro Sula'
    telefono_valido = '8765-4321'

    # Validar "Ciudad"
    assert validar_ciudad(ciudad_valida) == True
    # Validar "Teléfono"
    assert validar_telefono(telefono_valido) == True

    result = update_sucursal(1, ciudad_valida, telefono_valido)

    # Verificar que la función retorne True al completar con éxito
    assert result == True
    mock_cursor.execute.assert_called_once_with(
        "UPDATE sucursales SET ciudad = %s, telefono = %s WHERE id_sucursal = %s",
        (ciudad_valida, telefono_valido, 1)
    )
    mock_conn.commit.assert_called_once()

# Prueba de la función delete_sucursal
@patch('app_sucursales.create_connection')
def test_delete_sucursal(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulación de la eliminación exitosa
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = delete_sucursal(1)

    assert result == True
    mock_cursor.execute.assert_called_once_with("DELETE FROM sucursales WHERE id_sucursal = %s", (1,))
    mock_conn.commit.assert_called_once()

# Prueba cuando ocurre un error en insert_sucursal
@patch('app_sucursales.create_connection')
def test_insert_sucursal_error(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular que ocurre un error durante la ejecución
    mock_cursor.execute.side_effect = Exception('Database error')

    result, errors = insert_sucursal('Tegucigalpa', '12345678')

    # Verificar que la función retorne "error" y que existan errores
    assert result == "error"
    assert 'database_error' in errors

# Pruebas de validación incorrecta en el campo "Ciudad"
def test_validar_ciudad():
    assert validar_ciudad('Te$$ucigalpa') == False  # Caracteres especiales
    assert validar_ciudad('Teguuucigalpa') == False  # Más de dos caracteres iguales consecutivos
    assert validar_ciudad('Tegucigaalpa') == False  # Dos vocales iguales consecutivas
    assert validar_ciudad('Teguciga1pa') == False  # Contiene números

# Pruebas de validación incorrecta en el campo "Teléfono"
def test_validar_telefono():
    assert validar_telefono('123a5678') == False  # Contiene letras
    assert validar_telefono('1234-5678') == True  # Valor válido
