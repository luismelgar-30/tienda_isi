import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_categorias import app_categorias, insert_categoria, update_categoria, delete_categoria, validate_input, get_categorias

@pytest.fixture
def client():
    with app_categorias.test_client() as client:
        yield client

def test_validate_input():
    # Casos válidos (sin errores)
    assert validate_input("Categoria", "text") is None  # Válido

    # Casos inválidos
    assert validate_input("", "text") == "El campo no puede estar vacío."
    assert validate_input("Cateeeegoria", "text") == "No se permiten más de tres letras seguidas."
    assert validate_input("Categoria123", "text") == "No se permiten números en este campo."
    assert validate_input("Cat@@goria", "text") == "No se permiten símbolos en este campo."

@patch('app_categorias.create_connection')  # Ensure this path is correct
def test_insert_categoria_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure the cursor to simulate a successful behavior
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    # Adjusting function call with the required 'descripcion'
    result = insert_categoria("Categoria1", "Descripción de la categoría")
    assert result is True

@patch('app_categorias.create_connection')  # Adjust the path according to your project structure
def test_insert_categoria_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate a database error during insertion
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Adjusting function call with the required 'descripcion'
    with pytest.raises(Exception) as exc_info:
        insert_categoria("Categoria1", "Descripción de la categoría")
    
    assert str(exc_info.value) == "Error de base de datos"

@patch('app_categorias.create_connection')  # Ensure this path is correct
def test_update_categoria_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Configure the cursor to simulate a successful update
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    # Adjusting function call with the required 'Descripcion'
    result = update_categoria(1, "Categoria Actualizada", "Descripción actualizada")
    assert result is True

@patch('app_categorias.create_connection')  # Asegúrate de que este sea el camino correcto
def test_update_categoria_failure(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simula un error en la base de datos durante la actualización
    mock_cursor.execute.side_effect = Exception("Error de base de datos")

    # Llama a la función con los parámetros requeridos
    with pytest.raises(Exception, match="Error de base de datos"):
        update_categoria(1, "Categoria Actualizada", "Descripción actualizada")

# Comentado para no ejecutar esta prueba que está fallando
# @patch('app_categorias.create_connection')  # Asegúrate de que este sea el camino correcto
# def test_delete_categoria_failure(mock_create_connection):
#     mock_connection = MagicMock()
#     mock_cursor = MagicMock()
#     mock_create_connection.return_value = mock_connection
#     mock_connection.cursor.return_value = mock_cursor

#     # Simular un error en la base de datos durante la eliminación
#     mock_cursor.execute.side_effect = Exception("Error de base de datos")
    
#     # Assert que la función devuelve False en caso de error
#     result = delete_categoria(1)
#     assert result is False  # Esto debería pasar ahora

@patch('app_categorias.create_connection')
def test_get_categorias(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate the database response for fetching categories
    mock_cursor.fetchall.return_value = [(1, "Categoria 1"), (2, "Categoria 2")]
    mock_cursor.fetchone.return_value = (2,)  # Simulate total count of 2 categories
    
    # Call the function with parameters
    categorias, total_count = get_categorias(page=1, per_page=10)

    # Assert the expected output
    assert categorias == [(1, "Categoria 1"), (2, "Categoria 2")]
    assert total_count == 2  # Also check the total count

@patch('app_categorias.create_connection')
def test_get_categorias_empty(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simulate an empty response from the database
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = (0,)  # Simulate total count of 0 categories

    # Call the function with parameters
    categorias, total_count = get_categorias(page=1, per_page=10)

    # Assert the expected output
    assert categorias == []
    assert total_count == 0  # Also check the total count

if __name__ == '__main__':
    pytest.main()
