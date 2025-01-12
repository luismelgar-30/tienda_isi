import pytest
from unittest.mock import patch, MagicMock
from app_equipo import app_equipo, insert_equipo, get_equipos, update_equipo, delete_equipo, get_equipo_by_id

@pytest.fixture
def client():
    with app_equipo.test_client() as client:
        yield client

# Tests for insert_equipo
@patch('app_equipo.create_connection')
def test_insert_equipo_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_equipo(1, "Tipo1", "Modelo1", "1234567", "Nuevo")
    assert result is True

@patch('app_equipo.create_connection')
def test_insert_equipo_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Error de base de datos")
    
    result = insert_equipo(1, "Tipo1", "Modelo1", "1234567", "Nuevo")
    assert result is False

# Tests for get_equipos
@patch('app_equipo.create_connection')
def test_get_equipos_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1, "Tipo1", "Modelo1", "1234567", "Nuevo")]
    mock_cursor.fetchone.return_value = (1,)  # Simulate total count of 1

    equipos, total_count = get_equipos(page=1, per_page=10)
    assert equipos == [(1, "Tipo1", "Modelo1", "1234567", "Nuevo")]
    assert total_count == 1

@patch('app_equipo.create_connection')
def test_get_equipos_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0

    equipos, total_count = get_equipos(page=1, per_page=10)
    assert equipos == []
    assert total_count == 0

# Tests for get_equipo_by_id
@patch('app_equipo.create_connection')
def test_get_equipo_by_id_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1, "Tipo1", "Modelo1", "1234567", "Nuevo")
    
    equipo = get_equipo_by_id(1)
    assert equipo == (1, "Tipo1", "Modelo1", "1234567", "Nuevo")

@patch('app_equipo.create_connection')
def test_get_equipo_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None
    
    equipo = get_equipo_by_id(999)  # Assuming 999 does not exist
    assert equipo is None

# Tests for update_equipo
# Tests for update_equipo
@patch('app_equipo.create_connection')
def test_update_equipo_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_equipo(1, "Tipo Actualizado", "Modelo Actualizado", "7654321", "Usado")
    assert result is True

@patch('app_equipo.create_connection')
def test_update_equipo_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulamos que ocurre un error al ejecutar la consulta
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Verificamos que el resultado sea False al manejar la excepción
    result = update_equipo(1, "Tipo Actualizado", "Modelo Actualizado", "7654321", "Usado")
    assert result is False  # Cambiamos a este resultado esperado

# Tests for delete_equipo
@patch('app_equipo.create_connection')
def test_delete_equipo_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_equipo(1)
    assert result is True

@patch('app_equipo.create_connection')
def test_delete_equipo_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulamos que ocurre un error al ejecutar la consulta
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Verificamos que el resultado sea False al manejar la excepción
    result = delete_equipo(1)
    assert result is False  # Cambiamos a este resultado esperado


if __name__ == '__main__':
    pytest.main()
