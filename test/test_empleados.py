import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_empleados import app_empleados, insert_user, update_user, delete_user, get_empleados, get_empleados_by_id, search_users

@pytest.fixture
def client():
    with app_empleados.test_client() as client:
        yield client


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_insert_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_user("Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "email@example.com", "1234567890", "Tipo", "12345678", "password")
    assert result is True


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_insert_user_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        insert_user("Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "email@example.com", "1234567890", "Tipo", "12345678", "password")

    assert str(exc_info.value) == "Error de base de datos"


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_update_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_user(1, "Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "email@example.com", "1234567890", "Tipo", "12345678", "password")
    assert result is True


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_update_user_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    with pytest.raises(Exception) as exc_info:
        update_user(1, "Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "email@example.com", "1234567890", "Tipo", "12345678", "password")

    assert str(exc_info.value) == "Error de base de datos"


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_delete_user_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_user(1)
    assert result is True

@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_get_empleados(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1, "Nombre", "Apellido", "2000-01-01", "email@example.com")]
    mock_cursor.fetchone.return_value = (1,)

    empleados, total_count = get_empleados(page=1, per_page=10)

    assert empleados == [(1, "Nombre", "Apellido", "2000-01-01", "email@example.com")]
    assert total_count == 1


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_get_empleados_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)

    empleados, total_count = get_empleados(page=1, per_page=10)

    assert empleados == []
    assert total_count == 0


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_search_users_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1, "Nombre", "Apellido", "2000-01-01", "email@example.com")]
    mock_cursor.fetchone.return_value = (1,)

    empleados, total_count = search_users("Nombre", "nombre", page=1, per_page=10)

    assert empleados == [(1, "Nombre", "Apellido", "2000-01-01", "email@example.com")]
    assert total_count == 1


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_search_users_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)

    empleados, total_count = search_users("NoExiste", "nombre", page=1, per_page=10)

    assert empleados == []
    assert total_count == 0


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_get_empleados_by_id(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1, "Nombre", "Apellido", "2000-01-01", "email@example.com")

    empleado = get_empleados_by_id(1)

    assert empleado == (1, "Nombre", "Apellido", "2000-01-01", "email@example.com")


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_get_empleados_by_id_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    empleado = get_empleados_by_id(999)

    assert empleado is None


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_get_empleados_by_id_error(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.side_effect = Exception("Error al buscar empleado")

    with pytest.raises(Exception) as exc_info:
        get_empleados_by_id(1)

    assert str(exc_info.value) == "Error al buscar empleado"


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_insert_user_duplicate_email(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Email ya existe")

    with pytest.raises(Exception) as exc_info:
        insert_user("Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "duplicate@example.com", "1234567890", "Tipo", "12345678", "password")

    assert str(exc_info.value) == "Email ya existe"


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_update_user_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Empleado no encontrado")

    with pytest.raises(Exception) as exc_info:
        update_user(999, "Nombre", "Apellido", "2000-01-01", 1, "2024-01-01", 1, "email@example.com", "1234567890", "Tipo", "12345678", "password")

    assert str(exc_info.value) == "Empleado no encontrado"


@patch('app_empleados.create_connection')  # Asegúrate de que esta ruta sea correcta
def test_delete_user_not_found(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.side_effect = Exception("Empleado no encontrado")

    with pytest.raises(Exception) as exc_info:
        delete_user(999)

    assert str(exc_info.value) == "Empleado no encontrado"

