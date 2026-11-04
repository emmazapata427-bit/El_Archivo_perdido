"""El Archivo Perdido: juego serio de estructuras de datos (consola).

Lógica de salas, menús, puntaje y preguntas. Las estructuras propias están en
``estructuras.py`` y el guardado/carga en ``persistencia.py``.

Cada sala tiene un reto práctico (sin penalización) y una pregunta conceptual:
si se falla se pierde vida y se cuenta un intento; si se acierta se recibe un
fragmento del catálogo y se guarda la partida.
"""

import random

import persistencia
from estructuras import ArbolBST

VIDA_INICIAL = 3
PENALIZACION_INTENTO = 5
TOTAL_SALAS = 5

NOMBRES_SALAS = {
    1: "Vestíbulo",
    2: "Estanterías",
    3: "Mapas",
    4: "Fichas",
    5: "Sellos",
}

# Fragmento que se obtiene al aprobar cada sala (modelo de datos del diseño).
FRAGMENTOS = {
    1: {"codigo": 1042, "titulo": "Algoritmos básicos", "sala": "Vestíbulo", "valor": 50},
    2: {"codigo": 2017, "titulo": "Estructuras lineales", "sala": "Estanterías", "valor": 50},
    3: {"codigo": 3305, "titulo": "Atlas de la biblioteca", "sala": "Mapas", "valor": 60},
    4: {"codigo": 4128, "titulo": "Fichas de autores", "sala": "Fichas", "valor": 70},
    5: {"codigo": 5090, "titulo": "Sellos de la hemeroteca", "sala": "Sellos", "valor": 70},
}

# Banco de preguntas conceptuales. "correcta" es el índice (base 0) de la opción.
PREGUNTAS = {
    1: [
        {
            "enunciado": "¿Qué tipo de dato es el más adecuado para 'activo' (si el explorador sigue en juego)?",
            "opciones": ["bool", "str", "float"],
            "correcta": 0,
            "explicacion": "Solo tiene dos estados posibles: verdadero o falso.",
        },
        {
            "enunciado": "Si guardas la vida como str ('3') e intentas restarle 1, ¿qué ocurre?",
            "opciones": ["Resulta 2", "Lanza TypeError", "Resulta '2'"],
            "correcta": 1,
            "explicacion": "No se puede restar un int a un str: por eso se convierte y valida la entrada.",
        },
    ],
    2: [
        {
            "enunciado": "¿Por qué una lista es adecuada para el inventario?",
            "opciones": [
                "Es mutable, conserva el orden y permite acceso por posición",
                "Es inmutable y por eso es segura",
                "No admite elementos repetidos",
            ],
            "correcta": 0,
            "explicacion": "El inventario cambia (agregar/quitar) y necesita orden: eso es una lista.",
        },
        {
            "enunciado": "¿Qué diferencia hay entre lista.sort() y sorted(lista)?",
            "opciones": [
                "sort() devuelve una lista nueva y sorted() modifica la original",
                "sort() ordena la lista original; sorted() devuelve una lista nueva",
                "No hay ninguna diferencia",
            ],
            "correcta": 1,
            "explicacion": "sort() es un método que ordena en el lugar; sorted() deja la original intacta.",
        },
    ],
    3: [
        {
            "enunciado": "¿Por qué una posición (fila, columna) se guarda como tupla y no como lista?",
            "opciones": [
                "Porque las tuplas ocupan menos letras al escribirlas",
                "Porque es inmutable y hashable (sirve de clave de diccionario o elemento de conjunto)",
                "Porque las listas no admiten números",
            ],
            "correcta": 1,
            "explicacion": "Una coordenada no debe cambiar por accidente y puede usarse como clave.",
        },
        {
            "enunciado": "Si pos = (2, 3) y ejecutas pos[0] = 5, ¿qué ocurre?",
            "opciones": ["pos pasa a ser (5, 3)", "Se ignora la instrucción", "Lanza TypeError"],
            "correcta": 2,
            "explicacion": "Las tuplas no admiten asignación por índice; hay que crear una tupla nueva.",
        },
    ],
    4: [
        {
            "enunciado": "¿Cómo consultas una clave que podría no existir sin que salte KeyError?",
            "opciones": ["ficha[clave]", "ficha.get(clave)", "ficha.keys(clave)"],
            "correcta": 1,
            "explicacion": "get() devuelve None (o un valor por defecto) si la clave no está.",
        },
        {
            "enunciado": "¿Cuál es el costo promedio de buscar por clave en un diccionario?",
            "opciones": ["O(1)", "O(n)", "O(log n)"],
            "correcta": 0,
            "explicacion": "Usa una tabla hash: el acceso por clave es de tiempo promedio constante.",
        },
    ],
    5: [
        {
            "enunciado": "¿Qué pasa al agregar a un conjunto un elemento que ya contiene?",
            "opciones": [
                "Queda duplicado",
                "Lanza una excepción",
                "El conjunto no cambia",
            ],
            "correcta": 2,
            "explicacion": "Un conjunto garantiza unicidad: los repetidos se ignoran.",
        },
        {
            "enunciado": "¿Qué operación entrega los códigos que están en A pero no en B?",
            "opciones": ["A | B (unión)", "A & B (intersección)", "A - B (diferencia)"],
            "correcta": 2,
            "explicacion": "La diferencia A - B conserva lo que está solo en A.",
        },
    ],
}


