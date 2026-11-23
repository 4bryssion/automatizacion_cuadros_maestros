# Equivalencias de instituciones, de programas y Tipos de persona

Boceto v0.8. Imágenes generadas con `tools/boceto_equivalencias_tipos.py`:
`modal_equivalencias_instituciones.png`, `modal_equivalencias_programas.png` y `modal_tipos_persona.png`.

## Equivalencias (instituciones y programas)

Los dos modales son iguales y solo cambian los textos. Cada equivalencia es un par **"como aparece en el Excel" → "es esta"**.

| Elemento | Comportamiento |
|---|---|
| Lista | Una fila por equivalencia, con buscador y botón **Crear equivalencia**. |
| Origen | Etiqueta que dice quién la creó: **Tú**, **Gemini** o **Revisión** (la confirmaste desde un aviso de Ver revisión). |
| Editar | El lápiz abre el editor dentro de la fila: el nombre tal cual aparece (con sus errores) y un desplegable con búsqueda sobre la matriz de convenios. |
| Eliminar | Confirmación en la misma fila: el programa volverá a preguntar la próxima vez que vea ese nombre; los Excel no se tocan. |
| Alcance | Se aplica a todos los archivos, de este año y de otros. |

Estas equivalencias son las que guardan las confirmaciones de Ver revisión, del asistente con Gemini y de Fuentes de datos.
La lista de programas de la matriz se administra en Configuración → Programas.

## Tipos de persona

Cada tipo del cuadro reconoce una lista de valores de la columna de vínculo de los Excel.

- Los 8 tipos de ejemplo: Estudiante saliente, Estudiante entrante, Experto internacional, Docente saliente, Docente entrante,
  Administrativo saliente, Administrativo entrante e Internacionalización en casa.
- Cada valor reconocido es una etiqueta. En el editor se quita con la X y se agrega con **Agregar valor**.
- El editor muestra los **valores que el programa vio y no reconoció** (en naranja); al tocar uno se agrega al tipo.
- **Internacionalización en casa** es un tipo base: se asigna a todo el reporte de internacionalización en casa, se puede renombrar y no se elimina.
- **Crear tipo** agrega uno nuevo.
