"""Estructuras propias del proyecto: nodo, árbol binario de búsqueda (BST) y
búsqueda secuencial de referencia.

El árbol se indexa por el ``codigo`` del fragmento. Todas las operaciones son
iterativas (no recursivas) para que el caso degenerado (inserción en orden
creciente) no agote el límite de recursión de Python. No usa librerías externas.
"""


class Nodo:
    """Nodo del BST: guarda la clave (codigo) y el fragmento completo."""

    def __init__(self, codigo, fragmento):
        """Crea un nodo sin hijos.

        Parámetros:
            codigo (int): clave numérica del fragmento.
            fragmento (dict): fragmento completo asociado a la clave.
        Retorna:
            None.
        """
        self.codigo = codigo
        self.fragmento = fragmento
        self.izquierdo = None
        self.derecho = None


class ArbolBST:
    """Árbol binario de búsqueda sin códigos repetidos."""

    def __init__(self):
        """Crea un árbol vacío.

        Parámetros:
            ninguno.
        Retorna:
            None.
        """
        self.raiz = None
        self.tamano = 0

    def insertar(self, codigo, fragmento):
        """Inserta un fragmento respetando el orden del BST.

        Parámetros:
            codigo (int): clave del fragmento.
            fragmento (dict): fragmento a almacenar.
        Retorna:
            bool: True si se insertó; False si el código ya existía.
        """
        nuevo = Nodo(codigo, fragmento)
        if self.raiz is None:
            self.raiz = nuevo
            self.tamano = 1
            return True

        actual = self.raiz
        while True:
            if codigo == actual.codigo:
                return False
            if codigo < actual.codigo:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    break
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    break
                actual = actual.derecho
        self.tamano += 1
        return True

    def buscar(self, codigo):
        """Busca un fragmento por código contando las comparaciones.

        Parámetros:
            codigo (int): clave a buscar.
        Retorna:
            tuple: (fragmento o None, número de comparaciones realizadas).
        """
        actual = self.raiz
        comparaciones = 0
        while actual is not None:
            comparaciones += 1
            if codigo == actual.codigo:
                return actual.fragmento, comparaciones
            actual = actual.izquierdo if codigo < actual.codigo else actual.derecho
        return None, comparaciones

    def inorden(self):
        """Recorre el árbol en inorden (izquierdo, raíz, derecho), sin recursión.

        Parámetros:
            ninguno.
        Retorna:
            list: códigos en el orden en que se visitan (ascendente si el
            árbol está bien construido).
        """
        resultado = []
        pila = []
        actual = self.raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo
            actual = pila.pop()
            resultado.append(actual.codigo)
            actual = actual.derecho
        return resultado

    def altura(self):
        """Calcula la altura del árbol (útil para medir el caso degenerado).

        Parámetros:
            ninguno.
        Retorna:
            int: número de niveles (0 si el árbol está vacío).
        """
        if self.raiz is None:
            return 0
        altura = 0
        nivel = [self.raiz]
        while nivel:
            altura += 1
            siguiente = []
            for nodo in nivel:
                if nodo.izquierdo is not None:
                    siguiente.append(nodo.izquierdo)
                if nodo.derecho is not None:
                    siguiente.append(nodo.derecho)
            nivel = siguiente
        return altura

    def __len__(self):
        """Devuelve la cantidad de nodos.

        Parámetros:
            ninguno.
        Retorna:
            int: número de fragmentos almacenados.
        """
        return self.tamano


def busqueda_secuencial(fragmentos, codigo):
    """Busca un código recorriendo una lista, contando las comparaciones.

    Sirve de referencia para contrastar con ``ArbolBST.buscar``.

    Parámetros:
        fragmentos (list): lista de diccionarios con la clave ``codigo``.
        codigo (int): código a buscar.
    Retorna:
        tuple: (fragmento o None, número de comparaciones realizadas).
    """
    comparaciones = 0
    for fragmento in fragmentos:
        comparaciones += 1
        if fragmento["codigo"] == codigo:
            return fragmento, comparaciones
    return None, comparaciones
