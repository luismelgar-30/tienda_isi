import pytest
from unittest.mock import patch, MagicMock
from app_devolucion_compra import (
    insert_devolucion,
    get_devoluciones,
    get_pedidos,
    get_detalles_by_pedido,
    update_devolucion,
    delete_devolucion,
    get_devolucion_by_id,
    get_producto_by_id,
)

@patch('app_devolucion_compra.create_connection')
def test_insert_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful insertion
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_devolucion(1, 1, '2024-10-01', 'Defective product', 2)

    assert result is True  # Expecting the function to return True on success


@patch('app_devolucion_compra.create_connection')
def test_insert_devolucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insertion
    mock_cursor.execute.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        insert_devolucion(1, 1, '2024-10-01', 'Defective product', 2)
    
    assert str(exc_info.value) == "Database error"

@patch('app_devolucion_compra.create_connection')
def test_get_devoluciones_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching devoluciones
    mock_cursor.fetchall.return_value = [(1, 1, 1, 'Product A', '2024-10-01', 'Defective product', 2)]
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = [1]

    devoluciones, total_count = get_devoluciones(1, 10)

    assert len(devoluciones) == 1
    assert total_count == 1

@patch('app_devolucion_compra.create_connection')
def test_get_pedidos_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching pedidos
    mock_cursor.fetchall.return_value = [(1, '2024-10-01')]

    pedidos = get_pedidos()

    assert len(pedidos) == 1
    assert pedidos[0] == (1, '2024-10-01')

@patch('app_devolucion_compra.create_connection')
def test_get_detalles_by_pedido_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching detalles by pedido
    mock_cursor.fetchall.return_value = [(1, 1, 5, 100.0)]

    detalles = get_detalles_by_pedido(1)

    assert len(detalles) == 1
    assert detalles[0] == (1, 1, 5, 100.0)

@patch('app_devolucion_compra.create_connection')
def test_update_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful update
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_devolucion(1, 1, 1, '2024-10-01', 'Changed reason', 3)

    assert result is True  # Expecting the function to return True on success

@patch('app_devolucion_compra.create_connection')
def test_update_devolucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during update
    mock_cursor.execute.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        update_devolucion(1, 1, 1, '2024-10-01', 'Changed reason', 3)
    assert str(exc_info.value) == "Database error"


@patch('app_devolucion_compra.create_connection')
def test_delete_devolucion_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful deletion
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_devolucion(1)

    assert result is True  # Expecting the function to return True on success

@patch('app_devolucion_compra.create_connection')
def test_delete_devolucion_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during deletion
    mock_cursor.execute.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        delete_devolucion(1)
    assert str(exc_info.value) == "Database error"


@patch('app_devolucion_compra.create_connection')
def test_get_devolucion_by_id_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching devolucion by ID
    mock_cursor.fetchone.return_value = (1, 1, '2024-10-01', 'Defective product', 2)

    devolucion = get_devolucion_by_id(1)

    assert devolucion == (1, 1, '2024-10-01', 'Defective product', 2)

@patch('app_devolucion_compra.create_connection')
def test_get_devolucion_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate not finding devolucion
    mock_cursor.fetchone.return_value = None

    devolucion = get_devolucion_by_id(1)

    assert devolucion is None  # Expecting None when not found

@patch('app_devolucion_compra.create_connection')
def test_get_producto_by_id_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching producto by ID
    mock_cursor.fetchone.return_value = (1, 'Product A', 100.0)

    producto = get_producto_by_id(1)

    assert producto == (1, 'Product A', 100.0)

@patch('app_devolucion_compra.create_connection')
def test_get_producto_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate not finding producto
    mock_cursor.fetchone.return_value = None

    producto = get_producto_by_id(1)

    assert producto is None  # Expecting None when not found
