"""Estructuras propias del proyecto: nodo y árbol binario de búsqueda (BST).

El árbol se indexa por el ``codigo`` del fragmento. Todas las operaciones son
iterativas (no recursivas) para que el caso degenerado (inserción en orden
creciente) no agote el límite de recursión de Python.
"""


class Nodo:
    """Nodo del BST: guarda la clave (codigo) y el fragmento completo."""

    def __init__(self, codigo, fragmento):
        self.codigo = codigo
        self.fragmento = fragmento
        self.izquierdo = None
        self.derecho = None


class ArbolBST:
    """Árbol binario de búsqueda sin códigos repetidos."""

    def __init__(self):
        self.raiz = None
        self.tamano = 0

    def insertar(self, codigo, fragmento):
        """Inserta un fragmento. Devuelve False si el código ya existía."""
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
        """Busca por código. Devuelve (fragmento o None, comparaciones)."""
        actual = self.raiz
        comparaciones = 0
        while actual is not None:
            comparaciones += 1
            if codigo == actual.codigo:
                return actual.fragmento, comparaciones
            actual = actual.izquierdo if codigo < actual.codigo else actual.derecho
        return None, comparaciones

    def inorden(self):
        """Lista de códigos en orden ascendente (recorrido inorden iterativo)."""
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
        """Altura del árbol (0 si está vacío); útil para medir el degenerado."""
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
        return self.tamano