# ------------------------------------------------------------ entrada validada
def leer_texto(mensaje, max_len=20):
    """Pide un texto no vacío de hasta max_len caracteres."""
    while True:
        texto = input(mensaje).strip()
        if not texto:
            print("  La entrada no puede estar vacía.")
        elif len(texto) > max_len:
            print(f"  Máximo {max_len} caracteres.")
        else:
            return texto


def leer_entero(mensaje, minimo=None, maximo=None):
    """Pide un entero y repite hasta que sea válido y esté en el rango."""
    while True:
        try:
            valor = int(input(mensaje).strip())
        except ValueError:
            print("  Debes ingresar un número entero.")
            continue
        if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
            print(f"  El valor debe estar entre {minimo} y {maximo}.")
            continue
        return valor


# ------------------------------------------------------------------- estado
def crear_estado(nombre):
    """Estado inicial: el explorador entra con inventario vacío."""
    return {
        "jugador": {
            "nombre": nombre,
            "vida": VIDA_INICIAL,    # int
            "puntaje": 0.0,          # float (admite bonificaciones)
            "nivel": 1,              # int
            "activo": True,          # bool
        },
        "inventario": [],            # list de dict (fragmentos)
        "sala_actual": 1,
        "intentos": 0,               # preguntas falladas
    }


def calcular_puntaje(inventario, intentos):
    """Suma de valores de los fragmentos menos la penalización por intentos."""
    total = sum(fragmento["valor"] for fragmento in inventario)
    return float(max(0, total - PENALIZACION_INTENTO * intentos))


def guardar_seguro(estado):
    """Guarda la partida; si falla, avisa pero no interrumpe el juego."""
    try:
        persistencia.guardar_partida(estado)
    except persistencia.ErrorPersistencia as error:
        print(f"  [Aviso] No se pudo guardar la partida: {error}")


def mostrar_estado(estado):
    jugador = estado["jugador"]
    print(f"  Explorador: {jugador['nombre']}")
    print(f"  Vida: {jugador['vida']}   Nivel: {jugador['nivel']}   "
          f"Puntaje: {jugador['puntaje']:.1f}   Intentos fallidos: {estado['intentos']}")
    print(f"  Fragmentos recuperados: {len(estado['inventario'])}/{TOTAL_SALAS}")


# -------------------------------------------------------------------- retos
def reto_vestibulo(estado):
    """Vestíbulo: variables int, float, str y bool."""
    print("Tu linterna ilumina un panel con tu estado. Cada dato tiene su propio tipo:\n")
    for clave, valor in estado["jugador"].items():
        print(f"  {clave:<8} = {valor!r:<14} -> {type(valor).__name__}")
    print("\nPara operar con la vida o el nivel hay que convertir la entrada con int()")
    print("y validarla; por eso el juego usa try/except en cada lectura.")
    input("\n(Enter para continuar)")


