nano tests/test_basic.py

import unittest
from biblocpal import Biblocpal

class TestBiblocpal(unittest.TestCase):
    def setUp(self):
        self.biblo = Biblocpal()

    def test_significado(self):
        self.assertIn("Saludo", self.biblo.obtener_significado("hola"))

    def test_respuesta_fija(self):
        self.assertEqual(self.biblo.obtener_respuesta_fija("hola"), "¡Hola! 😊 ¿Cómo estás?")

if __name__ == "__main__":
    unittest.main()
