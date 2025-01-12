import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import unittest
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app_sucursales import insert_sucursal, update_sucursal, delete_sucursal, get_sucursales, get_sucursal_by_id, search_sucursales, format_telefono

# Mock para la conexión de base de datos
@pytest.fixture
def mock_connection():
    with patch('app_sucursales.create_connection') as mock_conn:
        mock_conn.return_value = MagicMock()
        yield mock_conn

# Prueba para insertar una sucursal nueva
def test_insert_sucursal(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchone.side_effect = [(0,), (0,)]  # No existen registros previos
    result, errors = insert_sucursal("Tegucigalpa", "9876-5432")
    assert result == "success"
    assert errors is None

def test_insert_sucursal_ciudad_duplicada(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchone.side_effect = [(1,), (0,)]  # Ciudad ya existe, teléfono no
    result, errors = insert_sucursal("Tegucigalpa", "9876-5432")
    assert result == "error"
    assert "ciudad_exists" in errors


# Prueba para insertar una sucursal con teléfono duplicado
def test_insert_sucursal_telefono_duplicado(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchone.side_effect = [(0,), (1,)]  # Teléfono ya existe
    result, errors = insert_sucursal("San Pedro Sula", "9876-5432")
    assert result == "error"
    assert "telefono_exists" in errors

# Prueba para actualizar una sucursal
def test_update_sucursal(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    result = update_sucursal(1, "San Pedro Sula", "9876-5432")
    assert result is True

# Prueba para eliminar una sucursal
def test_delete_sucursal(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    result = delete_sucursal(1)
    assert result is True

# Prueba para obtener una sucursal por su ID
def test_get_sucursal_by_id(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (1, "Tegucigalpa", "9876-5432")
    sucursal = get_sucursal_by_id(1)
    assert sucursal == (1, "Tegucigalpa", "9876-5432")

# Prueba para formatear el teléfono
def test_format_telefono():
    assert format_telefono("98765432") == "9876-5432"
    assert format_telefono("9876-5432") == "9876-5432"
    assert format_telefono("9876-54321") == "9876-54321"  # Formato incorrecto no se ajusta

# Prueba para obtener todas las sucursales
def test_get_sucursales(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [(1, "Tegucigalpa", "9876-5432"), (2, "San Pedro Sula", "8765-4321")]
    mock_cursor.fetchone.return_value = (2,)
    sucursales, total = get_sucursales(1, 5)
    assert len(sucursales) == 2
    assert total == 2

# Prueba para buscar sucursales por criterio
def test_search_sucursales(mock_connection):
    mock_cursor = mock_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [(1, "Tegucigalpa", "9876-5432")]
    mock_cursor.fetchone.return_value = (1,)
    sucursales, total = search_sucursales('ciudad', 'Tegucigalpa', 1, 5)
    assert len(sucursales) == 1
    assert total == 1

import unittest
from app_sucursales import insert_sucursal  # Asegúrate de tener la función que inserta sucursales

class TestSucursalInsert(unittest.TestCase):

    # Pruebas para el campo "ciudad"
    def test_ciudad_no_caracteres_especiales(self):
        result, errors = insert_sucursal('San Pedro@', '1234-5678')
        self.assertIn('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.', errors)

    def test_ciudad_no_tres_letras_repetidas_seguidas(self):
        result, errors = insert_sucursal('Bueeena', '1234-5678')
        self.assertIn('La ciudad no puede tener más de dos letras iguales consecutivas.', errors)


    def test_ciudad_no_vacio(self):
        result, errors = insert_sucursal('', '1234-5678')
        self.assertIn('¡Todos los campos obligatorios deben ser completados!', errors)


    def test_ciudad_minimo_tres_caracteres(self):
        result, errors = insert_sucursal('AB', '1234-5678')
        self.assertIn('La ciudad debe tener al menos 3 caracteres.', errors)

    def test_ciudad_no_acepta_numeros(self):
        result, errors = insert_sucursal('San Pedro 123', '1234-5678')
        self.assertIn('La ciudad contiene caracteres no permitidos. Solo se permiten letras y espacios.', errors)

    def test_telefono_no_acepta_letras(self):
        result, errors = insert_sucursal('San Pedro', '1234-ABCD')
        self.assertIn('El teléfono contiene caracteres no permitidos. Solo se permiten números y un guión en el formato xxxx-xxxx.', errors)


if __name__ == '__main__':
    unittest.main()

