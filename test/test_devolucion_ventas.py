import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_devolucion_ventas import app_devoluciones, insert_devolucion, get_devoluciones, update_devolucion, delete_devolucion, get_devolucion_by_id

@pytest.fixture
def client():
    with app_devoluciones.test_client() as client:
        yield client

@patch('app_devolucion_ventas.create_connection')
def test_insert_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un comportamiento exitoso de inserción
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_devolucion(1, 1, '2024-10-01', 'Motivo', 2)
    assert result is True

@patch('app_devolucion_ventas.create_connection')
def test_insert_devolucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un error en la base de datos durante la inserción
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        insert_devolucion(1, 1, '2024-10-01', 'Motivo', 2)

    assert str(exc_info.value) == "Error de base de datos"

@patch('app_devolucion_ventas.create_connection')
def test_get_devoluciones(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular la respuesta de la base de datos para la recuperación de devoluciones
    mock_cursor.fetchall.return_value = [(1, 1, 1, 'Producto 1', '2024-10-01', 'Motivo', 2)]
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (1,)  # Simular un total de 1 devolución

    devoluciones, total_count = get_devoluciones(page=1, per_page=10)

    assert devoluciones == [(1, 1, 1, 'Producto 1', '2024-10-01', 'Motivo', 2)]
    assert total_count == 1

@patch('app_devolucion_ventas.create_connection')
def test_update_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un comportamiento exitoso de actualización
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_devolucion(1, 1, 1, '2024-10-01', 'Motivo Actualizado', 3)
    assert result is True

@patch('app_devolucion_ventas.create_connection')
def test_update_devolucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un error en la base de datos durante la actualización
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        update_devolucion(1, 1, 1, '2024-10-01', 'Motivo Actualizado', 3)

    assert str(exc_info.value) == "Error de base de datos"

@patch('app_devolucion_ventas.create_connection')
def test_delete_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un comportamiento exitoso de eliminación
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_devolucion(1)
    assert result is True
# Se espera que la función devuelva False en caso de error

@patch('app_devolucion_ventas.create_connection')
def test_get_devolucion_by_id(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular la respuesta de la base de datos para la recuperación de una devolución específica
    mock_cursor.fetchone.return_value = (1, 1, 1, '2024-10-01', 'Motivo', 2)

    devolucion = get_devolucion_by_id(1)
    assert devolucion == (1, 1, 1, '2024-10-01', 'Motivo', 2)

@patch('app_devolucion_ventas.create_connection')
def test_get_devolucion_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular que no se encuentra la devolución
    mock_cursor.fetchone.return_value = None

    devolucion = get_devolucion_by_id(999)  # ID no existente
    assert devolucion is None

if __name__ == '__main__':
    pytest.main()
