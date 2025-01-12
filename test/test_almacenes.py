import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_almacenes import app_almacenes, insert_almacen, update_almacen, delete_almacen, validate_text_field, get_sucursales

@pytest.fixture
def client():
    with app_almacenes.test_client() as client:
        yield client

def test_validate_text_field():
    # Valid cases
    assert validate_text_field("Almacen") == (True, "")  # Valid

    # Invalid cases
    assert validate_text_field("A") == (False, "El campo debe tener entre 3 y 20 caracteres.")
    assert validate_text_field("Almacen123") == (False, "El campo no puede contener números.")
    assert validate_text_field("Almacén@") == (False, "El campo no puede contener caracteres especiales.")
    assert validate_text_field("Almaaa") == (False, "El campo no puede contener tres letras seguidas iguales.")

@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_insert_almacen_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure cursor to simulate successful behavior
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_almacen("Almacen1", "Direccion 1", 1)
    assert result is True

@patch('app_almacenes.create_connection')  # Adjust the path according to your project structure
def test_insert_almacen_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insert
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Assert that the exception is raised
    with pytest.raises(Exception) as exc_info:
        insert_almacen("Almacen1", "Direccion 1", 1)
    
    assert str(exc_info.value) == "Error de base de datos"


@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_update_almacen_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure the cursor to simulate successful update behavior
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_almacen(1, "Almacen Actualizado", "Direccion Actualizada", 1)
    assert result is True

@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_update_almacen_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during update
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Assert that the function returns False on error
    result = update_almacen(1, "Almacen Actualizado", "Direccion Actualizada", 1)
    assert result is False  # Expecting a failure return value

@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_delete_almacen_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during delete
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Assert that the function returns False on error
    result = delete_almacen(1)
    assert result is False  # Expecting a failure return value

@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_delete_almacen_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during delete
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    result = delete_almacen(1)
    assert result is False  # Expect the function to return False instead of raising an exception

@patch('app_almacenes.create_connection')  # Ensure this path is correct
def test_get_sucursales(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate database response
    mock_cursor.fetchall.return_value = [(1, "Sucursal 1"), (2, "Sucursal 2")]

    sucursales = get_sucursales()
    assert sucursales == [(1, "Sucursal 1"), (2, "Sucursal 2")]

@patch('app_almacenes.create_connection') 
def test_get_sucursales_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    sucursales = get_sucursales()
    assert sucursales == []


if __name__ == '__main__':
    pytest.main()
