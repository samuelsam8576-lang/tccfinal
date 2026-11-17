"""Verifica a navegação da interface arquivada sem rede ou navegador."""
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class InterfaceTest(unittest.TestCase):
    def test_estacoes_e_variaveis_sem_consulta_ao_vivo(self):
        with patch('requests.Session.get', side_effect=AssertionError('Modo arquivado não deve consultar API')):
            app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run(timeout=30)
            self.assertFalse(app.exception)
            for codigo, n in [('EF24', '63'), ('EF25', '27'), ('EF26', '90')]:
                app.selectbox[0].set_value(codigo).run(timeout=30)
                self.assertFalse(app.exception)
                self.assertEqual(app.metric[0].value, n)
            app.selectbox[1].set_value('ph').run(timeout=30)
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, '88')
            app.selectbox[2].set_value('pm10').run(timeout=30)
            self.assertFalse(app.exception)
            self.assertTrue(any('não superou' in x.value for x in app.error))


if __name__ == '__main__':
    unittest.main()
