import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from mysql.connector import Error
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app_proveedores import insert_user, get_proveedor, get_proveedor_by_id, update_user, delete_proveedor, search_users,validate_input

# Datos de prueba
TEST_PROVEEDOR = {
    'Nombre_del_proveedor': 'Proveedor Prueba',
    'Producto_Servicio': 'Servicios TI',
    'Historial_de_desempeño': 'A',
    'nombre_compañia': 'Compania Prueba',
    'Telefono': '9876-1234',
    'Ciudad': 'Ciudad Prueba',
    'tipo': 'DNI',
    'Documento': '0801198712345'
}

@pytest.fixture(scope="module")
def proveedor_test_data():
    """Fixture que devuelve los datos de un proveedor de prueba."""
    return TEST_PROVEEDOR

def test_insert_user(proveedor_test_data):
    """Prueba de inserción de un nuevo proveedor."""
    result = insert_user(
        proveedor_test_data['Nombre_del_proveedor'],
        proveedor_test_data['Producto_Servicio'],
        proveedor_test_data['Historial_de_desempeño'],
        proveedor_test_data['nombre_compañia'],
        proveedor_test_data['Telefono'],
        proveedor_test_data['Ciudad'],
        proveedor_test_data['tipo'],
        proveedor_test_data['Documento']
    )
    assert result == True, "Error al insertar proveedor"

def test_get_proveedor():
    """Prueba de obtención de proveedores con paginación."""
    page = 1
    per_page = 5
    proveedores, total_count = get_proveedor(page, per_page)
    assert len(proveedores) > 0, "No se obtuvieron proveedores"
    assert total_count >= 1, "El conteo total de proveedores debería ser al menos 1"

def test_get_proveedor_by_id():
    """Prueba de obtención de proveedor por ID."""
    id_proveedor = 1  # Asegúrate de que este ID exista en la base de datos
    proveedor = get_proveedor_by_id(id_proveedor)
    assert proveedor is not None, f"No se encontró el proveedor con ID {id_proveedor}"

def test_update_user(proveedor_test_data):
    """Prueba de actualización de un proveedor."""
    id_proveedor = 1  # Asegúrate de que este ID exista en la base de datos
    result = update_user(
        id_proveedor,
        proveedor_test_data['Nombre_del_proveedor'] + ' Actualizado',
        proveedor_test_data['Producto_Servicio'],
        proveedor_test_data['Historial_de_desempeño'],
        proveedor_test_data['nombre_compañia'],
        proveedor_test_data['Telefono'],
        proveedor_test_data['Ciudad'],
        proveedor_test_data['tipo'],
        proveedor_test_data['Documento']
    )
    assert result == True, "Error al actualizar el proveedor"

def test_delete_proveedor():
    """Prueba de eliminación de un proveedor."""
    id_proveedor = 2  # Asegúrate de que este ID exista en la base de datos para eliminarlo
    result = delete_proveedor(id_proveedor)
    assert result == True, "Error al eliminar el proveedor"

def test_search_users():
    """Prueba de búsqueda de proveedores."""
    search_criteria = 'Ciudad'
    search_query = 'Prueba'
    page = 1
    per_page = 5
    proveedores, total_count = search_users(search_criteria, search_query, page, per_page)
    assert len(proveedores) > 0, "No se encontraron proveedores con los criterios de búsqueda"
    assert total_count > 0, "El conteo total de proveedores debería ser mayor que 0"


import unittest

