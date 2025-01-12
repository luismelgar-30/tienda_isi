import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_inventario_almacenes import insert_inventario_almacen  # Importación ajustada

# Validar el formato del id_almacen
def validar_id_almacen(id_almacen):
    if not id_almacen:
        return False, "El id_almacen no puede estar vacío."
    # Aquí puedes añadir más validaciones según el formato esperado
    return True, ""

# Validar la cantidad en stock
def validar_cantidad_en_stock(cantidad):
    if cantidad < 0:
        return False, "La cantidad en stock no puede ser negativa."
    return True, ""

# Modificar insert_inventario_almacen para usar las validaciones
def insert_inventario_almacen_validated(id_almacen, id_producto, cantidad_en_stock, stock_minimo, stock_maximo):
    # Validar el id_almacen
    valid, msg = validar_id_almacen(id_almacen)
    if not valid:
        return False, msg
    # Validar la cantidad en stock
    valid, msg = validar_cantidad_en_stock(cantidad_en_stock)
    if not valid:
        return False, msg
    # Si pasa todas las validaciones, insertar el inventario
    return insert_inventario_almacen(id_almacen, id_producto, cantidad_en_stock, stock_minimo, stock_maximo), ""

# Prueba de la función insert_inventario_almacen usando un mock
@patch('app_inventario_almacenes.create_connection')
def test_insert_inventario_almacen(mock_create_connection):
    # Simular una conexión exitosa
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result, msg = insert_inventario_almacen_validated('1', 'Producto 1', 10, 5, 20)
    
    # Verificar que la función retorne True al completar con éxito
    assert result == True

    # Verificar que el cursor ejecutó la consulta SQL correcta
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO inventario_almacenes (id_almacenes, id_producto, cantidad_en_stock, stock_minimo, stock_maximo) VALUES (%s, %s, %s, %s, %s)", 
        ('1', 'Producto 1', 10, 5, 20)
    )

    # Verificar que se haya llamado a commit
    mock_conn.commit.assert_called_once()

# Prueba cuando el id_almacen está vacío
@patch('app_inventario_almacenes.create_connection')
def test_insert_inventario_almacen_id_vacio(mock_create_connection):
    result, msg = insert_inventario_almacen_validated('', 'Producto 1', 10, 5, 20)
    assert result == False
    assert msg == "El id_almacen no puede estar vacío."

# Prueba cuando la cantidad en stock es negativa
@patch('app_inventario_almacenes.create_connection')
def test_insert_inventario_almacen_cantidad_negativa(mock_create_connection):
    result, msg = insert_inventario_almacen_validated('1', 'Producto 1', -5, 5, 20)
    assert result == False
    assert msg == "La cantidad en stock no puede ser negativa."

# Prueba cuando ocurre un error durante la ejecución de la consulta
# @patch('app_inventario_almacenes.create_connection')
# def test_insert_inventario_almacen_error(mock_create_connection):
#     # Simular una conexión exitosa
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()

#     mock_create_connection.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Simular que ocurre un error durante la ejecución
#     mock_cursor.execute.side_effect = Exception('Database error')

#     result, msg = insert_inventario_almacen_validated('2', 'Producto 2', 15, 5, 20)

#     # Verificar que la función retorne False cuando ocurre un error
#     assert result == False
#     assert msg == ""
