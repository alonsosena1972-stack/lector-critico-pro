"""
Lector Crítico CNSC — SÍ AL MÉRITO
Motor de comprensión lectora, lectura crítica y juicio situacional para concursos.

Funciones principales:
- Comprensión lectora o lectura crítica.
- 1, 5, 10, 20, 30, 40, 50, 80 o 100 preguntas.
- Tema o eje temático libre.
- Texto base opcional para crear preguntas sobre un material entregado.
- Párrafos y opciones configurables por extensión.
- Generación por bloques para no perder el simulacro completo.
- Resultado, explicaciones y PDF descargable.

Para generar preguntas nuevas sobre cualquier tema se requiere OPENAI_API_KEY
configurada en Streamlit Secrets. Si la conexión no está configurada, la aplicación
muestra un aviso y no presenta preguntas de demostración.
"""

from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import streamlit as st

from core import PUNTAJE_MINIMO, calcular_puntaje, valor_por_pregunta

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
    )
except ImportError:
    colors = None


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS ACCESIBLES
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Lector Crítico CNSC | SÍ AL MÉRITO",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { color-scheme: light dark; }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background:
            radial-gradient(circle at 5% 0%, rgba(14, 165, 233, .13), transparent 28%),
            radial-gradient(circle at 95% 8%, rgba(16, 185, 129, .12), transparent 25%),
            var(--background-color, #f7fafc) !important;
        color: var(--text-color, #111827) !important;
    }

    header[data-testid="stHeader"] { background: transparent !important; }

    .block-container {
        max-width: 1280px;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102a43 0%, #0f766e 100%) !important;
        border-right: 3px solid #f4b942 !important;
    }

    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p { font-size: 1.05rem !important; }

    h1, h2, h3, h4, h5, h6,
    p, label, [data-testid="stMarkdownContainer"] {
        color: var(--text-color, #111827) !important;
    }

    .brand-title {
        text-align: center;
        color: #047857 !important;
        font-family: Inter, Arial, sans-serif;
        font-size: clamp(2.4rem, 6vw, 4.5rem) !important;
        line-height: 1.05 !important;
        font-weight: 900 !important;
        letter-spacing: -1px;
        margin: .3rem 0 .5rem 0;
        text-shadow: 0 3px 18px rgba(4, 120, 87, .2);
    }

    .brand-subtitle {
        text-align: center;
        color: #075985 !important;
        font-size: clamp(1.15rem, 2.4vw, 1.55rem) !important;
        line-height: 1.45 !important;
        font-weight: 800;
        max-width: 1050px;
        margin: 0 auto 1rem auto;
    }

    .hero-strip {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        max-width: 1120px;
        margin: 0 auto 2rem auto;
        padding: 1rem 1.2rem;
        border-radius: 16px;
        color: #ffffff !important;
        background: linear-gradient(90deg, #0f766e 0%, #0369a1 55%, #b45309 100%);
        font-size: 1.12rem;
        font-weight: 900;
        text-align: center;
        box-shadow: 0 10px 25px rgba(3, 105, 161, .22);
    }

    .config-card,
    .reading-card,
    .result-card {
        background-color: var(--secondary-background-color, #ffffff) !important;
        border: 2px solid #0f766e !important;
        border-radius: 18px;
        padding: 1.5rem 1.7rem;
        margin: 1rem 0;
        box-shadow: 0 10px 28px rgba(15, 118, 110, .14);
    }

    .reading-card {
        border-left: 8px solid #0369a1 !important;
        font-size: 1.2rem;
        line-height: 1.75;
    }

    .reading-label {
        color: #075985 !important;
        font-weight: 900;
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: .03em;
        margin-bottom: .5rem;
    }

    .question-title {
        color: #047857 !important;
        font-size: 1.35rem !important;
        font-weight: 900 !important;
        line-height: 1.45 !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div,
    [data-testid="stChatInput"] textarea {
        background-color: var(--background-color, #ffffff) !important;
        color: var(--text-color, #111827) !important;
        border: 2px solid #0f766e !important;
        border-radius: 10px !important;
        min-height: 3.2rem !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] input,
    [data-testid="stChatInput"] textarea {
        color: var(--text-color, #111827) !important;
        -webkit-text-fill-color: var(--text-color, #111827) !important;
        font-size: 1.12rem !important;
        line-height: 1.55 !important;
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stCheckbox"] label {
        font-size: 1.08rem !important;
        font-weight: 800 !important;
        line-height: 1.45 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: var(--secondary-background-color, #ffffff) !important;
        color: var(--text-color, #111827) !important;
    }

    div[data-baseweb="menu"] li { color: var(--text-color, #111827) !important; }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, #047857 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-size: 1.08rem !important;
        font-weight: 900 !important;
        min-height: 3.25rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: .8rem 1.4rem;
        box-shadow: 0 6px 16px rgba(4, 120, 87, .28);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        opacity: .9;
        transform: translateY(-1px);
    }

    [data-testid="stAlert"] {
        font-size: 1.08rem !important;
        line-height: 1.55 !important;
        border-radius: 12px !important;
    }

    [data-testid="stCaptionContainer"] { font-size: 1rem !important; }

    .footer-box {
        background-color: var(--secondary-background-color, #ffffff) !important;
        color: var(--text-color, #111827) !important;
        padding: 1.5rem;
        border-top: 4px solid #f4b942;
        border-radius: 14px;
        text-align: center;
        margin-top: 3rem;
        font-size: 1rem;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# CONSTANTES Y SECRETOS
# -----------------------------------------------------------------------------
CORREO_EMPRESA = "si.al.merito2026@gmail.com"
WHATSAPP = "3146715497 - 3153838792 - 3004417737"
ENLACE_CNSC = "https://www.cnsc.gov.co"
ENLACE_SIMO = "https://simo.cnsc.gov.co"
ENLACE_JITSI = "https://meet.jit.si/SiAlMeritoSesionGarantizada2026Oficial"

CANTIDADES = [1, 5, 10, 20, 30, 50, 80, 100]
BLOQUE_GENERACION = 10
NIVELES_COMPLEJIDAD = [
    "Mixta (progresiva)",
    "Básica",
    "Intermedia",
    "Avanzada",
    "Experta",
]
NIVELES_BLOOM = [
    "Comprender",
    "Aplicar",
    "Analizar",
    "Evaluar",
    "Inferir",
]
EJES_CARRERA_ADMINISTRATIVA = [
    "Todos los ejes / tema libre",
    "Constitución y derechos fundamentales",
    "Organización del Estado y función pública",
    "Administración y gestión pública",
    "Planeación y gestión institucional",
    "Servicio al ciudadano y derecho de petición",
    "Transparencia, participación y control social",
    "Ética, integridad y lucha contra la corrupción",
    "Régimen disciplinario y responsabilidad del servidor público",
    "Contratación estatal",
    "Presupuesto y finanzas públicas",
    "Control interno y gestión del riesgo",
    "Talento humano y competencias comportamentales",
    "Gestión documental y archivo",
    "Gobierno digital y seguridad de la información",
    "Enfoque diferencial, inclusión y derechos humanos",
    "Gestión ambiental y desarrollo sostenible",
    "Juicio situacional aplicado al servicio público",
]

# La prueba siempre se califica sobre 100 puntos.


def extraer_texto_archivo(archivo: Any) -> tuple[str, str]:
    """Extrae texto de PDF, DOCX o TXT y devuelve texto + nombre de fuente."""
    if archivo is None:
        return "", ""
    nombre = str(getattr(archivo, "name", "material_subido"))
    extension = Path(nombre).suffix.lower()
    try:
        contenido = archivo.getvalue()
        if extension == ".pdf":
            if PdfReader is None:
                raise RuntimeError("Falta instalar pypdf para leer PDF.")
            lector = PdfReader(BytesIO(contenido))
            texto = "\n".join((pagina.extract_text() or "") for pagina in lector.pages)
        elif extension == ".docx":
            if Document is None:
                raise RuntimeError("Falta instalar python-docx para leer Word.")
            documento = Document(BytesIO(contenido))
            texto = "\n".join(parrafo.text for parrafo in documento.paragraphs)
        else:
            texto = contenido.decode("utf-8", errors="replace")
        return texto.strip(), nombre
    except Exception as error:
        raise RuntimeError(f"No fue posible leer {nombre}.") from error


def leer_secret(nombre: str, defecto: str = "") -> str:
    try:
        valor = st.secrets.get(nombre, None)
    except Exception:
        valor = None
    if valor is None:
        valor = os.getenv(nombre, defecto)
    return str(valor).strip() if valor is not None else ""


OPENAI_API_KEY = leer_secret("OPENAI_API_KEY")
OPENAI_MODEL = leer_secret("OPENAI_MODEL", "gpt-4o")
CLIENTE_OPENAI = None
if OPENAI_API_KEY and OpenAI is not None:
    try:
        CLIENTE_OPENAI = OpenAI(api_key=OPENAI_API_KEY, timeout=60.0, max_retries=2)
    except Exception:
        CLIENTE_OPENAI = None


# -----------------------------------------------------------------------------
# BANCO LOCAL HISTÓRICO (NO SE USA COMO FALLBACK)
# -----------------------------------------------------------------------------
# Se conserva como referencia del banco original, pero el simulador profesional
# solo muestra preguntas cuando la conexión con OpenAI está activa. Así no se
# presentan cuatro reactivos como si fueran un simulacro completo.
BANCO_LOCAL = [
    {
        "modo": "Comprensión lectora",
        "tema": "Función pública",
        "eje": "Textos normativos y administrativos",
        "perfil": "Todos los perfiles",
        "contexto": (
            "El servicio público exige que las decisiones administrativas se orienten "
            "al interés general y respeten los principios de igualdad, imparcialidad, "
            "eficacia, economía, celeridad, publicidad y moralidad. El cumplimiento "
            "formal de un trámite no basta si la actuación termina favoreciendo un "
            "interés particular o desconoce los derechos de los ciudadanos. Por ello, "
            "la gestión pública debe relacionar los procedimientos con los resultados "
            "que producen en la comunidad."
        ),
        "enunciado": "De acuerdo con el texto, la actuación administrativa debe principalmente:",
        "opciones": {
            "A": "Cumplir trámites sin considerar los efectos que producen en la ciudadanía.",
            "B": "Orientar sus decisiones al interés general y a resultados que beneficien a la comunidad.",
            "C": "Priorizar siempre la conveniencia de los funcionarios encargados del procedimiento.",
            "D": "Evitar cualquier control ciudadano para acelerar la gestión institucional.",
        },
        "respuesta": "B",
        "explicacion": "El texto relaciona los procedimientos con sus resultados y exige que la actuación se oriente al interés general.",
        "habilidad": "Idea principal",
    },
    {
        "modo": "Lectura crítica",
        "tema": "Gestión pública",
        "eje": "Argumentación",
        "perfil": "Todos los perfiles",
        "contexto": (
            "Una entidad puede ejecutar la totalidad de su presupuesto y, aun así, no "
            "resolver el problema que motivó la inversión. La ejecución financiera es "
            "un dato importante, pero no demuestra por sí sola que exista valor público. "
            "Para evaluar la gestión se requiere observar si los productos y servicios "
            "entregados modificaron positivamente la situación de la población. Esta "
            "perspectiva desplaza la atención exclusiva de los medios hacia los efectos "
            "y resultados de la acción estatal."
        ),
        "enunciado": "La tesis central del texto es que la evaluación de una entidad debe:",
        "opciones": {
            "A": "Medir únicamente el porcentaje de presupuesto ejecutado durante el año.",
            "B": "Eliminar los indicadores financieros porque carecen de utilidad pública.",
            "C": "Relacionar los recursos ejecutados con los productos y efectos logrados en la población.",
            "D": "Delegar la evaluación completa en los funcionarios responsables del gasto.",
        },
        "respuesta": "C",
        "explicacion": "El texto no elimina el indicador financiero; afirma que debe complementarse con el análisis de productos, efectos y resultados.",
        "habilidad": "Tesis y evaluación de argumentos",
    },
    {
        "modo": "Comprensión lectora",
        "tema": "Debido proceso",
        "eje": "Derechos fundamentales",
        "perfil": "Todos los perfiles",
        "contexto": (
            "El debido proceso protege a las personas frente a decisiones arbitrarias de "
            "las autoridades. En una actuación administrativa, la entidad debe informar "
            "los motivos de su decisión, permitir que el interesado conozca las pruebas, "
            "ofrecer oportunidades de defensa y aplicar las reglas previamente establecidas. "
            "La existencia de una finalidad legítima no autoriza a la administración a "
            "omitir las garantías que permiten controvertir una decisión."
        ),
        "enunciado": "Según el texto, el debido proceso cumple la función de:",
        "opciones": {
            "A": "Impedir que las autoridades adopten cualquier decisión administrativa.",
            "B": "Garantizar que las decisiones tengan razones, reglas y oportunidades de defensa.",
            "C": "Sustituir las normas vigentes por la opinión del interesado.",
            "D": "Acelerar todos los trámites aunque se reduzcan las posibilidades de contradicción.",
        },
        "respuesta": "B",
        "explicacion": "El texto destaca información, reglas, pruebas y defensa como garantías contra la arbitrariedad.",
        "habilidad": "Inferencia directa",
    },
    {
        "modo": "Lectura crítica",
        "tema": "Ética pública",
        "eje": "Análisis de argumentos",
        "perfil": "Todos los perfiles",
        "contexto": (
            "La legalidad es una condición indispensable de la función pública, pero no "
            "agota el concepto de integridad. Una decisión puede ajustarse aparentemente "
            "a una regla y, sin embargo, utilizar el poder institucional para beneficiar "
            "indebidamente a una persona o grupo. La integridad exige examinar también la "
            "finalidad de la decisión, sus efectos sobre la igualdad y la transparencia "
            "del proceso mediante el cual fue adoptada."
        ),
        "enunciado": "¿Qué relación establece el texto entre legalidad e integridad?",
        "opciones": {
            "A": "Son conceptos idénticos, por lo que basta cumplir una regla para demostrar integridad.",
            "B": "La integridad reemplaza completamente la obligación de cumplir las normas.",
            "C": "La legalidad es necesaria, pero la integridad también examina la finalidad y los efectos de la decisión.",
            "D": "La integridad solo puede ser evaluada por la persona que tomó la decisión.",
        },
        "respuesta": "C",
        "explicacion": "El texto afirma que la legalidad es indispensable, pero que la integridad exige revisar finalidad, igualdad, transparencia y efectos.",
        "habilidad": "Relación entre conceptos",
    },
]


# -----------------------------------------------------------------------------
# FUNCIONES DE GENERACIÓN Y VALIDACIÓN
# -----------------------------------------------------------------------------
def limpiar_json(texto: str) -> str:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*", "", texto)
        texto = re.sub(r"\s*```$", "", texto)
    return texto.strip()


def normalizar_pregunta(item: dict[str, Any], numero: int) -> dict[str, Any] | None:
    """Valida estructura, dificultad, extensión y soporte de cada reactivo."""
    if not isinstance(item, dict):
        return None
    contexto = str(item.get("contexto", "")).strip()
    enunciado = str(item.get("enunciado", "")).strip()
    explicacion = str(item.get("explicacion", "")).strip()
    habilidad = str(item.get("habilidad", "")).strip() or "Análisis de lectura"
    complejidad = str(item.get("complejidad", "Intermedia")).strip()
    bloom = str(item.get("bloom", "Analizar")).strip()
    tipo_ejercicio = str(item.get("tipo_ejercicio", "Lectura crítica")).strip()
    opciones = item.get("opciones", {})
    respuesta = str(item.get("respuesta", "")).strip().upper()
    soporte = item.get("soporte", {})
    if not isinstance(soporte, dict):
        soporte = {}
    fuente = str(soporte.get("fuente", "")).strip()
    referencia = str(soporte.get("referencia", "")).strip()
    enlace = str(soporte.get("enlace", "")).strip()

    if not isinstance(opciones, dict):
        return None
    opciones_limpias = {
        letra: str(opciones.get(letra, "")).strip()
        for letra in ("A", "B", "C", "D")
    }
    palabras_contexto = len(contexto.split())
    palabras_opciones = [len(opciones_limpias[x].split()) for x in opciones_limpias]
    if (
        palabras_contexto < 75
        or len(enunciado) < 20
        or len(explicacion) < 35
        or any(palabras < 22 for palabras in palabras_opciones)
        or respuesta not in opciones_limpias
        or complejidad not in NIVELES_COMPLEJIDAD[1:]
        or bloom not in NIVELES_BLOOM
        or not fuente
        or not referencia
    ):
        return None

    return {
        "id": numero,
        "contexto": contexto,
        "enunciado": enunciado,
        "opciones": opciones_limpias,
        "respuesta": respuesta,
        "explicacion": explicacion,
        "habilidad": habilidad,
        "complejidad": complejidad,
        "bloom": bloom,
        "tipo_ejercicio": tipo_ejercicio,
        "soporte": {
            "fuente": fuente,
            "referencia": referencia,
            "enlace": enlace,
        },
    }


def instrucciones_generacion(config: dict[str, Any], cantidad: int) -> str:
    texto_base = config["texto_base"].strip()
    base = (
        "Usa exclusivamente el siguiente texto base para formular las preguntas:\n"
        + texto_base
        if texto_base
        else "Construye un texto original y autosuficiente relacionado con el tema indicado."
    )
    return f"""
Crea {cantidad} reactivos de alta calidad para un simulacro colombiano de
{config['modo']} orientado a concursos de carrera administrativa.

Tema o eje: {config['tema'] or config['eje']}.
Perfil: {config['perfil']}.
Dificultad solicitada: {config['complejidad']}.
Extensión del texto: {config['extension']}.
Extensión de las opciones: {config['opciones_extension']}.
Tipo de ejercicio: {config['tipo_ejercicio']}.
Fuente base indicada por el usuario: {config['fuente_oficial'] or 'material temático general; no inventes una norma'}.

{base}

Cada reactivo debe ser independiente, complejo y no repetirse. Devuelve esta estructura:
{{
  "contexto": "Texto o caso de 8 a 10 líneas visuales, aproximadamente 100 a 160 palabras",
  "enunciado": "Pregunta clara y exigente",
  "opciones": {{"A": "Párrafo de mínimo 3 líneas", "B": "Párrafo de mínimo 3 líneas", "C": "Párrafo de mínimo 3 líneas", "D": "Párrafo de mínimo 3 líneas"}},
  "respuesta": "A",
  "explicacion": "Fundamenta la respuesta y explica por qué las otras tres se descartan",
  "habilidad": "idea principal, inferencia, propósito, tono, argumento, relación o evaluación",
  "complejidad": "Básica, Intermedia, Avanzada o Experta",
  "bloom": "Comprender, Aplicar, Analizar, Evaluar o Inferir",
  "tipo_ejercicio": "Comprensión lectora, Lectura crítica o Juicio situacional",
  "soporte": {{"fuente": "nombre de la norma, guía, texto o material", "referencia": "artículo, capítulo, apartado o explicación de origen", "enlace": "URL oficial si existe"}}
}}

REGLAS OBLIGATORIAS:
- Devuelve únicamente un objeto JSON con la clave "preguntas" y una lista.
- Siempre produce exactamente cuatro opciones A, B, C y D.
- El contexto debe tener mínimo 75 palabras y preferiblemente 100 a 160 palabras.
- Cada opción debe tener mínimo 22 palabras y extensión parecida a las demás.
- Solo una opción puede ser correcta; las otras deben ser plausibles pero incorrectas.
- No uses "todas las anteriores" ni "ninguna de las anteriores".
- No inventes citas, artículos, sentencias, fechas, vigencias o datos normativos.
- Si no se proporciona una norma concreta, no atribuyas artículos: usa como fuente el texto base o material temático y dilo claramente.
- Para temas jurídicos o administrativos, el soporte debe identificar la norma o guía de origen; no presentes una norma como vigente sin material que lo confirme.
- En juicio situacional, presenta un escenario laboral y opciones de actuación; evalúa la decisión más adecuada según el caso y su soporte.
- Para comprensión lectora prioriza información explícita, inferencias y vocabulario.
- Para lectura crítica prioriza tesis, argumentos, supuestos, tono, propósito, relación entre ideas y evaluación de evidencia.
- Aplica la taxonomía de Bloom y asigna la habilidad que realmente mide el reactivo.
""".strip()


def generar_bloque(config: dict[str, Any], cantidad: int) -> list[dict[str, Any]]:
    if CLIENTE_OPENAI is None:
        return []

    respuesta = CLIENTE_OPENAI.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un diseñador experto de evaluaciones de lectura en español. "
                    "Devuelve JSON válido, sin comentarios fuera del JSON."
                ),
            },
            {"role": "user", "content": instrucciones_generacion(config, cantidad)},
        ],
        response_format={"type": "json_object"},
        temperature=0.35,
        max_tokens=min(12000, max(2500, cantidad * 900)),
    )
    contenido = respuesta.choices[0].message.content or ""
    datos = json.loads(limpiar_json(contenido))
    lista = datos.get("preguntas", [])
    return [p for p in lista if isinstance(p, dict)]


def generar_preguntas(config: dict[str, Any], cantidad: int) -> tuple[list[dict], bool]:
    """Genera preguntas nuevas en lotes; no usa preguntas repetidas de respaldo."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY no está configurada en los Secrets de esta aplicación."
        )
    if OpenAI is None:
        raise RuntimeError(
            "La dependencia openai no está instalada. Revisa requirements.txt."
        )
    if CLIENTE_OPENAI is None:
        raise RuntimeError(
            "No se pudo iniciar la conexión con OpenAI. Revisa la clave y reinicia la aplicación."
        )

    preguntas: list[dict] = []
    huellas: set[str] = set()
    intentos = 0

    # Se permiten varios intentos, pero nunca se presenta un simulacro incompleto como terminado.
    while len(preguntas) < cantidad and intentos < 6:
        faltan = cantidad - len(preguntas)
        lote = min(BLOQUE_GENERACION, faltan)
        intentos += 1
        try:
            crudas = generar_bloque(config, lote)
        except Exception as error:
            if not preguntas:
                raise RuntimeError("No fue posible generar el primer bloque.") from error
            break

        for item in crudas:
            normalizada = normalizar_pregunta(item, len(preguntas) + 1)
            if normalizada is None:
                continue
            huella = re.sub(
                r"\s+", " ", normalizada["enunciado"].lower()
            )[:240]
            if huella in huellas:
                continue
            huellas.add(huella)
            normalizada["id"] = len(preguntas) + 1
            preguntas.append(normalizada)
            if len(preguntas) >= cantidad:
                break

    return preguntas[:cantidad], True


# -----------------------------------------------------------------------------
# PDF Y ARCHIVOS DEL PROYECTO
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / "pdf_generados"
PDF_DIR.mkdir(parents=True, exist_ok=True)


def guardar_pdf_en_proyecto(pdf_bytes: bytes, config: dict[str, Any]) -> Path | None:
    """Guarda una copia organizada; el botón de descarga también la entrega al usuario."""
    try:
        sello = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = re.sub(r"[^a-zA-Z0-9_-]+", "_", config.get("eje", "simulacro"))[:45]
        ruta = PDF_DIR / f"simulacro_{nombre}_{sello}.pdf"
        ruta.write_bytes(pdf_bytes)
        return ruta
    except Exception:
        return None


def seguro_pdf(texto: Any) -> str:
    return html.escape(str(texto or "")).replace("\n", "<br/>")


def generar_pdf(preguntas: list[dict], config: dict[str, Any]) -> bytes:
    if colors is None:
        raise RuntimeError("Falta instalar reportlab.")

    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Lector Crítico Pro - SÍ AL MÉRITO",
        author="SÍ AL MÉRITO",
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#075985"),
        alignment=TA_CENTER,
        spaceAfter=5,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    meta = ParagraphStyle(
        "Meta",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )
    contexto = ParagraphStyle(
        "Contexto",
        parent=estilos["Normal"],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )
    pregunta = ParagraphStyle(
        "Pregunta",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#075985"),
        spaceAfter=7,
    )
    opcion = ParagraphStyle(
        "Opcion",
        parent=estilos["Normal"],
        fontSize=10,
        leading=14,
        leftIndent=12,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5,
    )
    explicacion = ParagraphStyle(
        "Explicacion",
        parent=estilos["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#047857"),
        spaceAfter=12,
    )

    elementos = [
        Paragraph("SÍ AL MÉRITO - LECTOR CRÍTICO PRO", titulo),
        Paragraph(
            f"{seguro_pdf(config['modo'])} | {seguro_pdf(config['tema'] or config['eje'])} | "
            f"{len(preguntas)} preguntas | {datetime.now().strftime('%d/%m/%Y')}",
            subtitulo,
        ),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f766e"), spaceAfter=12),
        Paragraph(
            f"<b>Perfil:</b> {seguro_pdf(config['perfil'])} &nbsp;&nbsp; "
            f"<b>Eje:</b> {seguro_pdf(config['eje'])}",
            meta,
        ),
    ]

    for idx, item in enumerate(preguntas, 1):
        soporte = item.get("soporte", {})
        elementos.extend(
            [
                Paragraph(
                    f"Pregunta {idx} — {seguro_pdf(item.get('habilidad'))} | "
                    f"Complejidad: {seguro_pdf(item.get('complejidad', 'Intermedia'))} | "
                    f"Bloom: {seguro_pdf(item.get('bloom', 'Analizar'))}",
                    pregunta,
                ),
                Paragraph(f"<b>Texto:</b> {seguro_pdf(item['contexto'])}", contexto),
                Paragraph(f"<b>Enunciado:</b> {seguro_pdf(item['enunciado'])}", pregunta),
            ]
        )
        for letra in ("A", "B", "C", "D"):
            elementos.append(
                Paragraph(
                    f"<b>{letra})</b> {seguro_pdf(item['opciones'][letra])}",
                    opcion,
                )
            )
        elementos.append(Spacer(1, 5))
        elementos.append(HRFlowable(width="100%", thickness=.5, color=colors.HexColor("#cbd5e1"), spaceAfter=12))

    elementos.append(PageBreak())
    elementos.append(Paragraph("Clave y retroalimentación", titulo))
    for idx, item in enumerate(preguntas, 1):
        soporte = item.get("soporte", {})
        elementos.append(
            Paragraph(
                f"<b>{idx}. Respuesta correcta: {item['respuesta']}</b><br/>"
                f"<b>Complejidad:</b> {seguro_pdf(item.get('complejidad', 'Intermedia'))} · "
                f"<b>Bloom:</b> {seguro_pdf(item.get('bloom', 'Analizar'))}<br/>"
                f"{seguro_pdf(item['explicacion'])}<br/>"
                f"<b>Soporte:</b> {seguro_pdf(soporte.get('fuente', 'No informado'))} — "
                f"{seguro_pdf(soporte.get('referencia', ''))}",
                explicacion,
            )
        )

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(16 * mm, 9 * mm, "© 2026 SÍ AL MÉRITO — Cesar Alonso Padilla")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    documento.build(elementos, onFirstPage=pie, onLaterPages=pie)
    return salida.getvalue()


# -----------------------------------------------------------------------------
# ENCABEZADO
# -----------------------------------------------------------------------------
st.markdown("<div class='brand-title'>SÍ AL MÉRITO</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='brand-subtitle'>Lector Crítico CNSC · Comprensión lectora, lectura crítica y juicio situacional</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='hero-strip'>📚 Textos más completos · 🧠 Preguntas de alto nivel · 🎯 Preparación por eje temático</div>",
    unsafe_allow_html=True,
)

if CLIENTE_OPENAI is not None:
    st.success("✅ Generador de preguntas con IA conectado y listo.")
else:
    st.warning(
        "⚠️ Generador de IA no conectado. Configura OPENAI_API_KEY en Secrets; "
        "la aplicación no usará preguntas de demostración."
    )


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DEL SIMULACRO
# -----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("## ⚙️ Configura tu simulacro")
    st.caption("Puedes generar desde 1 hasta 100 preguntas. Para cantidades grandes se trabaja por bloques.")

    with st.form("configuracion_simulacro"):
        col1, col2 = st.columns(2)
        with col1:
            modo = st.selectbox(
                "Tipo de evaluación:",
                ["Comprensión lectora", "Lectura crítica"],
            )
            tipo_ejercicio = st.selectbox(
                "Tipo de ejercicio:",
                ["Mixto", "Comprensión lectora", "Lectura crítica", "Juicio situacional"],
            )
            perfil = st.selectbox(
                "Perfil del aspirante:",
                ["Todos los perfiles", "Bachiller", "Técnico", "Tecnólogo", "Profesional", "Directivo"],
            )
            cantidad = st.selectbox(
                "Número de preguntas:",
                CANTIDADES,
                index=CANTIDADES.index(10),
            )
            complejidad = st.selectbox("Complejidad:", NIVELES_COMPLEJIDAD, index=0)
        with col2:
            eje_catalogo = st.selectbox("Eje temático de carrera administrativa:", EJES_CARRERA_ADMINISTRATIVA)
            eje_libre = st.text_input(
                "Eje o subtema personalizado (opcional):",
                placeholder="Ejemplo: Ley 1437, servicio al ciudadano, archivo, contratación...",
            )
            extension = st.selectbox(
                "Extensión de los textos:",
                [
                    "Compleja: 8 a 10 líneas (100 a 160 palabras)",
                    "Profunda: 12 a 16 líneas (170 a 260 palabras)",
                    "Avanzada: 17 a 25 líneas (270 a 400 palabras)",
                ],
                index=0,
            )
            opciones_extension = st.selectbox(
                "Extensión mínima de las opciones:",
                [
                    "Desarrolladas: mínimo 3 líneas (22 a 40 palabras)",
                    "Amplias: 4 a 6 líneas (41 a 70 palabras)",
                ],
                index=0,
            )

        fuente_oficial = st.text_input(
            "Fuente oficial o norma base (opcional):",
            placeholder="Ejemplo: Ley 1437 de 2011, artículo 14; guía oficial de la convocatoria; documento suministrado.",
        )
        texto_base = st.text_area(
            "Texto, documento o material base (opcional):",
            placeholder="Pega aquí el material de estudio. La IA deberá fundamentar las respuestas en este contenido.",
            height=170,
        )
        archivo_base = st.file_uploader(
            "O carga un PDF, Word o TXT de estudio:",
            type=["pdf", "docx", "txt"],
            help="El contenido cargado se incorpora como material base para las preguntas y su soporte.",
        )
        iniciar = st.form_submit_button(
            "🚀 Generar simulacro",
            use_container_width=True,
        )

if iniciar:
    eje = eje_libre.strip()
    if not eje and eje_catalogo != "Todos los ejes / tema libre":
        eje = eje_catalogo
    try:
        texto_archivo, nombre_archivo = extraer_texto_archivo(archivo_base)
    except RuntimeError as error:
        texto_archivo, nombre_archivo = "", ""
        st.error(str(error))
    texto_completo = "\n\n".join(part for part in (texto_base.strip(), texto_archivo) if part).strip()
    fuente_final = fuente_oficial.strip() or nombre_archivo
    if not eje and not texto_completo:
        st.warning("Selecciona un eje, escribe un subtema o carga/pega un material base.")
    else:
        config = {
            "modo": modo,
            "tipo_ejercicio": tipo_ejercicio,
            "perfil": perfil,
            "cantidad": cantidad,
            "eje": eje or "Tema del texto base",
            "tema": eje,
            "complejidad": complejidad,
            "extension": extension,
            "opciones_extension": opciones_extension,
            "fuente_oficial": fuente_final,
            "texto_base": texto_completo,
        }
        error_generacion = ""
        with st.spinner(f"Construyendo {cantidad} preguntas en bloques de {BLOQUE_GENERACION}..."):
            try:
                preguntas, uso_ia = generar_preguntas(config, cantidad)
            except RuntimeError as error:
                preguntas, uso_ia = [], False
                error_generacion = str(error)

        if len(preguntas) == cantidad:
            st.session_state["preguntas"] = preguntas
            st.session_state["config"] = config
            st.session_state["uso_ia"] = uso_ia
            st.session_state["finalizado"] = False
            st.session_state["respuestas"] = {}
            st.rerun()
        else:
            st.error(
                error_generacion
                or (
                    f"La IA solo validó {len(preguntas)} de {cantidad} preguntas. "
                    "No se mostrará un simulacro incompleto. Reduce la cantidad, "
                    "aporta un texto base o vuelve a intentarlo."
                )
            )


# -----------------------------------------------------------------------------
# SIMULACRO
# -----------------------------------------------------------------------------
preguntas_actuales = st.session_state.get("preguntas", [])
config_actual = st.session_state.get("config", {})

if preguntas_actuales:
    st.divider()
    st.markdown("## 📝 Simulacro en curso")
    st.info(
        f"**{config_actual.get('modo', '')}** · "
        f"**Tema:** {config_actual.get('eje', '')} · "
        f"**Preguntas:** {len(preguntas_actuales)}"
    )

    respondidas = 0
    for idx, item in enumerate(preguntas_actuales, 1):
        key = f"respuesta_{item.get('id', idx)}_{idx}"
        if st.session_state.get(key):
            respondidas += 1

    st.progress(respondidas / len(preguntas_actuales), text=f"Respondidas: {respondidas} de {len(preguntas_actuales)}")

    for idx, item in enumerate(preguntas_actuales, 1):
        key = f"respuesta_{item.get('id', idx)}_{idx}"
        with st.expander(
            f"Pregunta {idx} · {item.get('habilidad', 'Análisis de lectura')} · "
            f"{item.get('complejidad', 'Intermedia')} · Bloom: {item.get('bloom', 'Analizar')}",
            expanded=(idx == 1),
        ):
            contexto_seguro = html.escape(item["contexto"]).replace("\n", "<br>")
            enunciado_seguro = html.escape(item["enunciado"]).replace("\n", "<br>")
            st.markdown("<div class='reading-label'>Texto de lectura</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='reading-card'>{contexto_seguro}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='question-title'>{enunciado_seguro}</div>", unsafe_allow_html=True)

            seleccion = st.radio(
                "Selecciona una respuesta:",
                options=["A", "B", "C", "D"],
                format_func=lambda letra, opciones=item["opciones"]: f"{letra}) {opciones[letra]}",
                key=key,
                index=None,
            )
            if seleccion:
                st.session_state["respuestas"][key] = seleccion

    col_a, col_b = st.columns(2)
    with col_a:
        finalizar = st.button("✅ Finalizar y ver resultados", use_container_width=True)
    with col_b:
        reiniciar = st.button("🔄 Crear otro simulacro", use_container_width=True)

    if reiniciar:
        st.session_state.pop("preguntas", None)
        st.session_state.pop("config", None)
        st.session_state["finalizado"] = False
        st.rerun()

    if finalizar:
        st.session_state["finalizado"] = True

    if st.session_state.get("finalizado"):
        total = len(preguntas_actuales)
        aciertos = 0
        respondidas_final = 0
        for idx, item in enumerate(preguntas_actuales, 1):
            key = f"respuesta_{item.get('id', idx)}_{idx}"
            elegida = st.session_state.get(key)
            if elegida:
                respondidas_final += 1
                if elegida == item["respuesta"]:
                    aciertos += 1

        puntaje = calcular_puntaje(aciertos, total) if total else 0
        puntaje_texto = f"{puntaje:.2f}".rstrip("0").rstrip(".")
        aprobado = puntaje >= PUNTAJE_MINIMO
        st.markdown("## 📊 Resultado del simulacro")
        r1, r2, r3 = st.columns(3)
        r1.metric("Aciertos", f"{aciertos} / {total}")
        r2.metric("Puntaje", f"{puntaje_texto} / 100")
        r3.metric("Sin responder", str(total - respondidas_final))
        st.caption(f"Cada acierto vale {valor_por_pregunta(total):.2f} puntos. Mínimo para ganar: {PUNTAJE_MINIMO}/100.")

        if aprobado:
            st.success(f"🎉 ¡GANASTE! Obtuviste {puntaje_texto}/100 puntos.")
        else:
            st.error(f"❌ NO GANASTE. Obtuviste {puntaje_texto}/100; necesitas mínimo {PUNTAJE_MINIMO}.")

        if puntaje >= 80:
            st.info("Excelente desempeño. Mantén el entrenamiento con textos de mayor complejidad.")
        elif aprobado:
            st.info("Aprobaste. Revisa las explicaciones para seguir fortaleciendo tus habilidades.")
        else:
            st.info("Este resultado es un diagnóstico. Repasa los textos y vuelve a practicar con otro eje.")

        st.markdown("### Retroalimentación")
        for idx, item in enumerate(preguntas_actuales, 1):
            key = f"respuesta_{item.get('id', idx)}_{idx}"
            elegida = st.session_state.get(key, "Sin responder")
            estado = "✅" if elegida == item["respuesta"] else "❌"
            with st.expander(f"{estado} Pregunta {idx} — respuesta correcta: {item['respuesta']}"):
                st.write(f"Tu respuesta: **{elegida}**")
                st.write(f"**Explicación:** {item['explicacion']}")

    st.markdown("### 📥 Descargar taller en PDF")
    if colors is None:
        st.warning("Instala reportlab para habilitar la descarga en PDF.")
    else:
        try:
            pdf_bytes = generar_pdf(preguntas_actuales, config_actual)
            ruta_pdf = guardar_pdf_en_proyecto(pdf_bytes, config_actual)
            st.download_button(
                "📄 Descargar cuadernillo PDF con clave y explicaciones",
                data=pdf_bytes,
                file_name=(
                    f"LectorCriticoCNSC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )
            if ruta_pdf:
                st.caption(f"Copia organizada en: pdf_generados/{ruta_pdf.name}")
        except Exception:
            st.error("No fue posible generar el PDF en este momento.")
else:
    st.info("Configura el tipo de evaluación, el tema y la cantidad de preguntas para comenzar.")


# -----------------------------------------------------------------------------
# PIE INSTITUCIONAL
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="footer-box">
        <strong>SÍ AL MÉRITO · Lector Crítico CNSC</strong><br>
        Comprensión lectora, lectura crítica y juicio situacional para concursos de carrera administrativa.<br>
        © 2026 SÍ AL MÉRITO — Cesar Alonso Padilla. Todos los derechos reservados.<br>
        Correo: {CORREO_EMPRESA} · WhatsApp: {WHATSAPP}<br>
        Fuentes oficiales para verificación: CNSC y SIMO.
    </div>
    """,
    unsafe_allow_html=True,
)
