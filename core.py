"""Reglas puras del Lector Crítico CNSC.

Este módulo no depende de Streamlit ni de la IA para poder probar las reglas
centrales del producto antes del despliegue.
"""

from __future__ import annotations

from typing import Any

PUNTAJE_MAXIMO = 100.0
PUNTAJE_MINIMO = 65.0
LETRAS = ("A", "B", "C", "D")
COMPLEJIDADES = ("Básica", "Intermedia", "Avanzada", "Experta")
BLOOM = ("Comprender", "Aplicar", "Analizar", "Evaluar", "Inferir")


def valor_por_pregunta(total: int) -> float:
    if total < 1:
        raise ValueError("El simulacro debe tener al menos una pregunta.")
    return PUNTAJE_MAXIMO / total


def calcular_puntaje(aciertos: int, total: int) -> float:
    if total < 1:
        raise ValueError("El total de preguntas debe ser mayor que cero.")
    if aciertos < 0 or aciertos > total:
        raise ValueError("Los aciertos deben estar entre cero y el total.")
    return aciertos * valor_por_pregunta(total)


def resultado_simulacro(aciertos: int, total: int) -> dict[str, Any]:
    puntaje = calcular_puntaje(aciertos, total)
    return {
        "aciertos": aciertos,
        "total": total,
        "valor_por_pregunta": valor_por_pregunta(total),
        "puntaje": puntaje,
        "aprobado": puntaje >= PUNTAJE_MINIMO,
        "estado": "GANASTE" if puntaje >= PUNTAJE_MINIMO else "NO GANASTE",
    }


def validar_pregunta(pregunta: dict[str, Any]) -> tuple[bool, list[str]]:
    """Valida la calidad mínima de un reactivo generado por IA."""
    errores: list[str] = []
    contexto = str(pregunta.get("contexto", "")).strip()
    enunciado = str(pregunta.get("enunciado", "")).strip()
    explicacion = str(pregunta.get("explicacion", "")).strip()
    opciones = pregunta.get("opciones", {})
    respuesta = str(pregunta.get("respuesta", "")).strip().upper()
    soporte = pregunta.get("soporte", {})

    if len(contexto.split()) < 75:
        errores.append("El contexto debe tener al menos 75 palabras.")
    if len(enunciado) < 20:
        errores.append("El enunciado es demasiado corto.")
    if not isinstance(opciones, dict) or set(opciones) != set(LETRAS):
        errores.append("Debe contener exactamente las opciones A, B, C y D.")
    else:
        for letra in LETRAS:
            if len(str(opciones[letra]).split()) < 22:
                errores.append(f"La opción {letra} debe tener al menos 22 palabras.")
    if respuesta not in LETRAS:
        errores.append("La respuesta correcta debe ser A, B, C o D.")
    if len(explicacion) < 35:
        errores.append("La explicación debe fundamentar la respuesta.")
    if pregunta.get("complejidad") not in COMPLEJIDADES:
        errores.append("La complejidad no corresponde a un nivel válido.")
    if pregunta.get("bloom") not in BLOOM:
        errores.append("El nivel de Bloom no corresponde a un nivel válido.")
    if not isinstance(soporte, dict) or not str(soporte.get("fuente", "")).strip():
        errores.append("Falta la fuente de soporte.")
    if not isinstance(soporte, dict) or not str(soporte.get("referencia", "")).strip():
        errores.append("Falta la referencia de soporte.")

    return not errores, errores
