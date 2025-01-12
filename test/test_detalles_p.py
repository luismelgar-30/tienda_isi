import pytest
from app_detalle_p import app_detalle_p, insert_or_update_detalle, get_detalles, get_detalle_by_id, update_detalle, delete_detalle
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app_detalle_p.config['TESTING'] = True
    with app_detalle_p.test_client() as client:
        yield client
      

def test_insert_or_update_detalle(client):
    # Simulando la conexión a la base de datos
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Simulamos la inserción
        mock_cursor.fetchone.return_value = None  # Simulamos que no existe el detalle, así que se insertará
        mock_cursor.execute.return_value = None  # Simulamos una inserción exitosa

        result = insert_or_update_detalle(1, 1, 5, 10.0, 50.0, 1, 57.5)
        assert result is True

def test_get_detalle_by_id(client):
    # Simulando la conexión a la base de datos
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = (1, 1, 1, 5, 10.0, 50.0, 1, 57.5)  # Simulando el detalle
        
        detalle = get_detalle_by_id(1)
        
        assert detalle is not None
        assert detalle[1] == 1  # id_pedido
        assert detalle[2] == 1  # id_producto

def test_update_detalle(client):
    # Simulando la conexión a la base de datos
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.execute.return_value = None  # Simulamos una actualización exitosa

        result = update_detalle(1, 1, 1, 5, 10.0, 50.0, 1, 57.5)
        
        assert result is True

def test_delete_detalle(client):
    # Simulando la conexión a la base de datos
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.execute.return_value = None  # Simulamos una eliminación exitosa
        
        result = delete_detalle(1)  # Intentamos eliminar el detalle con ID 1
        
        assert result is True

def test_insert_or_update_detalle_error(client):
    # Simulando la conexión a la base de datos y generando un error
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simulamos un error de base de datos al intentar insertar
        mock_cursor.execute.side_effect = Exception("Error de base de datos")

        with pytest.raises(Exception) as exc_info:
            insert_or_update_detalle(1, 1, 5, 10.0, 50.0, 1, 57.5)
        
        assert str(exc_info.value) == "Error de base de datos"

def test_get_detalle_by_id_not_found(client):
    # Simulando la conexión a la base de datos
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = None  # Simulamos que no se encuentra el detalle

        detalle = get_detalle_by_id(999)  # ID que no existe
        
        assert detalle is None  # Debería ser None si no se encuentra el detalle

def test_update_detalle_error(client):
    # Simulando la conexión a la base de datos y generando un error
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simulamos un error al intentar actualizar
        mock_cursor.execute.side_effect = Exception("Error al actualizar")

        with pytest.raises(Exception) as exc_info:
            update_detalle(1, 1, 1, 5, 10.0, 50.0, 1, 57.5)
        
        assert str(exc_info.value) == "Error al actualizar"

def test_delete_detalle_error(client):
    # Simulando la conexión a la base de datos y generando un error
    with patch('app_detalle_p.create_connection') as mock_create_connection:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        
        # Simulamos un error al intentar eliminar
        mock_cursor.execute.side_effect = Exception("Error al eliminar")

        with pytest.raises(Exception) as exc_info:
            delete_detalle(999)  # Intentamos eliminar un detalle que no existe
        
        assert str(exc_info.value) == "Error al eliminar"