def reto_estanterias(estado):
    """Estanterías: lista (orden, acceso por posición, sorted con key)."""
    sueltos = [
        {"codigo": 3400, "titulo": "Redes"},
        {"codigo": 1250, "titulo": "Álgebra"},
        {"codigo": 2780, "titulo": "Bases de datos"},
        {"codigo": 1999, "titulo": "Python"},
    ]
    print("Cuatro fichas están tiradas en el suelo, en desorden (una lista):\n")
    for i, ficha in enumerate(sueltos):
        print(f"  [{i}] {ficha['codigo']}  {ficha['titulo']}")
    ordenados = sorted(sueltos, key=lambda ficha: ficha["codigo"])
    print("\nReto: al ordenarlas de menor a mayor por código, ¿qué código queda en la posición 0?")
    while True:
        respuesta = leer_entero("  Código: ")
        if respuesta == ordenados[0]["codigo"]:
            break
        print("  No es ese. Pista: es el menor de todos.")
    print("\nEstantería ordenada con sorted(lista, key=...):")
    for i, ficha in enumerate(ordenados):
        print(f"  [{i}] {ficha['codigo']}  {ficha['titulo']}")
    print(f"  lista[0] = {ordenados[0]['codigo']}   lista[-1] = {ordenados[-1]['codigo']}")


def dibujar_mapa(posicion, objetivo, filas, columnas):
    for fila in range(filas):
        celdas = []
        for columna in range(columnas):
            celda = (fila, columna)  # la tupla sirve para comparar posiciones
            if celda == posicion:
                celdas.append("E")
            elif celda == objetivo:
                celdas.append("X")
            else:
                celdas.append(".")
        print("   " + " ".join(celdas))


def reto_mapas(estado):
    """Mapas: tuplas (fila, columna) inmutables."""
    filas, columnas = 4, 4
    objetivo = (3, 3)
    posicion = (0, 0)
    movimientos = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
    print("Estás en el mapa (E). Llega a la salida (X) con w/a/s/d.")
    print("Tu posición es una tupla (fila, columna): no se modifica, se reemplaza.\n")
    while posicion != objetivo:
        dibujar_mapa(posicion, objetivo, filas, columnas)
        print(f"  posición = {posicion}")
        tecla = input("  Mover (w/a/s/d): ").strip().lower()
        if tecla not in movimientos:
            print("  Tecla inválida.")
            continue
        fila, columna = posicion                      # desempaquetado
        d_fila, d_columna = movimientos[tecla]
        nueva = (fila + d_fila, columna + d_columna)  # tupla nueva
        if not (0 <= nueva[0] < filas and 0 <= nueva[1] < columnas):
            print("  Hay una pared de estantes. Intenta otra dirección.")
            continue
        posicion = nueva
    print(f"\n¡Llegaste a {objetivo}!")


def reto_fichas(estado):
    """Fichas: diccionario consultado por clave con get()."""
    fichero = {
        7001: {"codigo": 7001, "titulo": "Catálogo de autores", "sala": "Estanterías", "valor": 10},
        7002: {"codigo": 7002, "titulo": "Registro de préstamos", "sala": "Sellos", "valor": 20},
        7003: {"codigo": 7003, "titulo": "Planos del edificio", "sala": "Mapas", "valor": 30},
        7004: {"codigo": 7004, "titulo": "Índice temático", "sala": "Fichas", "valor": 40},
    }
    print("Un fichero guarda fragmentos como diccionarios, con claves nombradas.")
    print(f"Códigos disponibles: {sorted(fichero)}")
    print("Reto: consulta por código hasta hallar la ficha cuya 'sala' sea 'Mapas'.\n")
    while True:
        codigo = leer_entero("  Código a consultar: ")
        ficha = fichero.get(codigo)  # None si no existe: no hay KeyError
        if ficha is None:
            print(f"  fichero.get({codigo}) -> None (esa clave no existe).")
            continue
        print(f"  fichero.get({codigo}) -> titulo={ficha['titulo']!r}, sala={ficha['sala']!r}")
        if ficha["sala"] == "Mapas":
            print("  ¡Esa es! Una consulta por clave no recorre todo el fichero.")
            return
        print("  No es de la sala 'Mapas'. Sigue buscando.")