class TestValidations(unittest.TestCase):

    def test_nombre_del_proveedor(self):
        self.assertIsNone(validate_input("Proveedor S.A.", 'text', ''))  # Válido
        self.assertEqual(validate_input("", 'Nombre_del_proveedor', ''), 'El campo no puede estar vacío.')  # Vacío
        self.assertEqual(validate_input("A", 'Nombre_del_proveedor', ''), 'El nombre del proveedor debe tener entre 3 y 50 caracteres.')  # Demasiado corto
        self.assertEqual(validate_input("A" * 51, 'Nombre_del_proveedor', ''), 'El nombre del proveedor debe tener entre 3 y 50 caracteres.')  # Demasiado largo

    def test_producto_servicio(self):
        self.assertIsNone(validate_input("Servicio de Limpieza", 'Producto_Servicio', ''))  # Válido
        self.assertEqual(validate_input("", 'Producto_Servicio', ''), 'El campo no puede estar vacío.')  # Vacío
        self.assertEqual(validate_input("P", 'Producto_Servicio', ''), 'El campo Producto/Servicio debe tener entre 3 y 100 caracteres.')  # Demasiado corto
        self.assertEqual(validate_input("A" * 101, 'Producto_Servicio', ''), 'El campo Producto/Servicio debe tener entre 3 y 100 caracteres.')  # Demasiado largo

    def test_historial_de_desempeño(self):
        self.assertIsNone(validate_input("Historial excelente.", 'Historial_de_desempeño', ''))  # Válido
        self.assertEqual(validate_input("A" * 256, 'Historial_de_desempeño', ''), 'El historial de desempeño no puede exceder los 255 caracteres.')  # Demasiado largo

    def test_nombre_compañia(self):
        self.assertIsNone(validate_input("Compañía XYZ", 'nombre_compañia', ''))  # Válido
        self.assertEqual(validate_input("", 'nombre_compañia', ''), 'El campo no puede estar vacío.')  # Vacío
        self.assertEqual(validate_input("A", 'nombre_compañia', ''), 'El nombre de la compañía debe tener entre 3 y 100 caracteres.')  # Demasiado corto
        self.assertEqual(validate_input("A" * 101, 'nombre_compañia', ''), 'El nombre de la compañía debe tener entre 3 y 100 caracteres.')  # Demasiado largo

    def test_ciudad(self):
        self.assertIsNone(validate_input("Tegucigalpa", 'Ciudad', ''))  # Válido
        self.assertEqual(validate_input("", 'Ciudad', ''), 'El campo no puede estar vacío.')  # Vacío
        self.assertEqual(validate_input("A", 'Ciudad', ''), 'El nombre de la ciudad debe tener entre 3 y 50 caracteres.')  # Demasiado corto
        self.assertEqual(validate_input("A" * 51, 'Ciudad', ''), 'El nombre de la ciudad debe tener entre 3 y 50 caracteres.')  # Demasiado largo

    def test_telefono(self):
        self.assertIsNone(validate_input("93812345", 'telefono', ''))  # Válido
        self.assertEqual(validate_input("", 'telefono', ''), 'El campo no puede estar vacío.')  # Vacío
        self.assertEqual(validate_input("12345678", 'telefono', ''), 'El primer número del Teléfono debe ser 9, 3, 8 o 2.')  # Primer dígito incorrecto
        self.assertEqual(validate_input("93812", 'telefono', ''), 'El teléfono debe tener exactamente 8 dígitos.')  # Demasiado corto
        self.assertEqual(validate_input("938123456", 'telefono', ''), 'El teléfono debe tener exactamente 8 dígitos.')  # Demasiado largo
        self.assertEqual(validate_input("93812A45", 'telefono', ''), 'El teléfono debe tener exactamente 8 dígitos.')  # Contiene letras

    def test_tipo(self):
        self.assertIsNone(validate_input("Proveedor", 'tipo', ''))  # Válido
        self.assertEqual(validate_input("No válido", 'tipo', ''), 'El tipo debe ser uno de los siguientes: Proveedor, Servicio, Ambos.')  # Tipo no válido

    def test_documento(self):
        # RTN
        self.assertIsNone(validate_input("12345678901234", 'document', 'RTN'))  # Válido
        self.assertEqual(validate_input("1234567890123", 'document', 'RTN'), 'El RTN debe tener exactamente 14 dígitos.')  # Demasiado corto
        self.assertEqual(validate_input("123456789012345", 'document', 'RTN'), 'El RTN debe tener exactamente 14 dígitos.')  # Demasiado largo
        
        # DNI
        self.assertIsNone(validate_input("1234567890123", 'document', 'DNI'))  # Válido
        self.assertEqual(validate_input("123456789012", 'document', 'DNI'), 'El Número de Identidad debe tener exactamente 13 dígitos.')  # Demasiado corto
        self.assertEqual(validate_input("12345678901234", 'document', 'DNI'), 'El Número de Identidad debe tener exactamente 13 dígitos.')  # Demasiado largo
        
        # Pasaporte
        self.assertIsNone(validate_input("E1234567", 'document', 'Pasaporte'))  # Válido
        self.assertEqual(validate_input("1234567", 'document', 'Pasaporte'), 'El Pasaporte debe comenzar con una E mayúscula seguido de 7 números.')  # No comienza con E
        self.assertEqual(validate_input("E123456", 'document', 'Pasaporte'), 'El Pasaporte debe comenzar con una E mayúscula seguido de 7 números.')  # Demasiado corto

if __name__ == '__main__':
    unittest.main()
