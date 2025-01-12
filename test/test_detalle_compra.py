import pytest
from unittest.mock import patch, MagicMock
from app_detalle_compra import app_detalles_compra, insert_detalle, get_precio, get_detalles, get_detalle_by_id, update_detalle, delete_detalle, get_stock

@pytest.fixture
def client():
    with app_detalles_compra.test_client() as client:
        yield client

@patch('app_detalle_compra.create_connection')
def test_insert_detalle_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful insertion
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_detalle(1, 1, 1, 10, 100.0, 1000.0, 1, 1100.0)

@patch('app_detalle_compra.create_connection')
def test_insert_detalle_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insertion
    mock_cursor.execute.side_effect = Exception("Database error")

    result = insert_detalle(1, 1, 1, 10, 100.0, 1000.0, 1, 1100.0)

    assert result is False  # Expecting the function to return False on error

@patch('app_detalle_compra.create_connection')
def test_get_precio_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching the product price
    mock_cursor.fetchone.return_value = (150.0,)

    result, status = get_precio(1)
    assert result['precio_unitario'] == 150.0
    assert status == 200

@patch('app_detalle_compra.create_connection')
def test_get_precio_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate no product found
    mock_cursor.fetchone.return_value = None

    result, status = get_precio(1)
    assert result['precio_unitario'] == 0
    assert status == 404

@patch('app_detalle_compra.create_connection')
def test_get_detalles_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching details
    mock_cursor.fetchall.return_value = [
        (1, 1, 'Empleado 1', 'Producto 1', 5, 50.0, 250.0, 15.0, 265.0),
        (2, 1, 'Empleado 2', 'Producto 2', 3, 30.0, 90.0, 10.0, 100.0)
    ]
    mock_cursor.fetchone.return_value = (2,)

    detalles, total_count = get_detalles(1, 10)
    assert len(detalles) == 2
    assert total_count == 2

@patch('app_detalle_compra.create_connection')
def test_update_detalle_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful update
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_detalle(1, 1, 1, 1, 10, 100.0, 1000.0, 1, 1100.0)
    assert result is True

@patch('app_detalle_compra.create_connection')
def test_delete_detalle_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful deletion
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_detalle(1)  # Call the delete function

    assert result is True  

@patch('app_detalle_compra.create_connection')
def test_get_stock_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate fetching stock data
    mock_cursor.fetchone.return_value = (100, 10, 200)

    with app_detalles_compra.test_client() as client:
        response = client.get('/get_stock/1')
        data = response.get_json()

        assert data['stock'] == 100
        assert data['stock_minimo'] == 10
        assert data['stock_maximo'] == 200
        assert response.status_code == 200

if __name__ == '__main__':
    pytest.main()
