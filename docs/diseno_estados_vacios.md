# Estados vacíos

Boceto v1.0. Todas las imágenes están en [`mockups/`](../mockups/) y se regeneran con `tools/boceto_todos.py`.

## La Matriz de convenios en la ventana principal

- Se muestra como **una fila aparte** sobre la tabla de archivos: "Matriz de convenios · ✔ Convenios.xlsx" o "✖ No se encontró".
- **No suma** a "N de 15 encontrados" (ese contador es de los archivos por año). Probar lectura sí la lista junto con los demás (16 en el ejemplo).
- **Sin la Matriz no se puede generar ni previsualizar:** los botones Generar cuadro maestro y Previsualizar cuadro se desactivan, con un aviso rosado y la nota "Se activan cuando el programa encuentre la Matriz de convenios".
- Si faltan archivos por año, en cambio, se puede generar igual: lo que falta queda anotado en la revisión.

## Carpeta sin archivos reconocibles (39) y falta solo la Matriz (40)

- **39:** "0 de 15 encontrados" (magenta), Matriz sin encontrar y un cuadro "No se reconoció ningún archivo en esta carpeta" con los nombres que busca el programa (se pueden cambiar en Fuentes de datos). Acciones: **Elegir otra carpeta…**, **Abrir esta carpeta**, **Revisar nombres en Fuentes de datos** (se abre encima, sin salir de la ventana).
- **40:** la tabla normal con la fila de la Matriz en ✖ y el aviso "No se puede generar todavía: falta la Matriz de convenios…".

## Revisión sin avisos (41)

- Check grande, "No hay avisos que revisar" y los tres grupos en 0 (corrige el Excel, resuélvelo aquí, informativos).
- Botones: **Recargar archivos** (secundario) y **Abrir cuadro** (principal). No hay "Generar cuadro de nuevo" porque no hay nada que incluir.
- **Ver revisión** sigue activo aunque no haya avisos: abre esta pantalla.

## Vista previa sin convenios (42)

- Si ningún convenio de la matriz aplica al programa: "0 convenios en el cuadro" y un cuadro explicativo con dos causas posibles, cada una con su acción: la columna «Programa - Pereira» no dice APLICA (**Abrir Convenios.xlsx**) o el nombre del programa no coincide con el de la lista (**Abrir Equivalencias de programas**).
- **Generar cuadro maestro** queda desactivado: "Sin convenios no hay cuadro que generar". Si se intenta generar sin pasar por la vista previa, la generación se detiene en el primer paso con el mismo mensaje (ver Hoja de errores).

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `39_vacio_carpeta_sin_archivos.png` | Carpeta sin ningún archivo reconocible |
| `40_vacio_falta_la_matriz.png` | Falta solo la Matriz de convenios |
| `41_vacio_revision_sin_avisos.png` | Revisión sin avisos |
| `42_vacio_previsualizar_sin_convenios.png` | Vista previa con 0 convenios |
