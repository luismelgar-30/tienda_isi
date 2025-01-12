import pytest
from unittest.mock import patch, MagicMock
from app_sar import app_sar, insert_sar, get_sar, get_sar_by_id, update_sar, delete_sar

@pytest.fixture
def client():
    with app_sar.test_client() as client:
        yield client


@patch('app_sar.create_connection')
def test_insert_sar_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular inserción exitosa
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_sar("123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")
    assert result is True


@patch('app_sar.create_connection')
def test_get_sar(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular respuesta de la base de datos al obtener SAR
    mock_cursor.fetchall.return_value = [(1, "123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")]

    sar = get_sar()
    
    assert sar == [(1, "123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")]


@patch('app_sar.create_connection')
def test_get_sar_by_id_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular respuesta para un ID de SAR específico
    mock_cursor.fetchone.return_value = (1, "123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")

    sar = get_sar_by_id(1)

    assert sar == (1, "123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")


@patch('app_sar.create_connection')
def test_get_sar_by_id_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular no encontrar el ID de SAR
    mock_cursor.fetchone.return_value = None

    sar = get_sar_by_id(999)  # Asumir que este ID no existe

    assert sar is None


@patch('app_sar.create_connection')
def test_update_sar_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular actualización exitosa
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_sar(1, "123456789", "CAI123", "2023-01-01", "2024-01-01", "100", "200", 1, "1", "Activo")
    assert result is True




@patch('app_sar.create_connection')
def test_delete_sar_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular eliminación exitosa
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_sar(1)
    assert result is True

if __name__ == '__main__':
    pytest.main()
