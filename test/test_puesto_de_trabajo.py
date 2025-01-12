
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Importar la librería para validaciones de expresiones regulares

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app_puesto_de_trabajo import app_puesto_de_trabajo, create_connection, insert_puesto_de_trabajo, update_puesto_de_trabajo, delete_puesto_de_trabajo, get_puesto_de_trabajo_by_id

@pytest.fixture
def client():
    app_puesto_de_trabajo.config['TESTING'] = True
    client = app_puesto_de_trabajo.test_client()
    yield client

# Prueba de inserción de puesto de trabajo
def test_insert_puesto_de_trabajo(client):
    result = insert_puesto_de_trabajo('Gerente', '09:00', '18:00', 30000)
    assert result is True, "Error al insertar el puesto de trabajo"

# Prueba de actualización de puesto de trabajo
def test_update_puesto_de_trabajo(client):
    # Asume que existe un puesto con id 5
    result = update_puesto_de_trabajo(16, '09:00', '18:00', 'Gerente', 35000)
    assert result is True, "Error al actualizar el puesto de trabajo"

# Prueba de eliminación de puesto de trabajo
def test_delete_puesto_de_trabajo(client):
    # Asume que existe un puesto con id 1
    result = delete_puesto_de_trabajo(1)
    assert result is True, "Error al eliminar el puesto de trabajo"

# Prueba de obtención de un puesto de trabajo por id
def test_get_puesto_de_trabajo_by_id(client):
    puesto = get_puesto_de_trabajo_by_id(17)
    assert puesto is not None, "Error al obtener el puesto de trabajo"
    assert puesto[1] == 'Gerente', "El nombre del puesto no coincide"
    assert puesto[4] == 35000, "El salario del puesto no coincide"

import pytest

# Pruebas para el campo puesto_trabajo
@pytest.mark.parametrize("puesto_trabajo, expected_error", [
    ("", "El puesto de trabajo no puede estar vacío."),  # Campo vacío
    ("abc123", "El puesto de trabajo solo debe contener letras y espacios."),  # Contiene números
    ("Puesto!", "El puesto de trabajo solo debe contener letras y espacios."),  # Contiene caracteres especiales
    ("Aaaa", "El puesto de trabajo no puede tener tres letras o espacios repetidos consecutivamente."),  # Tres letras repetidas
    ("coope", "El puesto de trabajo no puede tener dos vocales iguales consecutivas."),  # Dos vocales iguales seguidas
    ("ab", "El puesto de trabajo debe tener entre 3 y 20 caracteres."),  # Menos de 3 caracteres
])
def test_validate_puesto_trabajo(puesto_trabajo, expected_error):
    from app_puesto_de_trabajo import validate_puesto_trabajo
    error_message = validate_puesto_trabajo(puesto_trabajo)
    assert error_message == expected_error, f"Error: {error_message}, Expected: {expected_error}"

# Pruebas para el campo salario
@pytest.mark.parametrize("salario, expected_error", [
    ("abc", "El salario debe ser un número decimal válido."),  # Letras en el campo salario
    ("5000", "El salario debe estar entre 7000 y 125000."),  # Salario menor que el límite
    ("150000", "El salario debe estar entre 7000 y 125000."),  # Salario mayor que el límite
])
def test_validate_salary(salario, expected_error):
    from app_puesto_de_trabajo import validate_salary
    error_message = validate_salary(salario)
    assert error_message == expected_error, f"Error: {error_message}, Expected: {expected_error}"
