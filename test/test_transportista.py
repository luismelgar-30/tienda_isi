import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import re  # Para validar los caracteres especiales

# Asegúrate de que la carpeta principal esté en el PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from app_transportistas import insert_transportista, get_transportista, get_transportista_by_id, update_transportista, delete_transportista

class TestTransportistasCRUD(unittest.TestCase):
    
    @patch('app_transportistas.create_connection')
    def test_insert_transportista_success(self, mock_create_connection):
        # Simula una conexión exitosa
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula que se ejecuta el insert sin errores
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        result = insert_transportista("Empresa Test", "9123-4567")
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO transportistas (nombre_empresa, Telefono) VALUES (%s, %s)", 
            ("Empresa Test", "9123-4567")
        )

    @patch('app_transportistas.create_connection')
    def test_insert_transportista_fail(self, mock_create_connection):
        # Simula un fallo en la conexión
        mock_create_connection.return_value = None
        
        result = insert_transportista("Empresa Test", "9123-4567")
        self.assertFalse(result)

    @patch('app_transportistas.create_connection')
    def test_get_transportista(self, mock_create_connection):
        # Simula una conexión exitosa y una respuesta de la BD
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula los resultados que devolvería la BD
        mock_cursor.fetchall.return_value = [("Empresa Test", "9123-4567")]
        mock_cursor.fetchone.return_value = (1,)
        
        result, count = get_transportista(1, 10)
        self.assertEqual(result, [("Empresa Test", "9123-4567")])
        self.assertEqual(count, 1)

    @patch('app_transportistas.create_connection')
    def test_get_transportista_by_id(self, mock_create_connection):
        # Simula una conexión exitosa y una respuesta de la BD
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula el resultado de una consulta por ID
        mock_cursor.fetchone.return_value = ("Empresa Test", "9123-4567")
        
        result = get_transportista_by_id(1)
        self.assertEqual(result, ("Empresa Test", "9123-4567"))
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM transportistas WHERE id_transportista = %s", (1,)
        )

    @patch('app_transportistas.create_connection')
    def test_update_transportista_success(self, mock_create_connection):
        # Simula una conexión exitosa y una actualización correcta
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Simula que se ejecuta el update sin errores
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None

        result = update_transportista(1, "Empresa Actualizada", "1234-5678")
        self.assertTrue(result)

        # Normaliza los espacios en la consulta SQL para la comparación
        expected_query = "\n    UPDATE transportistas\n    SET nombre_empresa = %s, Telefono = %s\n    WHERE id_transportista = %s\n    ".strip()
        actual_query = "UPDATE transportistas SET nombre_empresa = %s, Telefono = %s WHERE id_transportista = %s".strip()

        mock_cursor.execute.assert_called_once_with(
            actual_query,
            ("Empresa Actualizada", "1234-5678", 1)
        )



    @patch('app_transportistas.create_connection')
    def test_delete_transportista_success(self, mock_create_connection):
        # Simula una conexión exitosa y una eliminación correcta
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_create_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula que se ejecuta el delete sin errores
        mock_cursor.execute.return_value = None
        mock_conn.commit.return_value = None
        
        result = delete_transportista(1)
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM transportistas WHERE id_transportista = %s", (1,)
        )

if __name__ == '__main__':
    unittest.main()
