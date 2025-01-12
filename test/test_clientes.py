import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_cliente import insert_user, get_cliente, get_cliente_by_id, update_user, delete_user, search_users

# Test for insert_user function
@patch('app_cliente.create_connection')
def test_insert_user_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular una inserción exitosa
    result = insert_user('Juan', 'Perez', '1990-01-01', 'juan@example.com', '12345678', 'Calle 1', '2023-10-10', 'normal', '0801-1234-5678')
    
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result == True

def validate_name(name):
    if not name:
        return "El nombre no puede estar vacío."
    
    if re.search(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', name):
        return "El nombre contiene caracteres especiales."
    
    if len(name) > 50:
        return "El nombre no puede tener más de 50 caracteres."
    
    if len(name) < 3:
        return "El nombre debe tener al menos 3 caracteres."
    
    if re.search(r'(.)\1{2,}', name):
        return "El nombre no puede tener más de dos caracteres idénticos consecutivos."
    
   
    
    return None

# Validación del email
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return "El email no tiene un formato válido."
    return None

# Pruebas unitarias
@pytest.mark.parametrize("name,expected", [
    ("", "El nombre no puede estar vacío."),
    ("Juan@", "El nombre contiene caracteres especiales."),
    ("A" * 51, "El nombre no puede tener más de 50 caracteres."),
    ("Ju", "El nombre debe tener al menos 3 caracteres."),
    ("Juaaan", "El nombre no puede tener más de dos caracteres idénticos consecutivos."),
  
    ("Juan", None),  # Nombre válido
])
def test_validate_name(name, expected):
    assert validate_name(name) == expected

@pytest.mark.parametrize("email,expected", [
    ("correo@", "El email no tiene un formato válido."),
    ("correo@dominio", "El email no tiene un formato válido."),
    ("correo@dominio.com", None),  # Email válido
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected

@patch('app_cliente.create_connection')
def test_insert_user_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    # Simular una inserción fallida (sin conexión)
    result = insert_user('Juan', 'Perez', '1990-01-01', 'juan@example.com', '12345678', 'Calle 1', '2023-10-10', 'normal', '0801-1234-5678')
    
    assert result is None

# Test for get_cliente function
@patch('app_cliente.create_connection')
def test_get_cliente_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular datos de cliente
    mock_cursor.fetchall.return_value = [('Juan', 'Perez', 'juan@example.com')]
    
    result = get_cliente()
    
    mock_cursor.execute.assert_called_once_with("SELECT * FROM cliente")
    assert result == [('Juan', 'Perez', 'juan@example.com')]

@patch('app_cliente.create_connection')
def test_get_cliente_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    result = get_cliente()
    
    assert result == []

# Test for get_cliente_by_id function
@patch('app_cliente.create_connection')
def test_get_cliente_by_id_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Simular datos del cliente por id
    mock_cursor.fetchone.return_value = ('Juan', 'Perez', 'juan@example.com')
    
    result = get_cliente_by_id(1)
    
    mock_cursor.execute.assert_called_once_with("SELECT * FROM cliente WHERE id_cliente = %s", (1,))
    assert result == ('Juan', 'Perez', 'juan@example.com')

@patch('app_cliente.create_connection')
def test_get_cliente_by_id_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    result = get_cliente_by_id(1)
    
    assert result is None

# Test for update_user function
@patch('app_cliente.create_connection')
def test_update_user_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    result = update_user(1, 'Juan', 'Perez', '1990-01-01', 'juan@example.com', '12345678', 'Calle 1', '2023-10-10', 'normal', '0801-1234-5678')
    
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result == True

@patch('app_cliente.create_connection')
def test_update_user_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    result = update_user(1, 'Juan', 'Perez', '1990-01-01', 'juan@example.com', '12345678', 'Calle 1', '2023-10-10', 'normal', '0801-1234-5678')
    
    assert result == False

# Test for delete_user function
@patch('app_cliente.create_connection')
def test_delete_user_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    result = delete_user(1)
    
    mock_cursor.execute.assert_called_once_with("DELETE FROM cliente WHERE id_cliente = %s", (1,))
    mock_conn.commit.assert_called_once()
    assert result == True

@patch('app_cliente.create_connection')
def test_delete_user_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    result = delete_user(1)
    
    assert result == False

# Test for search_users function
@patch('app_cliente.create_connection')
def test_search_users_success(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [('Juan', 'Perez', 'juan@example.com')]
    
    result = search_users('Juan')
    
    assert result == [('Juan', 'Perez', 'juan@example.com')]

@patch('app_cliente.create_connection')
def test_search_users_failure(mock_create_connection):
    mock_create_connection.return_value = None
    
    result = search_users('Juan')
    
    assert result == []
