import pytest
from unittest.mock import patch, MagicMock
import re

# Importación de funciones de la aplicación de promoción
from app_promocion import insert_promocion, get_promocion, get_promocion_by_id, update_promocion, delete_promocion

# Validar nombre de la promoción con reglas
def validar_nombre_promocion(nombre):
    if not nombre:
        return False, "El nombre de la promoción no puede estar vacío."
    if len(nombre) < 3 or len(nombre) > 100:
        return False, "El campo debe tener entre 3 y 100 caracteres."
    if re.search(r'\d', nombre):
        return False, "El campo no puede contener números."
    if not re.match("^[A-Za-zÀ-ÿ '-]+$", nombre):
        return False, "El campo no puede contener caracteres especiales."
    if re.search(r'(.)\1\1', nombre):
        return False, "El campo no puede contener tres letras seguidas iguales."
    return True, ""

# Validar valor de la promoción (descripción) con longitud máxima
def validar_valor_promocion(valor):
    if len(valor) > 255:
        return False, "El valor de la promoción no puede tener más de 255 caracteres."
    return True, ""

# Modificar insert_promocion para usar las validaciones
def insert_promocion_validated(nombre, valor):
    # Validar nombre
    valid, msg = validar_nombre_promocion(nombre)
    if not valid:
        return False, msg
    # Validar valor
    valid, msg = validar_valor_promocion(valor)
    if not valid:
        return False, msg
    try:
        insert_promocion(nombre, valor)
        return True, ""
    except Exception as e:
        return False, str(e)

@pytest.fixture
def mock_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

# Prueba de inserción de promoción exitosa
@patch('app_promocion.create_connection')
def test_insert_promocion_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    # Simular una ejecución exitosa de la consulta
    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    # Asegurarse de que el nombre y la descripción cumplan con las validaciones
    result, msg = insert_promocion_validated('Promocion Uno', 'Descripción de prueba')
    assert result == True
    assert msg == ""

    # Ajustar la llamada para que coincida con el salto de línea
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO promocion (nombre, valor)\n               VALUES (%s, %s)",
        ('Promocion Uno', 'Descripción de prueba')
    )
    mock_conn.commit.assert_called_once()

# Casos inválidos para validar el nombre de la promoción
def test_validar_nombre_promocion_invalid_cases():
    # Demasiado corto
    assert validar_nombre_promocion("A") == (False, "El campo debe tener entre 3 y 100 caracteres.")
    # Contiene números
    assert validar_nombre_promocion("Promocion123") == (False, "El campo no puede contener números.")
    # Contiene caracteres especiales
    assert validar_nombre_promocion("Promocion@") == (False, "El campo no puede contener caracteres especiales.")
    # Letras consecutivas repetidas
    assert validar_nombre_promocion("Promooocion") == (False, "El campo no puede contener tres letras seguidas iguales.")

# Casos válidos para validar el nombre de la promoción
def test_validar_nombre_promocion_valid_cases():
    # Nombre válido
    assert validar_nombre_promocion("Promocion") == (True, "")
    assert validar_nombre_promocion("Promoción Especial") == (True, "")

# Prueba de actualización exitosa


# Prueba de eliminación exitosa
@patch('app_promocion.create_connection')
def test_delete_promocion_success(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    mock_cursor.execute.return_value = None
    mock_conn.commit.return_value = None

    result = delete_promocion(1)
    assert result == True

    mock_cursor.execute.assert_called_once_with("DELETE FROM promocion WHERE id_promocion = %s", (1,))
    mock_conn.commit.assert_called_once()

# Prueba de obtención de promociones
@patch('app_promocion.create_connection')
def test_get_promocion(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    # Simular la consulta exitosa
    mock_cursor.fetchall.return_value = [
        (1, 'Promocion 1', 'Descripción de prueba')
    ]

    result = get_promocion(10, 0)  # Proporciona 'limit' y 'offset'
    assert result == [(1, 'Promocion 1', 'Descripción de prueba')]

    mock_cursor.execute.assert_called_once_with("SELECT * FROM promocion LIMIT %s OFFSET %s", (10, 0))

# Prueba de obtención de promoción por ID
@patch('app_promocion.create_connection')
def test_get_promocion_by_id(mock_create_connection, mock_connection):
    mock_conn, mock_cursor = mock_connection
    mock_create_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1, 'Promocion 1', 'Descripción de prueba')

    result = get_promocion_by_id(1)
    assert result == (1, 'Promocion 1', 'Descripción de prueba')

    mock_cursor.execute.assert_called_once_with("SELECT * FROM promocion WHERE id_promocion = %s", (1,))

if __name__ == '__main__':
    pytest.main()
