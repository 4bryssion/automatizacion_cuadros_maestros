# Identidad visual para la interfaz (resumen del Manual de marca 2026-2027)

Resumen de los datos del manual que usa la ventana del programa. Los archivos de marca
(logotipos, tipografías, manual) **no se suben al repositorio**: viven en `assets/marca/`,
que está en `.gitignore`.

## Nombre
- Nombre completo: **Fundación Universitaria del Área Andina**. Nombre de uso diario: **Areandina**.

## Colores (manual, paleta cromática)
| Uso en la ventana | Color | Hex |
|---|---|---|
| Verde principal (línea de marca, acentos) | Pantone 2287 CP | `#7FB536` |
| Llamado a la acción (botón principal) | manual: "Llamado a la acción" | `#67882C` |
| Magenta (errores, faltantes) | Pantone 225 C | `#E6007E` |
| Naranja (avisos) | Pantone 130 U | `#F59C2F` |
| Gris | — | `#606060` |
| Gris oscuro (títulos, encabezados) | manual: posgrado virtual | `#282828` |
| Negro / Blanco | — | `#000000` / `#FFFFFF` |

Contrastes medidos (WCAG; mínimo 4,5:1 texto normal, 3:1 texto grande/negrita ≥ 14 pt):
- Blanco sobre `#67882C`: 4,09 → solo con texto de 14 pt en negrita (botón principal).
- Blanco sobre `#7FB536`: 2,45 → **no usar para texto**. Negro sobre `#7FB536`: 8,57.
- Magenta sobre blanco: 4,5. Gris `#606060` sobre blanco: 6,29.
- No comunicar estado solo con color: siempre acompañar con icono y texto.

## Tipografía (Brown Std)
- Titulares y texto a resaltar: **Brown Bold** (familia `BrownStd`, estilo Bold).
- Cuerpo de texto: **Brown Regular** (familia `BrownStd`). Textos largos: **Brown Light** (familia `BrownStd Light`).
- En Windows se puede cargar la fuente solo para el programa (sin instalarla y sin permisos de
  administrador) con `AddFontResourceExW` y la marca `FR_PRIVATE`. Los archivos `.otf` viajan
  junto al programa. Si no cargan, la ventana cae a Segoe UI.

## Logotipo
- Usar solo los archivos oficiales: no redibujar, deformar, girar ni cambiar colores.
- Mínimo digital: **30 px** (logotipo) y **60 px** (isotipo). Respetar el área protegida.
- Variantes entregadas: logotipo verde, negro y blanco; isotipo verde y blanco (PNG con transparencia).
- En la ventana: logotipo verde sobre fondo blanco, arriba a la izquierda.
- El isotipo, si se usa, va siempre con el logotipo y en papel secundario.

## Decisiones de interfaz que dependen de Tkinter
- Sin esquinas redondeadas ni sombras (Tkinter estándar): campos y botones rectos.
- La barra de título la dibuja Windows; no se puede cambiar.
- Rejilla de archivos: `ttk.Treeview` o etiquetas en cuadrícula.

Boceto de referencia: `tools/render_boceto.py` (necesita los archivos de marca en `assets/marca/`).