def reto_sellos(estado):
    """Sellos: conjunto para quitar duplicados y validar pistas."""
    pistas = [101, 205, 101, 307, 205, 412, 307, 101]
    validos = {101, 307, 500}
    print(f"Pistas selladas (con repetidas): {pistas}")
    print("Reto: ¿cuántos códigos distintos hay?")
    unicos = set(pistas)
    while True:
        respuesta = leer_entero("  Cantidad: ")
        if respuesta == len(unicos):
            break
        print("  No coincide. Pista: los repetidos cuentan una sola vez.")
    print(f"\n  set(pistas)         = {sorted(unicos)}")
    print(f"  unicos & validos    = {sorted(unicos & validos)}   (pistas auténticas)")
    print(f"  unicos - validos    = {sorted(unicos - validos)}   (pistas falsas)")
    print(f"  validos - unicos    = {sorted(validos - unicos)}   (códigos que aún faltan)")


SALAS = {
    1: reto_vestibulo,
    2: reto_estanterias,
    3: reto_mapas,
    4: reto_fichas,
    5: reto_sellos,
}


# --------------------------------------------------------------- preguntas
def preguntar(estado, sala_id):
    """Hace preguntas hasta acertar o quedarse sin vida.

    Devuelve True si acertó, False si la vida llegó a 0.
    """
    jugador = estado["jugador"]
    ultima = None
    while True:
        candidatas = [p for p in PREGUNTAS[sala_id] if p is not ultima] or PREGUNTAS[sala_id]
        pregunta = random.choice(candidatas)
        ultima = pregunta

        print(f"\nPregunta de la sala: {pregunta['enunciado']}")
        for i, opcion in enumerate(pregunta["opciones"], start=1):
            print(f"  {i}) {opcion}")
        eleccion = leer_entero("Tu respuesta: ", 1, len(pregunta["opciones"]))

        if eleccion - 1 == pregunta["correcta"]:
            print(f"¡Correcto! {pregunta['explicacion']}")
            return True

        jugador["vida"] -= 1
        estado["intentos"] += 1
        print(f"Incorrecto. {pregunta['explicacion']}")
        print(f"Pierdes 1 de vida. Vida restante: {max(jugador['vida'], 0)}")
        if jugador["vida"] <= 0:
            jugador["activo"] = False
            return False


def recibir_fragmento(estado, sala_id):
    """Agrega el fragmento de la sala al inventario (sin duplicar) y actualiza el estado."""
    fragmento = dict(FRAGMENTOS[sala_id])
    codigos = {f["codigo"] for f in estado["inventario"]}
    if fragmento["codigo"] not in codigos:
        estado["inventario"].append(fragmento)
        print(f"Recibes el fragmento {fragmento['codigo']}: «{fragmento['titulo']}» "
              f"(+{fragmento['valor']} pts).")
    estado["jugador"]["puntaje"] = calcular_puntaje(estado["inventario"], estado["intentos"])
    estado["sala_actual"] = sala_id + 1
    estado["jugador"]["nivel"] = estado["sala_actual"]


# -------------------------------------------------------------- sala central
def sala_central(estado):
    """Vista preliminar: inserta el inventario en el BST y muestra el inorden.

    La reconstrucción completa (6 pasos, consultas con conteo de comparaciones)
    se implementa en la siguiente entrega.
    """
    print("\n=== SALA CENTRAL (versión preliminar) ===")
    arbol = ArbolBST()
    for fragmento in estado["inventario"]:
        arbol.insertar(fragmento["codigo"], fragmento)
    print(f"Catálogo reconstruido con {len(arbol)} fragmentos.")
    print(f"Recorrido inorden (códigos ordenados): {arbol.inorden()}")


