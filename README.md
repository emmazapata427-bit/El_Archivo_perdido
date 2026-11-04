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
| `estructuras.py` | `Nodo` y `ArbolBST` implementados desde cero (inserción, búsqueda con conteo de comparaciones, inorden, altura) |
| `persistencia.py` | Guardado/carga de la partida en JSON y tabla de puntajes, con validación y manejo de excepciones |
| `datos/` | Se crean aquí `partida.json` y `puntajes.json` (ignorados por git) |
| `tests/` | Pruebas unitarias (`unittest`) |

## Salas y estructuras

| Sala | Estructura | Reto |
|---|---|---|
| 1 Vestíbulo | `int`, `float`, `str`, `bool` | Inspeccionar el estado del jugador y sus tipos |
| 2 Estanterías | `list` | Ordenar fichas con `sorted(key=...)` y acceder por posición |
| 3 Mapas | `tuple` (fila, columna) | Moverse en una cuadrícula reemplazando la tupla |
| 4 Fichas | `dict` | Consultar fragmentos por código con `get()` |
| 5 Sellos | `set` | Quitar duplicados y validar pistas (`&`, `-`) |
| Sala Central | BST propio | **Versión preliminar**: inserta el inventario y muestra el inorden |

Tras cada reto hay una pregunta conceptual: si se falla se pierde 1 de vida y se
cuenta un intento (se repite con otra pregunta mientras quede vida); si se
acierta se recibe el fragmento de la sala y se guarda la partida.

**Puntaje** = suma de `valor` de los fragmentos − 5 × intentos fallidos (mínimo 0).

## Persistencia

- `datos/partida.json`: jugador, inventario, sala actual e intentos. Se guarda
  tras cada sala y también si el jugador interrumpe (Ctrl+C / Ctrl+D). Se
  elimina al terminar la partida.
- `datos/puntajes.json`: los 10 mejores puntajes.
- Escritura atómica (archivo temporal + `os.replace`): un corte a mitad de
  guardado no corrompe el archivo anterior.
- Al cargar se valida la forma y los tipos del JSON. Un archivo dañado produce
  `ErrorPersistencia`, que el juego muestra como aviso sin cerrarse.

## Pendiente para la siguiente entrega

- Sala Central completa: los 6 pasos (carga desde archivo, depuración con
  conjunto, ubicación con tuplas, BST, verificación inorden, consulta con
  conteo de comparaciones).
- Medición del caso degenerado del BST (100 / 1.000 / 5.000 fragmentos,
  orden aleatorio vs. creciente). `ArbolBST.altura()` y las pruebas ya cubren
  el caso base.
