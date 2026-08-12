# Lector Crítico CNSC — SÍ AL MÉRITO

Aplicación de entrenamiento para comprensión lectora, lectura crítica y juicio situacional orientada a concursos de carrera administrativa en Colombia.

## Alcance

- Ejes temáticos de carrera administrativa y tema libre.
- Simulacros de 1, 5, 10, 20, 30, 50, 80 y 100 preguntas.
- Cuatro opciones por pregunta: A, B, C y D.
- Textos complejos y opciones desarrolladas.
- Complejidad por reactivo y taxonomía de Bloom.
- Soporte de fuente, referencia y enlace por pregunta.
- Carga de material base en PDF, Word o TXT para fundamentar la generación.
- Puntaje máximo: 100 puntos.
- Aprobación del simulador: 65 puntos o más.
- Retroalimentación y descarga de PDF con páginas numeradas e identidad de SÍ AL MÉRITO.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para generación con IA, configurar `OPENAI_API_KEY` en `.streamlit/secrets.toml` o como variable de entorno.

Los PDF se organizan en `pdf_generados/` cuando el entorno permite escritura.

## Nota de uso

La aplicación es un simulador de entrenamiento. Las normas y fuentes deben verificarse en el documento oficial vigente de la convocatoria o entidad correspondiente antes de presentarse como información oficial.

© 2026 SÍ AL MÉRITO — Cesar Alonso Padilla. Todos los derechos reservados.
