import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_distribucion import app_distribucion, insert_distribucion, update_distribucion, delete_distribucion, validate_text_field, validate_numeric_field, validate_date_field, get_distribuciones, search_distribuciones, get_distribucion_by_id

@pytest.fixture
def client():
    with app_distribucion.test_client() as client:
        yield client


def test_validate_numeric_field():
    # Casos válidos
    assert validate_numeric_field("123", "Cantidad") is None  # Válido
    assert validate_numeric_field("0", "Cantidad") is None  # Válido

    # Casos inválidos
    assert validate_numeric_field("abc", "Cantidad") == "El campo Cantidad solo puede contener números."
    assert validate_numeric_field("123abc", "Cantidad") == "El campo Cantidad solo puede contener números."


@patch('app_distribucion.create_connection')
def test_insert_distribucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure the cursor to simulate a successful behavior
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_distribucion(1, 2, 3, 100, "2024-12-31")
    assert result is True

@patch('app_distribucion.create_connection')
def test_insert_distribucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insertion
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        insert_distribucion(1, 2, 3, 100, "2024-12-31")

    assert str(exc_info.value) == "Error de base de datos"

@patch('app_distribucion.create_connection')
def test_update_distribucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure the cursor to simulate a successful update
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_distribucion(1, 1, 2, 3, 100, "2024-12-31")
    assert result is True

@patch('app_distribucion.create_connection')
def test_update_distribucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during update
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        update_distribucion(1, 1, 2, 3, 100, "2024-12-31")

    assert str(exc_info.value) == "Error de base de datos"

@patch('app_distribucion.create_connection')
def test_delete_distribucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful deletion
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_distribucion(1)
    assert result is True

@patch('app_distribucion.create_connection')
def test_get_distribuciones(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate the database response for fetching distribuciones
    mock_cursor.fetchall.return_value = [(1, "Almacen 1", "Almacen 2", "Producto 1", 100, "2024-12-31")]
    mock_cursor.fetchone.return_value = (1,)  # Simulate total count of 1 distribucion

    distribuciones, total_count = get_distribuciones(page=1, per_page=10)

    assert distribuciones == [(1, "Almacen 1", "Almacen 2", "Producto 1", 100, "2024-12-31")]
    assert total_count == 1

@patch('app_distribucion.create_connection')
def test_get_distribuciones_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate an empty response from the database
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0 distribuciones

    distribuciones, total_count = get_distribuciones(page=1, per_page=10)

    assert distribuciones == []
    assert total_count == 0

@patch('app_distribucion.create_connection')
def test_get_distribucion_by_id_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching a distribucion by ID
    mock_cursor.fetchone.return_value = (1, 1, 2, 3, 100, "2024-12-31")

    distribucion = get_distribucion_by_id(1)
    assert distribucion == (1, 1, 2, 3, 100, "2024-12-31")

@patch('app_distribucion.create_connection')
def test_get_distribucion_by_id_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate no distribucion found
    mock_cursor.fetchone.return_value = None

    distribucion = get_distribucion_by_id(999)
    assert distribucion is None

@patch('app_distribucion.create_connection')
def test_search_distribuciones_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate the database response for searching distribuciones
    mock_cursor.fetchall.return_value = [(1, "Almacen 1", "Almacen 2", "Producto 1", 100, "2024-12-31")]
    mock_cursor.fetchone.return_value = (1,)  # Simulate total count of 1 distribucion

    distribuciones, total_count = search_distribuciones("Almacen 1", page=1, per_page=10)

    assert distribuciones == [(1, "Almacen 1", "Almacen 2", "Producto 1", 100, "2024-12-31")]
    assert total_count == 1

@patch('app_distribucion.create_connection')
def test_search_distribuciones_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate an empty response for the search
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0 distribuciones

    distribuciones, total_count = search_distribuciones("Non-existent", page=1, per_page=10)

    assert distribuciones == []
    assert total_count == 0

if __name__ == '__main__':
    pytest.main()
