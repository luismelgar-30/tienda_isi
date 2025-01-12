import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_proveedores import insert_user, get_proveedor, get_proveedor_by_id, update_user, delete_proveedor

# Función para validar el campo de texto
def validate_text(text):
    if not (3 <= len(text) <= 50):
        return False, "Debe tener entre 3 y 50 caracteres"
    
    # Verifica que no tenga caracteres especiales
    if re.search(r'[^a-zA-Z\s]', text):
        return False, "No debe contener caracteres especiales"
    
    # Verifica que no tenga más de dos caracteres iguales consecutivos
    if re.search(r'(.)\1\1', text):
        return False, "No debe tener más de dos caracteres iguales consecutivos"
    
    # Verifica que no haya dos vocales iguales consecutivas
    if re.search(r'[aeiou]{2}', text, re.IGNORECASE):
        return False, "No debe tener dos vocales iguales consecutivas"
    
    # Verifica que no haya números si es un campo de texto
    if re.search(r'\d', text):
        return False, "No debe contener números en campos de texto"
    
    return True, ""

# Prueba de la función insert_user con validaciones
@patch('app_proveedores.create_connection')
def test_insert_user(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    nombre_proveedor = 'Juan Pérez'
    # Validar el nombre del proveedor antes de insertar
    valido, mensaje = validate_text(nombre_proveedor)
    assert valido, f"Error en validación del nombre: {mensaje}"

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = insert_user(nombre_proveedor, 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')

    # Verificar que la función retorne True al completar con éxito
    assert result == True

    # Verificar que el cursor ejecutó la consulta SQL correcta
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO proveedores (Nombre_del_proveedor, Producto_Servicio, Historial_de_desempeño, nombre_compañia, Telefono, Ciudad, tipo, Documento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (nombre_proveedor, 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')
    )

    # Verificar que se haya llamado a commit
    mock_conn.commit.assert_called_once()

# Prueba de la función get_proveedor
@patch('app_proveedores.create_connection')
def test_get_proveedor(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchall.return_value = [
        ('Juan Pérez', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')
    ]

    result = get_proveedor()

    assert result == [
        ('Juan Pérez', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')
    ]
    mock_cursor.execute.assert_called_once_with("SELECT * FROM proveedor_de_compra_proveedor")

# Prueba de la función get_proveedor_by_id
@patch('app_proveedores.create_connection')
def test_get_proveedor_by_id(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular la consulta exitosa
    mock_cursor.fetchone.return_value = ('Juan Pérez', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')

    result = get_proveedor_by_id(1)

    assert result == ('Juan Pérez', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')
    mock_cursor.execute.assert_called_once_with("SELECT * FROM proveedores WHERE id_proveedor = %s", (1,))

# Prueba de la función update_user
@patch('app_proveedores.create_connection')
def test_update_proveedor(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular una ejecución exitosa de la actualización
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = update_user('Juan Jose', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')

    # Verificar que la función retorne True al completar con éxito
    assert result == True
    mock_cursor.execute.assert_called_once_with(
    """
UPDATE proveedores
SET Nombre_del_proveedor = %s, Producto_Servicio = %s, Historial_de_desempeño = %s, nombre_compañia = %s, Telefono = %s, Ciudad = %s, tipo = %s, Documento = %s
WHERE id_proveedor = %s
""",
    ('Juan Jose', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678', 1)
)

    mock_conn.commit.assert_called_once()

# Prueba de la función delete_proveedor
@patch('app_proveedores.create_connection')
def test_delete_proveedor(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulación de la eliminación exitosa
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = delete_proveedor(1)

    assert result == True
    mock_cursor.execute.assert_called_once_with("DELETE FROM proveedores WHERE id_proveedor = %s", (1,))
    mock_conn.commit.assert_called_once()

# Prueba cuando ocurre un error en insert_user
@patch('app_proveedores.create_connection')
def test_insert_proveedor_error(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular que ocurre un error durante la ejecución
    mock_cursor.execute.side_effect = Exception('Database error')

    result = insert_user('Juan Pérez', 'Servicios de TI', 'Excelente', 'CompuTec S.A.', '12345678', 'Tegucigalpa', 'Empresa', '0801-1234-5678')

    # Verificar que la función retorne False cuando ocurre un error
    assert result == False