# ------------------------------------------------------------------- partida
def terminar_partida(estado, victoria):
    jugador = estado["jugador"]
    jugador["puntaje"] = calcular_puntaje(estado["inventario"], estado["intentos"])
    print("\n" + "=" * 50)
    if victoria:
        print("¡Reconstruiste el catálogo antes del amanecer!")
    else:
        print("Te quedaste sin vida: la linterna se apaga. FIN DE PARTIDA.")
    mostrar_estado(estado)
    print("=" * 50)
    try:
        persistencia.registrar_puntaje(
            jugador["nombre"], jugador["puntaje"], len(estado["inventario"]), estado["intentos"]
        )
        persistencia.eliminar_partida()
    except persistencia.ErrorPersistencia as error:
        print(f"  [Aviso] No se pudo actualizar el almacenamiento: {error}")


def jugar(estado):
    """Ciclo principal de la partida. Guarda al avanzar y ante una interrupción."""
    try:
        while estado["sala_actual"] <= TOTAL_SALAS:
            sala_id = estado["sala_actual"]
            print(f"\n=== SALA {sala_id}/{TOTAL_SALAS}: {NOMBRES_SALAS[sala_id].upper()} ===")
            mostrar_estado(estado)
            print()
            SALAS[sala_id](estado)

            if not preguntar(estado, sala_id):
                terminar_partida(estado, victoria=False)
                return
            recibir_fragmento(estado, sala_id)
            guardar_seguro(estado)
            print("(Partida guardada)")

        sala_central(estado)
        terminar_partida(estado, victoria=True)
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupción detectada. Guardando la partida...")
        guardar_seguro(estado)
        print("Puedes continuarla desde el menú principal.")


def nueva_partida():
    if persistencia.existe_partida():
        resp = input("Ya hay una partida guardada; empezar una nueva la borrará. ¿Continuar? (s/n): ")
        if resp.strip().lower() != "s":
            return
    print("\nUna tormenta destruyó el catálogo de la biblioteca. Entras con una linterna")
    print("y el inventario vacío. Recupera los fragmentos antes de que amanezca.\n")
    nombre = leer_texto("Nombre del explorador: ")
    jugar(crear_estado(nombre))


def continuar_partida():
    try:
        estado = persistencia.cargar_partida()
    except persistencia.ErrorPersistencia as error:
        print(f"\nNo se pudo cargar la partida: {error}")
        return
    if estado is None:
        print("\nNo hay partida guardada.")
        return
    print(f"\nBienvenido de nuevo, {estado['jugador']['nombre']}.")
    jugar(estado)


def mostrar_puntajes():
    try:
        tabla = persistencia.cargar_puntajes()
    except persistencia.ErrorPersistencia as error:
        print(f"\nNo se pudo leer la tabla de puntajes: {error}")
        return
    print("\n=== TABLA DE PUNTAJES ===")
    if not tabla:
        print("  Aún no hay puntajes.")
        return
    print(f"  {'#':<3}{'Nombre':<22}{'Puntaje':>8}{'Frag.':>7}{'Intentos':>10}  Fecha")
    for i, r in enumerate(tabla, start=1):
        print(f"  {i:<3}{r['nombre']:<22}{r['puntaje']:>8.1f}{r.get('fragmentos', '-'):>7}"
              f"{r.get('intentos', '-'):>10}  {r.get('fecha', '')}")


def main():
    print("=" * 50)
    print("  EL ARCHIVO PERDIDO")
    print("  Juego serio de estructuras de datos en Python")
    print("=" * 50)
    try:
        while True:
            print("\n1) Nueva partida")
            print("2) Continuar partida guardada")
            print("3) Tabla de puntajes")
            print("4) Salir")
            opcion = leer_entero("Opción: ", 1, 4)
            if opcion == 1:
                nueva_partida()
            elif opcion == 2:
                continuar_partida()
            elif opcion == 3:
                mostrar_puntajes()
            else:
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("¡Hasta pronto!")


if __name__ == "__main__":
    main()
