"""Experimento: comparaciones del BST frente a la búsqueda secuencial.

Para cada tamaño de catálogo se construyen dos árboles (códigos en orden
aleatorio y en orden creciente) y se busca cada código existente. Se reporta
el promedio y el máximo de comparaciones, y la altura del árbol.

Uso:  python experimento.py
"""

import random

from estructuras import ArbolBST, busqueda_secuencial

TAMANOS = (100, 1000, 5000)
SEMILLA = 2026  # fija para que los resultados sean reproducibles


def medir(codigos):
    """Mide comparaciones del BST y de la búsqueda secuencial para un orden dado.

    Parámetros:
        codigos (list): códigos únicos, en el orden en que se insertan.
    Retorna:
        dict: promedio y máximo de comparaciones del árbol y de la lista,
        y altura del árbol.
    """
    arbol = ArbolBST()
    lista = []
    for codigo in codigos:
        arbol.insertar(codigo, {"codigo": codigo})
        lista.append({"codigo": codigo})

    total_arbol = max_arbol = total_lista = max_lista = 0
    for codigo in codigos:
        _, c_arbol = arbol.buscar(codigo)
        _, c_lista = busqueda_secuencial(lista, codigo)
        total_arbol += c_arbol
        total_lista += c_lista
        max_arbol = max(max_arbol, c_arbol)
        max_lista = max(max_lista, c_lista)
    n = len(codigos)
    return {
        "prom_arbol": total_arbol / n,
        "max_arbol": max_arbol,
        "prom_lista": total_lista / n,
        "max_lista": max_lista,
        "altura": arbol.altura(),
    }


def ejecutar():
    """Ejecuta el experimento para todos los tamaños y órdenes de inserción.

    Parámetros:
        ninguno.
    Retorna:
        list: filas (dict) con tamaño, orden y métricas.
    """
    rng = random.Random(SEMILLA)
    filas = []
    for n in TAMANOS:
        base = list(range(1, n + 1))
        aleatorio = base[:]
        rng.shuffle(aleatorio)
        for orden, codigos in (("aleatorio", aleatorio), ("creciente", base)):
            fila = {"n": n, "orden": orden}
            fila.update(medir(codigos))
            filas.append(fila)
    return filas


def imprimir(filas):
    """Imprime los resultados como tabla de texto.

    Parámetros:
        filas (list): resultado de ejecutar().
    Retorna:
        None.
    """
    print(f"{'n':>6} {'orden':<10} {'prom. árbol':>12} {'máx. árbol':>11} "
          f"{'prom. lista':>12} {'máx. lista':>11} {'altura':>7}")
    for f in filas:
        print(f"{f['n']:>6} {f['orden']:<10} {f['prom_arbol']:>12.2f} {f['max_arbol']:>11} "
              f"{f['prom_lista']:>12.2f} {f['max_lista']:>11} {f['altura']:>7}")


if __name__ == "__main__":
    imprimir(ejecutar())
