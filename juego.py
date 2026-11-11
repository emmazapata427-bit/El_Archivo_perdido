"""El Archivo Perdido: juego serio de estructuras de datos (consola).

Lógica de salas, menús, puntaje y preguntas. Las estructuras propias están en
``estructuras.py`` y el guardado/carga en ``persistencia.py``.

Cada sala tiene un reto práctico (sin penalización) y una pregunta conceptual:
si se falla se pierde vida y se cuenta un intento; si se acierta se recibe un
fragmento del catálogo y se guarda la partida. Al completar las cinco salas se
entra a la Sala Central, donde se ejecuta «La Reconstrucción del Catálogo».
"""

import random

import persistencia
from estructuras import ArbolBST, busqueda_secuencial

VIDA_INICIAL = 3
PENALIZACION_INTENTO = 5
TOTAL_SALAS = 5
FRAGMENTOS_POR_ESTANTE = 3

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
    """Pide un texto no vacío y repite hasta que sea válido.

    Parámetros:
        mensaje (str): texto que se muestra al pedir el dato.
        max_len (int): longitud máxima permitida.
    Retorna:
        str: el texto ingresado, sin espacios en los extremos.
    """
    while True:
        texto = input(mensaje).strip()
        if not texto:
            print("  La entrada no puede estar vacía.")
        elif len(texto) > max_len:
            print(f"  Máximo {max_len} caracteres.")
        else:
            return texto


def leer_entero(mensaje, minimo=None, maximo=None):
    """Pide un entero y repite hasta que sea válido y esté en el rango.

    Parámetros:
        mensaje (str): texto que se muestra al pedir el dato.
        minimo (int | None): valor mínimo permitido (opcional).
        maximo (int | None): valor máximo permitido (opcional).
    Retorna:
        int: el número ingresado.
    """
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


def leer_decimal(mensaje, minimo=None, maximo=None):
    """Pide un número decimal (acepta coma o punto) y repite hasta que sea válido.

    Parámetros:
        mensaje (str): texto que se muestra al pedir el dato.
        minimo (float | None): valor mínimo permitido (opcional).
        maximo (float | None): valor máximo permitido (opcional).
    Retorna:
        float: el número ingresado.
    """
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
        except ValueError:
            print("  Debes ingresar un número (por ejemplo 2.5).")
            continue
        if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
            print(f"  El valor debe estar entre {minimo} y {maximo}.")
            continue
        return valor


# ------------------------------------------------------------------- estado
def crear_estado(nombre):
    """Crea el estado inicial: el explorador entra con el inventario vacío.

    Parámetros:
        nombre (str): nombre del jugador.
    Retorna:
        dict: estado con jugador, inventario, recolectados, sala_actual e intentos.
    """
    return {
        "jugador": {
            "nombre": nombre,
            "vida": VIDA_INICIAL,    # int
            "puntaje": 0.0,          # float (admite bonificaciones)
            "nivel": 1,              # int
            "activo": True,          # bool
        },
        "inventario": [],            # list de dict: fragmentos únicos
        "recolectados": [],          # list de dict: todo lo recogido (puede repetirse)
        "sala_actual": 1,
        "intentos": 0,               # preguntas falladas
    }


def calcular_puntaje(inventario, intentos):
    """Calcula el puntaje: suma de valores menos la penalización por intentos.

    Parámetros:
        inventario (list): fragmentos válidos (sin repetidos).
        intentos (int): preguntas falladas.
    Retorna:
        float: puntaje, nunca negativo.
    """
    total = sum(fragmento["valor"] for fragmento in inventario)
    return float(max(0, total - PENALIZACION_INTENTO * intentos))


