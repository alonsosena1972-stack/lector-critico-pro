import unittest

from core import calcular_puntaje, resultado_simulacro, validar_pregunta, valor_por_pregunta


class PuntuacionTests(unittest.TestCase):
    def test_veinte_preguntas_cada_una_vale_cinco(self):
        self.assertEqual(valor_por_pregunta(20), 5)
        self.assertEqual(calcular_puntaje(13, 20), 65)
        self.assertEqual(resultado_simulacro(13, 20)["estado"], "GANASTE")
        self.assertEqual(resultado_simulacro(12, 20)["estado"], "NO GANASTE")

    def test_maximo_siempre_es_cien(self):
        for total in (1, 5, 10, 20, 30, 50, 80, 100):
            self.assertEqual(calcular_puntaje(total, total), 100)

    def test_limite_de_aprobacion(self):
        self.assertTrue(resultado_simulacro(65, 100)["aprobado"])
        self.assertFalse(resultado_simulacro(64, 100)["aprobado"])
        self.assertTrue(resultado_simulacro(52, 80)["aprobado"])
        self.assertFalse(resultado_simulacro(51, 80)["aprobado"])

    def test_rechaza_totales_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_puntaje(0, 0)
        with self.assertRaises(ValueError):
            calcular_puntaje(21, 20)


class ValidacionTests(unittest.TestCase):
    def pregunta_valida(self):
        return {
            "contexto": " ".join(["Este es un contexto amplio para evaluar comprensión lectora y análisis crítico."] * 15),
            "enunciado": "¿Cuál interpretación está mejor sustentada por el contenido del texto presentado?",
            "opciones": {letra: " ".join([f"La opción {letra} presenta una interpretación razonable, pero no es la más sustentada por el texto."] * 4) for letra in "ABCD"},
            "respuesta": "B",
            "explicacion": "La opción B relaciona la información principal con la conclusión del texto y permite descartar las demás alternativas.",
            "complejidad": "Avanzada",
            "bloom": "Analizar",
            "soporte": {"fuente": "Texto base suministrado", "referencia": "Párrafos del material de estudio"},
        }

    def test_pregunta_valida(self):
        valida, errores = validar_pregunta(self.pregunta_valida())
        self.assertTrue(valida, errores)

    def test_pregunta_sin_soporte_es_rechazada(self):
        pregunta = self.pregunta_valida()
        pregunta["soporte"] = {}
        valida, errores = validar_pregunta(pregunta)
        self.assertFalse(valida)
        self.assertIn("Falta la fuente de soporte.", errores)


if __name__ == "__main__":
    unittest.main()
