"""
Lector Crítico Pro — SÍ AL MÉRITO
Versión profesional y accesible.

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
from typing import Any

import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

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
    page_title="Lector Crítico Pro | SÍ AL MÉRITO",
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

CANTIDADES = [1, 5, 10, 15, 20, 30, 40, 50, 80, 100]
BLOQUE_GENERACION = 10


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
    if not isinstance(item, dict):
        return None
    contexto = str(item.get("contexto", "")).strip()
    enunciado = str(item.get("enunciado", "")).strip()
    explicacion = str(item.get("explicacion", "")).strip()
    habilidad = str(item.get("habilidad", "")).strip() or "Análisis de lectura"
    opciones = item.get("opciones", {})
    respuesta = str(item.get("respuesta", "")).strip().upper()

    if not isinstance(opciones, dict):
        return None
    opciones_limpias = {
        letra: str(opciones.get(letra, "")).strip()
        for letra in ("A", "B", "C", "D")
    }
    if (
        min(len(contexto), len(enunciado), len(explicacion)) < 20
        or any(len(opciones_limpias[x]) < 5 for x in opciones_limpias)
        or respuesta not in opciones_limpias
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
{config['modo']}.

Tema o eje: {config['tema'] or config['eje']}.
Perfil: {config['perfil']}.
Extensión del texto: {config['extension']}.
Extensión de las opciones: {config['opciones_extension']}.

{base}

Cada reactivo debe ser independiente, no repetirse y tener esta estructura:
{{
  "contexto": "Párrafo de lectura",
  "enunciado": "Pregunta clara",
  "opciones": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
  "respuesta": "A",
  "explicacion": "Explica por qué la respuesta es correcta y por qué la lectura permite descartar las demás",
  "habilidad": "idea principal, inferencia, propósito, tono, argumento, relación o evaluación"
}}

REGLAS:
- Devuelve únicamente un objeto JSON con la clave "preguntas" y una lista.
- Las cuatro opciones deben tener extensión y estructura parecidas; evita pistas por longitud.
- Solo una opción puede ser correcta.
- No uses "todas las anteriores" ni "ninguna de las anteriores".
- No inventes citas, artículos, sentencias, fechas o datos normativos.
- Si se trata de un tema jurídico, formula el reactivo sobre el texto y no presentes
  como vigente una norma que no esté en el material proporcionado.
- Para comprensión lectora prioriza información explícita, inferencias y vocabulario.
- Para lectura crítica prioriza tesis, argumentos, supuestos, tono, propósito,
  relación entre ideas y evaluación de la evidencia.
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

    while len(preguntas) < cantidad and intentos < 3:
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
# PDF
# -----------------------------------------------------------------------------
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
        elementos.extend(
            [
                Paragraph(f"Pregunta {idx} — {seguro_pdf(item.get('habilidad'))}", pregunta),
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
        elementos.append(
            Paragraph(
                f"<b>{idx}. Respuesta correcta: {item['respuesta']}</b><br/>"
                f"{seguro_pdf(item['explicacion'])}",
                explicacion,
            )
        )

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(16 * mm, 9 * mm, "SÍ AL MÉRITO - Preparación para el empleo público")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    documento.build(elementos, onFirstPage=pie, onLaterPages=pie)
    return salida.getvalue()


# -----------------------------------------------------------------------------
# ENCABEZADO
# -----------------------------------------------------------------------------
st.markdown("<div class='brand-title'>SÍ AL MÉRITO</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='brand-subtitle'>Lector Crítico Pro · Comprensión lectora y lectura crítica para concursos públicos</div>",
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
            perfil = st.selectbox(
                "Perfil del aspirante:",
                ["Todos los perfiles", "Bachiller", "Técnico", "Profesional", "Directivo"],
            )
            cantidad = st.selectbox(
                "Número de preguntas:",
                CANTIDADES,
                index=CANTIDADES.index(10),
            )
        with col2:
            eje = st.text_input(
                "Eje temático o área:",
                placeholder="Ejemplo: ética pública, historia, salud, derecho, ambiente...",
            )
            extension = st.selectbox(
                "Extensión de los textos:",
                [
                    "Media: 250 a 400 palabras",
                    "Larga: 450 a 700 palabras",
                    "Muy larga: 700 a 1000 palabras",
                ],
                index=1,
            )
            opciones_extension = st.selectbox(
                "Extensión de las opciones:",
                [
                    "Claras: 15 a 30 palabras",
                    "Desarrolladas: 30 a 55 palabras",
                    "Amplias: 55 a 90 palabras",
                ],
                index=1,
            )

        texto_base = st.text_area(
            "Texto, documento o material base (opcional):",
            placeholder="Si lo dejas vacío, AlonsoBot creará los textos sobre el eje temático indicado.",
            height=150,
        )
        iniciar = st.form_submit_button(
            "🚀 Generar simulacro",
            use_container_width=True,
        )

if iniciar:
    if not eje.strip() and not texto_base.strip():
        st.warning("Escribe un eje temático o pega un texto base para generar el simulacro.")
    else:
        config = {
            "modo": modo,
            "perfil": perfil,
            "cantidad": cantidad,
            "eje": eje.strip() or "Tema del texto base",
            "tema": eje.strip(),
            "extension": extension,
            "opciones_extension": opciones_extension,
            "texto_base": texto_base.strip(),
        }
        error_generacion = ""
        with st.spinner(f"Construyendo {cantidad} preguntas en bloques de {BLOQUE_GENERACION}..."):
            try:
                preguntas, uso_ia = generar_preguntas(config, cantidad)
            except RuntimeError as error:
                preguntas, uso_ia = [], False
                error_generacion = str(error)

        if len(preguntas) < cantidad and preguntas:
            st.warning(
                f"Se generaron {len(preguntas)} preguntas válidas de {cantidad}. "
                "Puedes volver a intentarlo para completar el simulacro."
            )
        if preguntas:
            st.session_state["preguntas"] = preguntas
            st.session_state["config"] = config
            st.session_state["uso_ia"] = uso_ia
            st.session_state["finalizado"] = False
            st.session_state["respuestas"] = {}
            st.rerun()
        else:
            st.error(
                error_generacion
                or "No se pudo construir el simulacro. Revisa la configuración e inténtalo de nuevo."
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
            f"Pregunta {idx} · {item.get('habilidad', 'Análisis de lectura')}",
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

        porcentaje = (aciertos / total * 100) if total else 0
        st.markdown("## 📊 Resultado del simulacro")
        r1, r2, r3 = st.columns(3)
        r1.metric("Aciertos", f"{aciertos} / {total}")
        r2.metric("Porcentaje", f"{porcentaje:.1f}%")
        r3.metric("Sin responder", str(total - respondidas_final))

        if porcentaje >= 80:
            st.success("Excelente desempeño. Mantén el entrenamiento con textos de mayor complejidad.")
        elif porcentaje >= 60:
            st.warning("Buen avance. Revisa las explicaciones y fortalece los tipos de pregunta con más errores.")
        else:
            st.info("Este resultado es un punto de partida. Repasa los textos y vuelve a practicar con otro eje.")

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
            st.download_button(
                "📄 Descargar cuadernillo PDF con clave y explicaciones",
                data=pdf_bytes,
                file_name=(
                    f"LectorCritico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )
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
        <strong>SÍ AL MÉRITO · Lector Crítico Pro</strong><br>
        Comprensión lectora, lectura crítica y preparación para concursos de carrera administrativa.<br>
        Correo: {CORREO_EMPRESA} · WhatsApp: {WHATSAPP}<br>
        Fuentes oficiales para verificación: CNSC y SIMO.
    </div>
    """,
    unsafe_allow_html=True,
)