def guardar_seguro(estado):
    """Guarda la partida y el archivo de recolectados; si falla, avisa sin interrumpir.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
    try:
        persistencia.guardar_partida(estado)
        persistencia.guardar_recolectados(estado.get("recolectados", []))
    except persistencia.ErrorPersistencia as error:
        print(f"  [Aviso] No se pudo guardar la partida: {error}")


def mostrar_estado(estado):
    """Imprime el resumen del jugador (vida, nivel, puntaje, intentos, fragmentos).

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
    jugador = estado["jugador"]
    print(f"  Explorador: {jugador['nombre']}")
    print(f"  Vida: {jugador['vida']}   Nivel: {jugador['nivel']}   "
          f"Puntaje: {jugador['puntaje']:.1f}   Intentos fallidos: {estado['intentos']}")
    print(f"  Fragmentos recuperados: {len(estado['inventario'])}/{TOTAL_SALAS}")


# -------------------------------------------------------------------- retos
def reto_vestibulo(estado):
    """Sala 1 (Vestíbulo): tipos int, float, str y bool con conversión validada.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
    print("Tu linterna ilumina un panel con tu estado. Cada dato tiene su propio tipo:\n")
    for clave, valor in estado["jugador"].items():
        print(f"  {clave:<8} = {valor!r:<14} -> {type(valor).__name__}")
    print("\nReto: calibra tu linterna. input() siempre devuelve str, así que hay que")
    print("convertir con int() y float() y validar la entrada.")
    pilas = leer_entero("  ¿Cuántas pilas tienes? (entero, 1-9): ", 1, 9)
    intensidad = leer_decimal("  Intensidad de la linterna (decimal, 0.5-5): ", 0.5, 5)
    horas = pilas * intensidad
    print(f"\n  pilas={pilas!r} ({type(pilas).__name__}), "
          f"intensidad={intensidad!r} ({type(intensidad).__name__})")
    print(f"  pilas * intensidad = {horas:.2f} ({type(horas).__name__}): "
          "int por float da float.")


def reto_estanterias(estado):
    """Sala 2 (Estanterías): lista con inserción, eliminación, búsqueda y orden.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
    estanteria = [
        {"codigo": 3400, "titulo": "Redes"},
        {"codigo": 0, "titulo": "(ficha ilegible)"},
        {"codigo": 1250, "titulo": "Álgebra"},
        {"codigo": 2780, "titulo": "Bases de datos"},
    ]
    print("Las fichas están en desorden en una lista:\n")
    for i, ficha in enumerate(estanteria):
        print(f"  [{i}] {ficha['codigo']}  {ficha['titulo']}")

    # 1) ELIMINAR
    print("\nPaso 1 · Eliminar. Hay una ficha ilegible: indica su posición.")
    while True:
        posicion = leer_entero(f"  Posición (0-{len(estanteria) - 1}): ", 0, len(estanteria) - 1)
        if estanteria[posicion]["codigo"] == 0:
            eliminada = estanteria.pop(posicion)
            print(f"  lista.pop({posicion}) -> se eliminó {eliminada['titulo']}")
            break
        print("  Esa ficha sí se puede leer. Busca la que tiene código 0.")

    # 2) INSERTAR
    estanteria.append({"codigo": 1999, "titulo": "Python"})
    estanteria.insert(1, {"codigo": 3100, "titulo": "Estadística"})
    print("\nPaso 2 · Insertar. Encuentras dos fichas más: append(1999) e insert(1, 3100).")
    print(f"  Ahora hay {len(estanteria)} fichas.")

    # 3) BUSCAR (con comprensión de listas)
    print("\nPaso 3 · Buscar. Elige un código de la estantería para localizarlo.")
    print(f"  Códigos presentes: {[ficha['codigo'] for ficha in estanteria]}")
    while True:
        codigo = leer_entero("  Código a buscar: ")
        coincidencias = [i for i, ficha in enumerate(estanteria) if ficha["codigo"] == codigo]
        if coincidencias:
            print(f"  Comprensión [i for i, f in enumerate(lista) if f['codigo'] == {codigo}]"
                  f" -> {coincidencias}")
            break
        print("  Ese código no está en la estantería.")

    # 4) ORDENAR
    ordenados = sorted(estanteria, key=lambda ficha: ficha["codigo"])
    print("\nPaso 4 · Ordenar. Al ordenar de menor a mayor por código, ¿qué código queda en la posición 0?")
    while True:
        respuesta = leer_entero("  Código: ")
        if respuesta == ordenados[0]["codigo"]:
            break
        print("  No es ese. Pista: es el menor de todos.")
    print("\nEstantería ordenada con sorted(lista, key=...):")
    for i, ficha in enumerate(ordenados):
        print(f"  [{i}] {ficha['codigo']}  {ficha['titulo']}")
    titulos = [ficha["titulo"] for ficha in ordenados]
    print(f"  Títulos (comprensión de listas): {titulos}")


