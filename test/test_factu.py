import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app_factu import app_factu, insert_factu, update_factu, delete_factu, get_factu, search_factu, get_factu_by_id, get_next_numero_factura, get_sar, get_sar_details

@pytest.fixture
def client():
    with app_factu.test_client() as client:
        yield client

@patch('app_factu.create_connection')
def test_insert_factu_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simula un comportamiento exitoso
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = insert_factu(1, "Factura123")
    assert result is True

@patch('app_factu.create_connection')
def test_insert_factu_failure(mock_create_connection):
    mock_create_connection.side_effect = Exception("Error de conexión")  # Simula un error de conexión

    with pytest.raises(Exception):  # Esperar una excepción
        insert_factu(1, "Factura1")

@patch('app_factu.create_connection')
def test_update_factu_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = update_factu(1, "Factura Actualizada")  # Ajustar la cantidad de argumentos
    assert result is True

@patch('app_factu.create_connection')
def test_update_factu_failure(mock_create_connection):
    mock_create_connection.side_effect = Exception("Error de conexión")

    with pytest.raises(Exception):  # Esperar una excepción
        update_factu(1, "Nuevo Valor")  # Ajustar la cantidad de argumentos

@patch('app_factu.create_connection')
def test_delete_factu_success(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular un comportamiento exitoso
    mock_cursor.execute.return_value = None
    mock_connection.commit.return_value = None

    result = delete_factu(1)  # Ajustar si delete_factu retorna True en caso de éxito
    assert result is True

@patch('app_factu.create_connection')
def test_delete_factu_failure(mock_create_connection):
    mock_create_connection.side_effect = Exception("Error de conexión")

    with pytest.raises(Exception):  # Esperar una excepción
        delete_factu(1)

@patch('app_factu.create_connection')
def test_get_factu(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1, 1, "Factura1"), (2, 1, "Factura2")]
    mock_cursor.fetchone.return_value = (2,)

    factu, total_count = get_factu(page=1, per_page=10)

    assert factu == [(1, 1, "Factura1"), (2, 1, "Factura2")]
    assert total_count == 2

@patch('app_factu.create_connection')
def test_search_factu(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simular respuesta de la base de datos
    mock_cursor.fetchall.return_value = [(1, "Factura1"), (2, "Factura2")]
    mock_cursor.fetchone.return_value = (2,)  # Simular conteo total de 2 facturas

    # Llama a la función con los criterios de búsqueda
    facturas, total_count = search_factu("id_sar", "Factura", 1, 10)

    # Asegúrate de que el retorno sea el esperado
    assert facturas == [(1, "Factura1"), (2, "Factura2")]
    assert total_count == 2

@patch('app_factu.create_connection')
def test_get_factu_by_id(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1, 1, "Factura1")

    factu = get_factu_by_id(1)

    assert factu == (1, 1, "Factura1")

@patch('app_factu.create_connection')
def test_get_next_numero_factura(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    # Simula el último número de factura y los detalles de SAR
    mock_cursor.fetchone.side_effect = [(None), (1, "00100000", "00199999")]

    numero_factura = get_next_numero_factura(1)

    assert numero_factura is not None

@patch('app_factu.create_connection')
def test_get_sar(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1,), (2,)]

    sar = get_sar()

    assert sar == [1, 2]

@patch('app_factu.create_connection')
def test_get_sar_details(mock_create_connection):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1, "00100000", "00199999")

    sar_details = get_sar_details(1)

    assert sar_details == (1, "00100000", "00199999")

if __name__ == '__main__':
    pytest.main()
