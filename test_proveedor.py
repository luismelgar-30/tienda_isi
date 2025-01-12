import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app_proveedores import insert_user, get_proveedor, get_proveedor_by_id, update_user, delete_proveedor, validate_input

# Mock para la conexión MySQL
@pytest.fixture
def mock_db_connection(mocker):
    mock_connection = mocker.patch('app_proveedores.create_connection')
    mock_cursor = mocker.MagicMock()
    mock_connection.return_value.cursor.return_value = mock_cursor
    return mock_connection, mock_cursor

# Prueba para insertar un proveedor
def test_insert_user_success(mock_db_connection):
    connection, cursor = mock_db_connection

    result = insert_user(
        Nombre_del_proveedor="Proveedor Test",
        Producto_Servicio="Servicio Test",
        Historial_de_desempeño="Bueno",
        nombre_compañia="Compañía Test",
        Telefono="22334455",
        Ciudad="Ciudad Test",
        tipo="DNI",
        Documento="0801199901234"
    )
    
    assert result is True
    cursor.execute.assert_called_once()

# Prueba de fallo al insertar por validación de documento
def test_insert_user_invalid_document(mock_db_connection):
    result = insert_user(
        Nombre_del_proveedor="Proveedor Test",
        Producto_Servicio="Servicio Test",
        Historial_de_desempeño="Bueno",
        nombre_compañia="Compañía Test",
        Telefono="22334455",
        Ciudad="Ciudad Test",
        tipo="DNI",
        Documento="080199990123"
    )

    assert result is False  # Documento inválido (13 en lugar de 14 dígitos)

# Prueba para obtener proveedores con paginación
def test_get_proveedor(mock_db_connection):
    connection, cursor = mock_db_connection

    # Simula retorno de proveedores y total_count
    cursor.fetchall.return_value = [('Proveedor Test', 'Servicio Test')]
    cursor.fetchone.return_value = [1]  # Total proveedores

    proveedores, total_count = get_proveedor(1, 10)

    assert len(proveedores) == 1
    assert total_count == 1

# Prueba para obtener un proveedor por ID
def test_get_proveedor_by_id(mock_db_connection):
    connection, cursor = mock_db_connection

    # Simula retorno de proveedor
    cursor.fetchone.return_value = ('Proveedor Test', 'Servicio Test')

    proveedor = get_proveedor_by_id(1)

    assert proveedor is not None
    assert proveedor[0] == 'Proveedor Test'

# Prueba para actualizar proveedor
def test_update_user(mock_db_connection):
    connection, cursor = mock_db_connection

    result = update_user(
        id_proveedor=1,
        Nombre_del_proveedor="Proveedor Test",
        Producto_Servicio="Servicio Actualizado",
        Historial_de_desempeño="Muy bueno",
        nombre_compañia="Compañía Test",
        Telefono="22334455",
        Ciudad="Ciudad Test",
        tipo="DNI",
        Documento="0801199901234"
    )

    assert result is True
    cursor.execute.assert_called_once()

# Prueba para eliminar un proveedor
def test_delete_proveedor(mock_db_connection):
    connection, cursor = mock_db_connection

    result = delete_proveedor(1)
    
    assert result is True
    cursor.execute.assert_called_once_with("DELETE FROM proveedores WHERE id_proveedor = %s", (1,))

# Prueba de validación de nombre (no debe contener números ni caracteres especiales)
@pytest.mark.parametrize("field_value, expected", [
    ("Proveedor123", "El campo no debe contener números."),
    ("Proveedor$$$", "El campo no debe contener solo signos."),
    ("Pro", None),  # Debe ser válido
    ("", "El campo no puede estar vacío."),
    ("Pr", "El campo debe tener entre 3 y 20 caracteres."),
])
def test_validate_input(field_value, expected):
    result = validate_input(field_value, 'text')
    assert result == expected

# Prueba de validación de teléfono (exactamente 8 dígitos)
@pytest.mark.parametrize("telefono, expected", [
    ("22334455", None),  # Válido
    ("11223344", "El primer número del Teléfono debe ser 9, 3, 8 o 2."),
    ("2233445", "El campo Teléfono debe ser numérico y tener exactamente 8 dígitos."),
    ("223344556", "El campo Teléfono debe ser numérico y tener exactamente 8 dígitos."),
])
def test_validate_input_telefono(telefono, expected):
    result = validate_input(telefono, 'telefono')
    assert result == expected

# Prueba de validación de documento (DNI con 13 dígitos)
@pytest.mark.parametrize("documento, tipo, expected", [
    ("0801199901234", "DNI", None),  # DNI válido
    ("080119990123", "DNI", "El Número de Identidad debe tener exactamente 13 dígitos."),
    ("E1234567", "Pasaporte", None),  # Pasaporte válido
    ("E123456", "Pasaporte", "El Pasaporte debe comenzar con una E mayúscula seguido de 7 números."),
])
def test_validate_document(documento, tipo, expected):
    result = validate_input(documento, 'document', tipo)
    assert result == expected
