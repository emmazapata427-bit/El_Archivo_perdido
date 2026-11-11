# El Archivo Perdido

Juego serio de consola para aprender estructuras de datos en Python.
**Estructuras de Datos 2026-2 · Proyecto Integrador · Grupo 11**
Universidad de San Buenaventura, Seccional Medellín.

Cristian Camilo Vega · Emmanuel Zapata Isaza · Nicolas Lopera Arroyave

## Ejecutar

Requiere Python 3.8+ y **ninguna dependencia externa**.

```bash
python juego.py
```

## Pruebas

```bash
python -m unittest discover -s tests -t .
```

## Estructura del repositorio

| Archivo | Contenido |
|---|---|
| `juego.py` | Menús, salas 1–5, preguntas, puntaje y ciclo de partida |
| `estructuras.py` | `Nodo` y `ArbolBST` implementados desde cero (inserción, búsqueda con conteo de comparaciones, inorden, altura) y `busqueda_secuencial` de referencia |
| `persistencia.py` | Guardado/carga de la partida en JSON y tabla de puntajes, con validación y manejo de excepciones |
| `experimento.py` | Compara comparaciones del BST vs. búsqueda secuencial (100, 1.000 y 5.000 fragmentos; orden aleatorio y creciente) |
| `datos/` | Se crean aquí `partida.json`, `recolectados.json` y `puntajes.json` (ignorados por git) |
| `DECLARACION_USO_IA.md` | Declaración del uso de herramientas de IA |
| `tests/` | Pruebas unitarias (`unittest`) |

## Salas y estructuras

| Sala | Estructura | Reto |
|---|---|---|
| 1 Vestíbulo | `int`, `float`, `str`, `bool` | Inspeccionar el estado del jugador y sus tipos |
| 2 Estanterías | `list` | Ordenar fichas con `sorted(key=...)` y acceder por posición |
| 3 Mapas | `tuple` (fila, columna) | Moverse en una cuadrícula reemplazando la tupla |
| 4 Fichas | `dict` | Consultar fragmentos por código con `get()` |
| 5 Sellos | `set` | Quitar duplicados y validar pistas (`&`, `-`) |
| Sala Central | BST propio | «La Reconstrucción del Catálogo»: 6 pasos (ver abajo) |

Tras cada reto hay una pregunta conceptual: si se falla se pierde 1 de vida y se
cuenta un intento (se repite con otra pregunta mientras quede vida); si se
acierta se recibe el fragmento de la sala y se guarda la partida.

**Puntaje** = suma de `valor` de los fragmentos − 5 × intentos fallidos (mínimo 0).

## La Reconstrucción del Catálogo (Sala Central)

Al superar las cinco salas se ejecuta, de forma visible, esta secuencia:

1. **Carga:** lee `datos/recolectados.json` (cada fragmento es un diccionario).
2. **Depuración:** elimina repetidos con un conjunto de códigos e informa cuántos se descartaron.
3. **Ubicación:** asigna a cada fragmento una tupla `(estante, nivel)`, guardada aparte del fragmento.
4. **Construcción:** inserta los fragmentos en el BST (clave = código).
5. **Verificación:** recorre el árbol en inorden y comprueba que esté ordenado; si no, avisa del error.
6. **Consulta:** busca por código y muestra las comparaciones del árbol frente a la búsqueda secuencial.

En la sala 5 el explorador halla una copia mojada de un fragmento ya recogido, para que la depuración tenga algo que descartar.

## Persistencia

- `datos/partida.json`: jugador, inventario, recolectados, sala actual e intentos. Se guarda
  tras cada sala y también si el jugador interrumpe (Ctrl+C / Ctrl+D). Se elimina al terminar.
- `datos/recolectados.json`: fragmentos recogidos (puede tener repetidos); lo lee la Sala Central.
- `datos/puntajes.json`: los 10 mejores puntajes.
- Escritura atómica (archivo temporal + `os.replace`): un corte a mitad de
  guardado no corrompe el archivo anterior.
- Al cargar se valida la forma y los tipos del JSON. Un archivo dañado produce
  `ErrorPersistencia`, que el juego muestra como aviso sin cerrarse.

## Experimento de búsquedas

```bash
python experimento.py
```

Imprime promedio y máximo de comparaciones del árbol y de la lista, y la altura del árbol,
para 100, 1.000 y 5.000 fragmentos insertados en orden aleatorio y en orden creciente
(semilla fija 2026 para que sea reproducible).
