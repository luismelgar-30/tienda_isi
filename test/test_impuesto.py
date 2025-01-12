import pytest
from unittest.mock import patch, MagicMock
from app_impuesto import app_impuesto, insert_user, update_user, delete_user, get_impuesto, search_impuesto, get_impuesto_by_id

@pytest.fixture
def client():
    with app_impuesto.test_client() as client:
        yield client

@patch('app_impuesto.create_connection')
def test_insert_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate successful behavior
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_user("Tipo de Impuesto", 15.0)
    assert result is True

@patch('app_impuesto.create_connection')
def test_insert_user_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insertion
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        insert_user("Tipo de Impuesto", 15.0)
    
    assert str(exc_info.value) == "Error de base de datos"

@patch('app_impuesto.create_connection')
def test_update_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_user(1, "Tipo de Impuesto Actualizado", 20.0)
    assert result is True

@patch('app_impuesto.create_connection')
def test_update_user_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        update_user(1, "Tipo de Impuesto Actualizado", 20.0)
    
    assert str(exc_info.value) == "Error de base de datos"

@patch('app_impuesto.create_connection')
def test_delete_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_user(1)
    assert result is True

@patch('app_impuesto.create_connection')
def test_delete_user_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        delete_user(1)
    
    assert str(exc_info.value) == "Error de base de datos"

@patch('app_impuesto.create_connection')
def test_get_impuesto(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate the database response for fetching impuestos
    mock_cursor.fetchall.return_value = [(1, "Tipo 1", 10.0), (2, "Tipo 2", 15.0)]
    mock_cursor.fetchone.return_value = (2,)  # Simulate total count of 2 impuestos

    impuesto, total_count = get_impuesto(page=1, per_page=10)

    assert impuesto == [(1, "Tipo 1", 10.0), (2, "Tipo 2", 15.0)]
    assert total_count == 2

@patch('app_impuesto.create_connection')
def test_get_impuesto_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate an empty response from the database
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0 impuestos

    impuesto, total_count = get_impuesto(page=1, per_page=10)

    assert impuesto == []
    assert total_count == 0

@patch('app_impuesto.create_connection')
def test_get_impuesto_by_id(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a successful fetch by id
    mock_cursor.fetchone.return_value = (1, "Tipo 1", 10.0)

    impuesto = get_impuesto_by_id(1)
    assert impuesto == (1, "Tipo 1", 10.0)

@patch('app_impuesto.create_connection')
def test_get_impuesto_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate not found
    mock_cursor.fetchone.return_value = None

    impuesto = get_impuesto_by_id(999)  # Assuming this ID does not exist
    assert impuesto is None

@patch('app_impuesto.create_connection')
def test_search_impuesto(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a successful search
    mock_cursor.fetchall.return_value = [(1, "Tipo 1", 10.0)]
    mock_cursor.fetchone.return_value = (1,)  # Simulate total count of 1

    impuesto, total_count = search_impuesto("tipo_impuesto", "Tipo 1", page=1, per_page=10)

    assert impuesto == [(1, "Tipo 1", 10.0)]
    assert total_count == 1

@patch('app_impuesto.create_connection')
def test_search_impuesto_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate an empty search result
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0

    impuesto, total_count = search_impuesto("tipo_impuesto", "No Existe", page=1, per_page=10)

    assert impuesto == []
    assert total_count == 0

@patch('app_impuesto.create_connection')
def test_insert_user_with_invalid_data(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error for invalid data
    mock_cursor.execute.side_effect = Exception("Error de datos inválidos")

    with pytest.raises(Exception) as exc_info:
        insert_user("", -15.0)  # Invalid data

    assert str(exc_info.value) == "Error de datos inválidos"

@patch('app_impuesto.create_connection')
def test_update_user_with_invalid_data(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error for invalid data
    mock_cursor.execute.side_effect = Exception("Error de datos inválidos")

    with pytest.raises(Exception) as exc_info:
        update_user(1, "", -20.0)  # Invalid data

    assert str(exc_info.value) == "Error de datos inválidos"

@patch('app_impuesto.create_connection')
def test_delete_non_existent_user(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a delete on a non-existent user
    mock_cursor.execute.side_effect = Exception("Usuario no encontrado")

    with pytest.raises(Exception) as exc_info:
        delete_user(999)  # Assuming this ID does not exist

    assert str(exc_info.value) == "Usuario no encontrado"

if __name__ == '__main__':
    pytest.main()
