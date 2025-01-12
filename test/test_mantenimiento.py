import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_mantenimiento import insert_mantenimiento, update_mantenimiento, delete_mantenimiento  # Importación ajustada

# Validar el formato del tipo de mantenimiento
def validar_tipo_mantenimiento(tipo):
    if not tipo:
        return False, "El tipo de mantenimiento no puede estar vacío."
    return True, ""

# Validar la fecha
def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, '%Y-%m-%d')  # Asegura que la fecha esté en formato YYYY-MM-DD
    except ValueError:
        return False, "Formato de fecha inválido. Usa 'YYYY-MM-DD'."
    return True, ""

# Modificar insert_mantenimiento para usar las validaciones
def insert_mantenimiento_validated(id_equipo, fecha, tipo, detalles, estado, documento):
    # Validar el tipo de mantenimiento
    valid, msg = validar_tipo_mantenimiento(tipo)
    if not valid:
        return False, msg
    # Validar la fecha
    valid, msg = validar_fecha(fecha)
    if not valid:
        return False, msg
    try:
        insert_mantenimiento(id_equipo, fecha, tipo, detalles, estado, documento)
        return True, ""
    except Exception as e:
        return False, str(e)

@pytest.fixture
def mock_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

# Prueba de inserción de mantenimiento exitosa
@patch('app_mantenimiento.create_connection')
def test_insert_mantenimiento_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result, msg = insert_mantenimiento_validated('1', '2024-10-01', 'Mantenimiento 1', 'Descripción de prueba', 'Activo', 'documento.pdf')
    assert result == True
    assert msg == ""

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO mantenimiento_equipo (id_equipo, fecha, tipo, detalles, estado, documento) VALUES (%s, %s, %s, %s, %s, %s)", 
        ('1', '2024-10-01', 'Mantenimiento 1', 'Descripción de prueba', 'Activo', 'documento.pdf')
    )
    mock_conn.commit.assert_called_once()

# Casos inválidos para validar el tipo de mantenimiento
def test_validar_tipo_mantenimiento_invalid_cases():
    assert validar_tipo_mantenimiento("") == (False, "El tipo de mantenimiento no puede estar vacío.")

# Casos válidos para validar el tipo de mantenimiento
def test_validar_tipo_mantenimiento_valid_cases():
    assert validar_tipo_mantenimiento("Mantenimiento 1") == (True, "")

# Prueba de actualización exitosa
@patch('app_mantenimiento.create_connection')
def test_update_mantenimiento_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    # Asegúrate de pasar todos los argumentos requeridos por la función
    result = update_mantenimiento(1, '1', '2024-10-02', 'Mantenimiento Actualizado', 'Detalles actualizados', 'Activo', 'documento_actualizado.pdf')
    assert result == True

    mock_cursor.execute.assert_called_once_with(
        "UPDATE mantenimiento_equipo SET id_equipo = %s, fecha = %s, tipo = %s, detalles = %s, estado = %s, documento = %s WHERE id_mantenimiento = %s",
        ('1', '2024-10-02', 'Mantenimiento Actualizado', 'Detalles actualizados', 'Activo', 'documento_actualizado.pdf', 1)
    )
    mock_conn.commit.assert_called_once()

# Prueba de eliminación exitosa
@patch('app_mantenimiento.create_connection')
def test_delete_mantenimiento_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = delete_mantenimiento(1)
    assert result == True

    mock_cursor.execute.assert_called_once_with("DELETE FROM mantenimiento_equipo WHERE id_mantenimiento = %s", (1,))
    mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    pytest.main()