def dibujar_mapa(posicion, objetivo, filas, columnas):
    """Dibuja la cuadrícula: E = explorador, X = salida, . = vacío.

    Parámetros:
        posicion (tuple): (fila, columna) del explorador.
        objetivo (tuple): (fila, columna) de la salida.
        filas (int): número de filas.
        columnas (int): número de columnas.
    Retorna:
        None.
    """
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
    """Sala 3 (Mapas): posiciones como tuplas inmutables con desempaquetado.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
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
    """Sala 4 (Fichas): diccionario consultado por clave, con claves inexistentes.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
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
    """Sala 5 (Sellos): conjunto para quitar repetidos y validar pistas.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        None.
    """
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
    print(f"  unicos | validos    = {sorted(unicos | validos)}   (unión)")
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
    """Hace preguntas conceptuales hasta acertar o quedarse sin vida.

    Cada fallo resta 1 de vida y suma 1 intento; tras un fallo se plantea otra
    pregunta distinta cuando el banco lo permite.

    Parámetros:
        estado (dict): estado de la partida (se modifica vida e intentos).
        sala_id (int): número de sala (1 a 5).
    Retorna:
        bool: True si acertó; False si la vida llegó a 0.
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
    """Entrega el fragmento de la sala y actualiza inventario, puntaje y nivel.

    El fragmento va al inventario (sin duplicar) y al registro de recolectados.
    En la sala 5 el explorador además halla una copia mojada de un fragmento
    ya recogido, para que la depuración de la Sala Central tenga trabajo.

    Parámetros:
        estado (dict): estado de la partida (se modifica).
        sala_id (int): sala superada (1 a 5).
    Retorna:
        None.
    """
    fragmento = dict(FRAGMENTOS[sala_id])
    recolectados = estado.setdefault("recolectados", [])
    codigos = {f["codigo"] for f in estado["inventario"]}
    if fragmento["codigo"] not in codigos:
        estado["inventario"].append(fragmento)
        recolectados.append(dict(fragmento))
        print(f"Recibes el fragmento {fragmento['codigo']}: «{fragmento['titulo']}» "
              f"(+{fragmento['valor']} pts).")
    if sala_id == TOTAL_SALAS and len(estado["inventario"]) > 1:
        copia = dict(random.choice(estado["inventario"][:-1]))
        recolectados.append(copia)
        print(f"Entre los sellos hallas también una copia mojada del fragmento {copia['codigo']}.")
    estado["jugador"]["puntaje"] = calcular_puntaje(estado["inventario"], estado["intentos"])
    estado["sala_actual"] = sala_id + 1
    estado["jugador"]["nivel"] = estado["sala_actual"]


# -------------------------------------------------- La Reconstrucción del Catálogo
def paso_carga(estado):
    """Paso 1 (Carga): lee desde archivo los fragmentos recolectados.

    Si el archivo no existe o está dañado, avisa y usa la copia del estado.

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        list: fragmentos (diccionarios) leídos, posiblemente con repetidos.
    """
    print("\n--- Paso 1 · Carga: leer los fragmentos desde el archivo ---")
    try:
        fragmentos = persistencia.cargar_recolectados()
        print(f"  Se leyeron {len(fragmentos)} fragmentos de {persistencia.RUTA_RECOLECTADOS}.")
    except persistencia.ErrorPersistencia as error:
        print(f"  [Aviso] {error}")
        print("  Se usará la copia de los fragmentos guardada en la partida.")
        fragmentos = [dict(f) for f in (estado.get("recolectados") or estado["inventario"])]
    for fragmento in fragmentos:
        print(f"    {fragmento['codigo']}  {fragmento['titulo']}")
    return fragmentos


def paso_depuracion(fragmentos):
    """Paso 2 (Depuración): elimina repetidos con un conjunto de códigos.

    Parámetros:
        fragmentos (list): fragmentos leídos, posiblemente con repetidos.
    Retorna:
        tuple: (lista de fragmentos únicos en orden de aparición,
                cantidad de fragmentos descartados).
    """
    print("\n--- Paso 2 · Depuración: eliminar duplicados con un conjunto ---")
    vistos = set()
    unicos = []
    descartados = []
    for fragmento in fragmentos:
        if fragmento["codigo"] in vistos:
            descartados.append(fragmento["codigo"])
        else:
            vistos.add(fragmento["codigo"])
            unicos.append(fragmento)
    print(f"  Códigos distintos: {sorted(vistos)}")
    print(f"  Se descartaron {len(descartados)} fragmentos duplicados"
          + (f" (códigos {descartados})." if descartados else "."))
    return unicos, len(descartados)


def paso_ubicacion(unicos):
    """Paso 3 (Ubicación): asigna a cada fragmento una tupla (estante, nivel).

    Los fragmentos se ordenan por código y se reparten FRAGMENTOS_POR_ESTANTE
    por estante. La posición se guarda aparte, sin mezclarla con el fragmento.

    Parámetros:
        unicos (list): fragmentos sin repetidos.
    Retorna:
        dict: {codigo: (estante, nivel)}.
    """
    print("\n--- Paso 3 · Ubicación: posición (estante, nivel) como tupla ---")
    posiciones = {}
    for indice, fragmento in enumerate(sorted(unicos, key=lambda f: f["codigo"])):
        estante = indice // FRAGMENTOS_POR_ESTANTE + 1
        nivel = indice % FRAGMENTOS_POR_ESTANTE + 1
        posiciones[fragmento["codigo"]] = (estante, nivel)
    for codigo, posicion in posiciones.items():
        estante, nivel = posicion  # desempaquetado
        print(f"  {codigo} -> estante {estante}, nivel {nivel}   {posicion}")
    return posiciones


def paso_construccion(unicos):
    """Paso 4 (Construcción): inserta los fragmentos en un BST por código.

    Parámetros:
        unicos (list): fragmentos sin repetidos, en el orden de inserción.
    Retorna:
        ArbolBST: el árbol construido.
    """
    print("\n--- Paso 4 · Construcción: árbol binario de búsqueda ---")
    arbol = ArbolBST()
    for fragmento in unicos:
        insertado = arbol.insertar(fragmento["codigo"], fragmento)
        print(f"  insertar({fragmento['codigo']}) -> {'ok' if insertado else 'repetido'}")
    print(f"  Árbol con {len(arbol)} nodos y altura {arbol.altura()}.")
    return arbol


def paso_verificacion(arbol, unicos):
    """Paso 5 (Verificación): comprueba que el recorrido inorden esté ordenado.

    Parámetros:
        arbol (ArbolBST): árbol construido.
        unicos (list): fragmentos que debían quedar en el árbol.
    Retorna:
        bool: True si el inorden está ordenado y contiene todos los códigos.
    """
    print("\n--- Paso 5 · Verificación: recorrido inorden ---")
    recorrido = arbol.inorden()
    print(f"  Inorden: {recorrido}")
    ordenado = all(recorrido[i] < recorrido[i + 1] for i in range(len(recorrido) - 1))
    completo = sorted(recorrido) == sorted(f["codigo"] for f in unicos)
    if ordenado and completo:
        print("  Verificación correcta: la lista está ordenada y no falta ningún fragmento.")
        return True
    print("  ERROR: el recorrido inorden no está ordenado o faltan fragmentos.")
    return False


def paso_consulta(arbol, unicos, posiciones):
    """Paso 6 (Consulta): busca por código y compara árbol contra búsqueda secuencial.

    Parámetros:
        arbol (ArbolBST): árbol construido.
        unicos (list): fragmentos en orden de aparición (lista para la búsqueda secuencial).
        posiciones (dict): {codigo: (estante, nivel)}.
    Retorna:
        int: número de consultas realizadas.
    """
    print("\n--- Paso 6 · Consulta: árbol vs. búsqueda secuencial ---")
    print(f"  Códigos del catálogo: {sorted(posiciones)}")
    consultas = 0
    while True:
        codigo = leer_entero("  Código a buscar (0 para terminar): ")
        if codigo == 0:
            return consultas
        consultas += 1
        fragmento, comp_arbol = arbol.buscar(codigo)
        _, comp_lista = busqueda_secuencial(unicos, codigo)
        if fragmento is None:
            print(f"  El código {codigo} no está en el catálogo.")
        else:
            print(f"  Encontrado: «{fragmento['titulo']}» ({fragmento['sala']}), "
                  f"posición {posiciones[codigo]}")
        print(f"  Comparaciones -> árbol: {comp_arbol} | búsqueda secuencial: {comp_lista}")


def sala_central(estado):
    """Sala Central: ejecuta «La Reconstrucción del Catálogo» (6 pasos visibles).

    Parámetros:
        estado (dict): estado de la partida.
    Retorna:
        bool: True si la verificación del árbol fue correcta.
    """
    print("\n=== SALA CENTRAL: LA RECONSTRUCCIÓN DEL CATÁLOGO ===")
    fragmentos = paso_carga(estado)
    unicos, descartados = paso_depuracion(fragmentos)
    estado["inventario"] = [dict(f) for f in unicos]  # solo cuentan los fragmentos válidos
    posiciones = paso_ubicacion(unicos)
    arbol = paso_construccion(unicos)
    correcto = paso_verificacion(arbol, unicos)
    paso_consulta(arbol, unicos, posiciones)
    return correcto


# ------------------------------------------------------------------- partida
def terminar_partida(estado, victoria):
    """Cierra la partida: calcula el puntaje, lo registra y borra los temporales.

    Parámetros:
        estado (dict): estado de la partida.
        victoria (bool): True si se reconstruyó el catálogo.
    Retorna:
        None.
    """
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
        persistencia.eliminar_recolectados()
    except persistencia.ErrorPersistencia as error:
        print(f"  [Aviso] No se pudo actualizar el almacenamiento: {error}")


def jugar(estado):
    """Ciclo principal de una partida; guarda al avanzar y ante una interrupción.

    Parámetros:
        estado (dict): estado inicial o cargado de la partida.
    Retorna:
        None.
    """
    try:
        estado.setdefault("recolectados", [dict(f) for f in estado["inventario"]])
        guardar_seguro(estado)
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
    """Inicia una partida nueva (pide confirmación si ya hay una guardada).

    Parámetros:
        ninguno.
    Retorna:
        None.
    """
    if persistencia.existe_partida():
        resp = input("Ya hay una partida guardada; empezar una nueva la borrará. ¿Continuar? (s/n): ")
        if resp.strip().lower() != "s":
            return
    print("\nUna tormenta destruyó el catálogo de la biblioteca. Entras con una linterna")
    print("y el inventario vacío. Recupera los fragmentos antes de que amanezca.\n")
    nombre = leer_texto("Nombre del explorador: ")
    jugar(crear_estado(nombre))


def continuar_partida():
    """Carga la partida guardada y la reanuda; avisa si no existe o está dañada.

    Parámetros:
        ninguno.
    Retorna:
        None.
    """
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
    """Muestra la tabla de puntajes (los 10 mejores).

    Parámetros:
        ninguno.
    Retorna:
        None.
    """
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
    """Muestra el menú principal y dirige las opciones del jugador.

    Parámetros:
        ninguno.
    Retorna:
        None.
    """
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
