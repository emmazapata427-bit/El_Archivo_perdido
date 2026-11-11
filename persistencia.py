"""Persistencia de «El Archivo Perdido».

- Partida: un único JSON (``datos/partida.json``) con jugador, inventario,
  sala actual e intentos.
- Tabla de puntajes: JSON (``datos/puntajes.json``) con una lista de registros.
- Fragmentos recolectados: JSON (``datos/recolectados.json``), que lee la Sala Central.

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
RUTA_RECOLECTADOS = os.path.join(DIR_DATOS, "recolectados.json")

MAX_PUNTAJES = 10
CLAVES_FRAGMENTO = {"codigo": int, "titulo": str, "sala": str, "valor": int}


class ErrorPersistencia(Exception):
    """Fallo al leer, escribir o validar un archivo del juego."""


# ----------------------------------------------------------------- utilidades
def _es_entero(valor):
    """Indica si un valor es int (excluyendo bool, que es subclase de int).

    Parámetros:
        valor: cualquier objeto.
    Retorna:
        bool: True si es un entero «real».
    """
    return isinstance(valor, int) and not isinstance(valor, bool)


def _es_numero(valor):
    """Indica si un valor es int o float (sin contar bool).

    Parámetros:
        valor: cualquier objeto.
    Retorna:
        bool: True si es numérico.
    """
    return (_es_entero(valor)) or isinstance(valor, float)


def _escribir_json(ruta, datos):
    """Escribe datos en JSON de forma atómica (archivo temporal + os.replace).

    Parámetros:
        ruta (str): archivo de destino.
        datos: objeto serializable a JSON.
    Retorna:
        None. Lanza ErrorPersistencia si la escritura falla.
    """
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
    """Lee un archivo JSON.

    Parámetros:
        ruta (str): archivo a leer.
    Retorna:
        El contenido decodificado, o None si el archivo no existe.
        Lanza ErrorPersistencia si el JSON es inválido o hay error de lectura.
    """
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
    """Comprueba que un fragmento tenga las claves y tipos del modelo de datos.

    Parámetros:
        fragmento (dict): debe tener codigo (int), titulo (str), sala (str)
            y valor (int).
    Retorna:
        None. Lanza ErrorPersistencia si algo no coincide.
    """
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
    """Comprueba que el estado de la partida tenga la forma y los tipos esperados.

    Parámetros:
        estado (dict): jugador, inventario, sala_actual, intentos y,
            opcionalmente, recolectados.
    Retorna:
        None. Lanza ErrorPersistencia si algo no es válido.
    """
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

    if not isinstance(estado.get("recolectados", []), list):
        raise ErrorPersistencia("'recolectados' debe ser una lista.")
    for fragmento in estado.get("recolectados", []):
        validar_fragmento(fragmento)

    if not _es_entero(estado["sala_actual"]) or not 1 <= estado["sala_actual"] <= 6:
        raise ErrorPersistencia("'sala_actual' debe estar entre 1 y 6.")
    if not _es_entero(estado["intentos"]) or estado["intentos"] < 0:
        raise ErrorPersistencia("'intentos' debe ser un entero >= 0.")


# --------------------------------------------------------------------- partida
def guardar_partida(estado, ruta=RUTA_PARTIDA):
    """Valida y guarda el estado completo de la partida en JSON.

    Parámetros:
        estado (dict): estado de la partida.
        ruta (str): archivo de destino.
    Retorna:
        None. Lanza ErrorPersistencia si el estado es inválido o falla la E/S.
    """
    validar_estado(estado)
    _escribir_json(ruta, estado)


def cargar_partida(ruta=RUTA_PARTIDA):
    """Carga y valida la partida guardada.

    Parámetros:
        ruta (str): archivo de origen.
    Retorna:
        dict con el estado, o None si no hay partida guardada.
        Lanza ErrorPersistencia si el archivo está dañado o es inválido.
    """
    estado = _leer_json(ruta)
    if estado is None:
        return None
    validar_estado(estado)
    return estado


def existe_partida(ruta=RUTA_PARTIDA):
    """Indica si hay una partida guardada.

    Parámetros:
        ruta (str): archivo de la partida.
    Retorna:
        bool: True si el archivo existe.
    """
    return os.path.isfile(ruta)


def eliminar_partida(ruta=RUTA_PARTIDA):
    """Borra la partida guardada (al terminar el juego).

    Parámetros:
        ruta (str): archivo de la partida.
    Retorna:
        None. No falla si el archivo no existe; lanza ErrorPersistencia si
        no se puede borrar.
    """
    try:
        os.remove(ruta)
    except FileNotFoundError:
        pass
    except OSError as error:
        raise ErrorPersistencia(f"No se pudo borrar '{ruta}': {error}") from error


# -------------------------------------------------------------------- puntajes
def cargar_puntajes(ruta=RUTA_PUNTAJES):
    """Carga la tabla de puntajes.

    Parámetros:
        ruta (str): archivo de puntajes.
    Retorna:
        list: registros ordenados de mayor a menor puntaje ([] si no hay).
        Lanza ErrorPersistencia si el archivo está dañado.
    """
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
    """Agrega un registro a la tabla y conserva solo los MAX_PUNTAJES mejores.

    Parámetros:
        nombre (str): nombre del jugador.
        puntaje (float): puntaje final.
        fragmentos (int): fragmentos válidos recuperados.
        intentos (int): preguntas falladas.
        ruta (str): archivo de puntajes.
    Retorna:
        list: la tabla actualizada.
    """
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


# ---------------------------------------------------------------- recolectados
def guardar_recolectados(fragmentos, ruta=RUTA_RECOLECTADOS):
    """Guarda en un archivo los fragmentos recolectados durante la partida.

    Parámetros:
        fragmentos (list): lista de diccionarios (puede incluir repetidos).
        ruta (str): archivo de destino.
    Retorna:
        None. Lanza ErrorPersistencia si algún fragmento es inválido o falla la E/S.
    """
    for fragmento in fragmentos:
        validar_fragmento(fragmento)
    _escribir_json(ruta, fragmentos)


def cargar_recolectados(ruta=RUTA_RECOLECTADOS):
    """Lee desde archivo los fragmentos recolectados (Paso 1 de la Sala Central).

    Parámetros:
        ruta (str): archivo de origen.
    Retorna:
        list: fragmentos (diccionarios). Lanza ErrorPersistencia si el archivo
        no existe, está dañado o contiene fragmentos inválidos.
    """
    datos = _leer_json(ruta)
    if datos is None:
        raise ErrorPersistencia(f"No existe el archivo de fragmentos '{ruta}'.")
    if not isinstance(datos, list):
        raise ErrorPersistencia("El archivo de fragmentos debe contener una lista.")
    for fragmento in datos:
        validar_fragmento(fragmento)
    return datos


def eliminar_recolectados(ruta=RUTA_RECOLECTADOS):
    """Borra el archivo de fragmentos recolectados al terminar la partida.

    Parámetros:
        ruta (str): archivo de fragmentos.
    Retorna:
        None. No falla si no existe.
    """
    try:
        os.remove(ruta)
    except FileNotFoundError:
        pass
    except OSError as error:
        raise ErrorPersistencia(f"No se pudo borrar '{ruta}': {error}") from error
