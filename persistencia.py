"""Persistencia de «El Archivo Perdido».

- Partida: un único JSON (``datos/partida.json``) con jugador, inventario,
  sala actual e intentos.
- Tabla de puntajes: JSON (``datos/puntajes.json``) con una lista de registros.

Las escrituras son atómicas (archivo temporal + ``os.replace``) para que un
corte a mitad de guardado no deje el archivo corrupto. Todos los errores de
E/S o de formato se traducen a ``ErrorPersistencia`` para que ``juego.py``
pueda manejarlos sin que la partida se interrumpa.
"""

import json
import os
import tempfile
from datetime import datetime

DIR_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
RUTA_PARTIDA = os.path.join(DIR_DATOS, "partida.json")
RUTA_PUNTAJES = os.path.join(DIR_DATOS, "puntajes.json")

MAX_PUNTAJES = 10
CLAVES_FRAGMENTO = {"codigo": int, "titulo": str, "sala": str, "valor": int}


class ErrorPersistencia(Exception):
    """Fallo al leer, escribir o validar un archivo del juego."""


# ----------------------------------------------------------------- utilidades
def _es_entero(valor):
    # bool es subclase de int; se excluye explícitamente.
    return isinstance(valor, int) and not isinstance(valor, bool)


def _es_numero(valor):
    return (_es_entero(valor)) or isinstance(valor, float)


def _escribir_json(ruta, datos):
    carpeta = os.path.dirname(ruta) or "."
    tmp = None
    try:
        os.makedirs(carpeta, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=carpeta, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        os.replace(tmp, ruta)
    except (OSError, TypeError, ValueError) as error:
        if tmp is not None and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise ErrorPersistencia(f"No se pudo escribir '{ruta}': {error}") from error


def _leer_json(ruta):
    """Devuelve el contenido, o None si el archivo no existe."""
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as error:
        raise ErrorPersistencia(f"'{ruta}' está dañado (JSON inválido): {error}") from error
    except OSError as error:
        raise ErrorPersistencia(f"No se pudo leer '{ruta}': {error}") from error


# ------------------------------------------------------------------ validación
def validar_fragmento(fragmento):
    if not isinstance(fragmento, dict):
        raise ErrorPersistencia("Un fragmento del inventario no es un diccionario.")
    for clave, tipo in CLAVES_FRAGMENTO.items():
        if clave not in fragmento:
            raise ErrorPersistencia(f"Al fragmento le falta la clave '{clave}'.")
        valor = fragmento[clave]
        if tipo is int and not _es_entero(valor):
            raise ErrorPersistencia(f"'{clave}' del fragmento debe ser int.")
        if tipo is str and not isinstance(valor, str):
            raise ErrorPersistencia(f"'{clave}' del fragmento debe ser str.")


def validar_estado(estado):
    """Comprueba que el estado cargado tenga la forma esperada."""
    if not isinstance(estado, dict):
        raise ErrorPersistencia("El estado de la partida no es un objeto JSON.")
    for clave in ("jugador", "inventario", "sala_actual", "intentos"):
        if clave not in estado:
            raise ErrorPersistencia(f"Falta la clave '{clave}' en la partida.")

    jugador = estado["jugador"]
    if not isinstance(jugador, dict):
        raise ErrorPersistencia("'jugador' debe ser un objeto.")
    if not isinstance(jugador.get("nombre"), str) or not jugador["nombre"].strip():
        raise ErrorPersistencia("'nombre' del jugador inválido.")
    for clave in ("vida", "nivel"):
        if not _es_entero(jugador.get(clave)):
            raise ErrorPersistencia(f"'{clave}' del jugador debe ser int.")
    if not _es_numero(jugador.get("puntaje")):
        raise ErrorPersistencia("'puntaje' del jugador debe ser numérico.")
    if not isinstance(jugador.get("activo"), bool):
        raise ErrorPersistencia("'activo' del jugador debe ser bool.")

    if not isinstance(estado["inventario"], list):
        raise ErrorPersistencia("'inventario' debe ser una lista.")
    for fragmento in estado["inventario"]:
        validar_fragmento(fragmento)

    if not _es_entero(estado["sala_actual"]) or not 1 <= estado["sala_actual"] <= 6:
        raise ErrorPersistencia("'sala_actual' debe estar entre 1 y 6.")
    if not _es_entero(estado["intentos"]) or estado["intentos"] < 0:
        raise ErrorPersistencia("'intentos' debe ser un entero >= 0.")


# --------------------------------------------------------------------- partida
def guardar_partida(estado, ruta=RUTA_PARTIDA):
    """Guarda el estado completo de la partida en JSON."""
    validar_estado(estado)
    _escribir_json(ruta, estado)


def cargar_partida(ruta=RUTA_PARTIDA):
    """Carga y valida la partida. Devuelve None si no hay partida guardada."""
    estado = _leer_json(ruta)
    if estado is None:
        return None
    validar_estado(estado)
    return estado


def existe_partida(ruta=RUTA_PARTIDA):
    return os.path.isfile(ruta)


def eliminar_partida(ruta=RUTA_PARTIDA):
    """Borra la partida guardada (al terminar el juego). No falla si no existe."""
    try:
        os.remove(ruta)
    except FileNotFoundError:
        pass
    except OSError as error:
        raise ErrorPersistencia(f"No se pudo borrar '{ruta}': {error}") from error


# -------------------------------------------------------------------- puntajes
def cargar_puntajes(ruta=RUTA_PUNTAJES):
    """Devuelve la tabla de puntajes ordenada de mayor a menor ([] si no hay)."""
    datos = _leer_json(ruta)
    if datos is None:
        return []
    if not isinstance(datos, list):
        raise ErrorPersistencia("La tabla de puntajes debe ser una lista.")
    validos = []
    for registro in datos:
        if (
            isinstance(registro, dict)
            and isinstance(registro.get("nombre"), str)
            and _es_numero(registro.get("puntaje"))
        ):
            validos.append(registro)
    return sorted(validos, key=lambda r: r["puntaje"], reverse=True)


def registrar_puntaje(nombre, puntaje, fragmentos, intentos, ruta=RUTA_PUNTAJES):
    """Agrega un registro y conserva solo los MAX_PUNTAJES mejores."""
    tabla = cargar_puntajes(ruta)
    tabla.append(
        {
            "nombre": nombre,
            "puntaje": float(puntaje),
            "fragmentos": int(fragmentos),
            "intentos": int(intentos),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    tabla.sort(key=lambda r: r["puntaje"], reverse=True)
    tabla = tabla[:MAX_PUNTAJES]
    _escribir_json(ruta, tabla)
    return tabla
