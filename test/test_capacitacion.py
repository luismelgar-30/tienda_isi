import pytest
from unittest.mock import patch, MagicMock
from app_capacitacion import insert_capacitacion, update_capacitacion, delete_capacitacion, get_empleados

# Validar campos de texto
def validate_text_field(text):
    if len(text) < 3 or len(text) > 20:
        return False, "El campo debe tener entre 3 y 20 caracteres."
    if any(char.isdigit() for char in text):
        return False, "El campo no puede contener números."
    if not all(char.isalnum() or char.isspace() for char in text):
        return False, "El campo no puede contener caracteres especiales."
    return True, ""

# Modificar insert_capacitacion para usar las validaciones
def insert_capacitacion_validated(id_empleado, tema, fecha, duracion, costo):  # Cambié 'nombre' por 'tema'
    valid, msg = validate_text_field(tema)  # Cambié 'nombre' por 'tema'
    if not valid:
        return False, msg
    try:
        insert_capacitacion(id_empleado, tema, fecha, duracion, costo)  # Cambié 'nombre' por 'tema'
        return True, ""
    except Exception as e:
        return False, str(e)

@pytest.fixture
def mock_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

# Casos inválidos para validar el campo de texto
def test_validate_text_field():
    assert validate_text_field("C") == (False, "El campo debe tener entre 3 y 20 caracteres.")
    assert validate_text_field("Capacitación123") == (False, "El campo no puede contener números.")
    assert validate_text_field("Capacitación@") == (False, "El campo no puede contener caracteres especiales.")
    assert validate_text_field("Capacitación válida") == (True, "")

# Prueba de eliminación exitosa
@patch('app_capacitacion.create_connection')
def test_delete_capacitacion_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = delete_capacitacion(1)
    assert result == True

    mock_cursor.execute.assert_called_once_with("DELETE FROM capacitacion WHERE id_capacitacion = %s", (1,))
    mock_conn.commit.assert_called_once()

# Prueba de obtención de empleados
@patch('app_capacitacion.create_connection')
def test_get_empleados(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    # Simular respuesta de la base de datos
    mock_cursor.fetchall.return_value = [(1, "Empleado 1"), (2, "Empleado 2")]

    empleados = get_empleados()
    assert empleados == [(1, "Empleado 1"), (2, "Empleado 2")]

    mock_cursor.execute.assert_called_once_with("SELECT id_empleado, nombre FROM empleados")

# Prueba de obtención de empleados vacía
@patch('app_capacitacion.create_connection')
def test_get_empleados_empty(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    empleados = get_empleados()
    assert empleados == []

if __name__ == '__main__':
    pytest.main()
