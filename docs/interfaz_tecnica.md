# Interfaz (técnico)

Código: `src/cuadro_maestro/interfaz/`. Se abre con `python -m cuadro_maestro` (en el .exe, al hacer doble clic).
Pruebas: `tests/test_interfaz.py` (la lógica sin Tkinter y una prueba de arranque si hay pantalla).

| Archivo | Qué tiene |
|---|---|
| `app.py` | Arranque: tipografías, configuración (avisos 46 y 47), estado guardado y carpeta perdida (48) |
| `ventana.py` | Ventana principal (mockups 01, 02, 34, 35, 39, 40), con la fecha de modificación de la matriz |
| `dialogos.py` | Confirmar (03), progreso con cancelar (30), cuadro generado (31, 33), generación detenida (43-45), avisos (46-49) |
| `revision.py` | Ver revisión (10-12, 41), Elegir institución (28), salir con cambios sin incluir (13) |
| `vista_previa.py` | Previsualizar cuadro (20, 42): lee y cruza sin crear nada; avisos con su botón; primeras filas |
| `configuracion.py` | Configuración (06) y sus modales: Programas (07), Equivalencias (16, 17), Tipos (18), Copias (24) |
| `fuentes.py` | Fuentes de datos (15), Elegir columna… y Probar lectura de la carpeta (22, también encima de la vista previa: 27) |
| `campos.py` | Campos del cuadro maestro (14): ordenar arrastrando, editor en la fila, campos base con candado |
| `reglas.py` | Reglas de cruce (19): Confirmada / Cambiada, restablecer una o todas; Ver cómo se aplican (21) |
| `intercambio.py` | Exportar e importar configuración (23) |
| `gemini.py` | Asistente con Gemini (08, 09) y Confirmar sugerencias del programa (29) |
| `flujo.py` | Generar desde cualquier pantalla (confirmar, progreso, errores) y guardar la última generación |
| `modelo.py` | Lógica de la ventana sin Tkinter: tabla de archivos, «x de y encontrados», mensajes, cuándo se puede generar |
| `tema.py` | Colores y estados del manual, Brown Std, botones, enlaces, «?» con su ayuda, símbolos dibujados |
| `ayudas.py` | Textos de los «?» (los mismos de `docs/textos_ayuda.md`) |
| `sistema.py` | Abrir un archivo o carpeta con el programa de Windows |

## Decisiones

- **Igual a los mockups (25-nov-2026):** botones, campos, listas, cajas, tarjetas, chips, interruptores, casillas y
  botones de opción son redondeados y suavizados. Se dibujan con Pillow a 4× y se reducen (`graficos.py`); las cajas son
  marcos de ttk con una imagen que se estira solo por el centro (`tema.Caja`, `tema.tabla`, `tema.cabecera`,
  `tema.tarjeta`). Los iconos tienen fondo transparente: sirven sobre cualquier color, también cuando la fila cambia.
- **Tablas:** cabecera oscura con las esquinas de arriba redondeadas; la última fila o un margen abajo deja ver las
  esquinas de abajo. Las rejillas (ventana principal, vista previa) usan las mismas columnas en la cabecera y en las
  filas para que queden alineadas.
- **La rueda del ratón sobre una lista desplegable no cambia la opción:** desplaza lo que la contiene. Antes, en Reglas
  de cruce, desplazarse con la rueda cambiaba reglas sin querer.
- **Barras de desplazamiento** delgadas, redondeadas y separadas 8 px del contenido; se esconden si todo cabe.
- **Ayudas «?»:** el «?» se centra por su caja real; el panel tiene esquinas redondeadas (en Windows, fuera de ellas es
  transparente) y su ancho depende del texto (400, 480 o 560 px).
- **Fuentes de datos:** al cambiar de fuente solo se cambian las tarjetas y el detalle (el nuevo se arma y luego se
  muestra), sin vaciar la ventana; con un cambio que no requiere leer, el detalle conserva la posición.

- **Símbolos dibujados** (✓, ✗, !, i, anillo de progreso): se dibujan con figuras y no con letras, para que se vean
  igual aunque la tipografía no traiga esos símbolos.
- **Brown Std** se carga solo para el programa con `AddFontResourceExW` (privada, sin instalar). Si no está, Segoe UI.
  Los archivos de marca (logotipo, tipografías, logo del CNA) viven en `assets/`, que no se sube al repositorio.
- **Generación en otro hilo:** la ventana sigue respondiendo; el avance llega por una cola. Cancelar (o la X) es inmediato.
- **Lecturas en otro hilo** (vista previa, Fuentes, Campos, Probar lectura) con `dialogos.en_espera`. Mientras trabaja
  otro hilo se pausa el recolector de basura de Python: si recogiera allí variables de Tk de pantallas cerradas, Tcl se
  cae («Segmentation fault»). Pasaba en 2 de cada 3 corridas de las capturas; con la pausa, 0 de 6.
- **Lo que recuerda la ventana** (carpeta, programa, vigencia y la última generación) se guarda en `estado.json` en los
  mismos dos lugares que la configuración; gana el más reciente.
- **Ventana angosta** (menos de 760 px): Programa y Vigencia se apilan, la tabla muestra solo las marcas y el texto de lo
  que falta, y la fecha de la matriz pasa debajo del nombre.
- Los avisos de arranque se muestran sin ventana dueña (la principal aún no está visible), centrados en la pantalla.

## Capturas en Windows

`tools/captura_ventana.py <carpeta>` abre la interfaz con la muestra inventada y guarda una imagen de cada ventana.
GitHub Actions lo corre en Windows en cada push y las sube como artefacto «capturas-windows» (sin la tipografía de
marca ni el logo, que no están en el repositorio).

## Ver revisión y cambios sin incluir

La lógica está en `src/cuadro_maestro/revision.py` (se prueba sin ventanas en `tests/test_revision.py`):

- Con la última generación se guardan sus avisos, una huella de cada fila del cuadro y de cada sección de la
  configuración. Ver revisión funciona al reabrir el programa sin volver a leer.
- **Recargar archivos** lee y cruza de nuevo sin escribir; compara los avisos por su clave (resueltos, siguen, nuevos) y
  cuenta las filas del cuadro que cambiarían. Si un archivo no se puede leer, muestra la Hoja de errores.
- **Cambios sin incluir** = alguna fila cambiaría, o la configuración cambió después de generar. Se guarda al instante.
- Con cambios sin incluir: volver al cuadro maestro o cerrar la ventana obliga a generar (13); al reabrir aparece el aviso
  36; cambiar carpeta, programa o vigencia pide generar antes o cancelar el cambio (38). Si la generación falla (no si
  se cancela) se deja salir y lo pendiente queda guardado.
- **Resolver aquí:** Elegir institución guarda una equivalencia de instituciones (origen Revisión); Confirmar sugerencia
  guarda la columna elegida en Fuentes de datos, la columna del programa o una equivalencia de programas. «Abrir
  Fuentes de datos» abre la fuente del aviso con el dato resaltado. Solo «Preguntar a Gemini» sigue desactivado.
- Generar de nuevo usa el programa, la vigencia y la carpeta del último cuadro, pasa por la alerta y muestra el mockup 32.

## Configuración

- Cada cambio se guarda al instante en los dos lugares (`Aplicacion.guardar_config`). Si ya hay un cuadro generado, se
  marca con cambios sin incluir cuando la configuración ya no es la misma con la que se generó.
- Los modales de listas comparten la base `ModalLista`: buscador con texto guía, Crear, una fila por elemento con lápiz
  y papelera, editor dentro de la lista (Enter guarda, Esc cancela) y confirmación de eliminación en la misma fila.
- Renombrar un programa conserva su identificador (la última generación y el estado lo siguen encontrando). Un programa
  nuevo propone la columna «<nombre> - Pereira». Los tipos base y los campos base muestran candado en vez de papelera.
- Los modales se abren encima de la pantalla desde la que se piden (Configuración, Ver revisión o la vista previa).

## Fuentes de datos, Campos y Reglas

La lógica está en `src/cuadro_maestro/ajustes.py` (se prueba sin ventanas en `tests/test_ajustes.py`).

- **Fuentes de datos** lee la carpeta y la vigencia de la ventana principal (sin vigencia válida, solo la matriz) y
  muestra el peor estado de cada dato entre los archivos leídos, con el encabezado del archivo más reciente. Cada cambio
  se guarda y se vuelve a leer para mostrar cómo queda. Sin carpeta se puede configurar igual («Sin leer»).
- **Elegir columna…** lista los encabezados de los archivos leídos de esa fuente (marca la sugerida y las que ya usa otro
  dato) y permite escribir uno que no esté. Se guarda como `elegida` y tiene prioridad sobre los sinónimos.
- **Año y semestre**: «se lee el año del nombre» o «se leen año y semestre»; la matriz es siempre un solo archivo.
- **Cambiar nombre** de una fuente cambia cómo la nombran los avisos, la revisión y la Hoja de errores.
- **Probar lectura** muestra un renglón por archivo esperado: los que faltan con el nombre de ejemplo que el programa sí
  reconoce (sale de la misma función que los avisos). «Arreglar ›» abre la fuente; sirve para columnas y encabezados.
- **Campos**: un campo de la matriz puede usar cualquier columna de la matriz; si no se leía, se agrega a la fuente
  «Matriz de convenios» como dato propio (`col-…`) y se quita al borrar el campo. Las columnas de programas
  («Derecho - Bogotá») no se ofrecen. Los campos base solo se renombran.
- **Reglas**: solo se ofrecen las opciones que el motor aplica (vigentes/vencidos con o sin resultados, preferido
  específico, marco o ninguno, desempate, fecha de fin, varios programas). Lo fijo se muestra con candado.

## Ver cómo se aplican las reglas

Lee la carpeta, el programa y la vigencia de la ventana principal y cruza dos veces: con las reglas confirmadas y con
las de hoy (`ajustes.aplicar_reglas`). Muestra la diferencia en cuatro cifras, una frase con el efecto, qué decidió cada
regla y un ejemplo real por cada clase de decisión. Las cifras y los ejemplos los anota el motor de cruce mientras decide
(`ResultadoCruce.traza`), así que lo que se ve es exactamente lo que se aplicaría al generar.

## Exportar e importar

`configuracion/intercambio.py`. El archivo es el mismo JSON de la configuración (formato y versión de esquema), así que
se valida igual que al abrir; uno de una versión más nueva no se importa. Exportar nunca sobrescribe («… (2).json»).
Importar deja antes una copia «Antes de importar». La tabla muestra hoy contra cómo quedaría con el modo elegido:

- **Combinar** (recomendado): agrega programas, campos (con la columna de la matriz que necesiten), equivalencias,
  tipos y valores de tipo que falten; lo tuyo gana; fuentes y reglas no cambian.
- **Reemplazar todo**: la configuración queda igual a la del archivo.

## Asistente con Gemini y Confirmar sugerencias

Lógica en `src/cuadro_maestro/sugerencias.py` (pruebas en `tests/test_sugerencias.py`).

- **Gemini (P16):** el programa no se conecta. Lee la carpeta (la del último cuadro desde Ver revisión; la de la ventana
  principal desde Configuración) y pregunta solo por lo que no reconoció: instituciones sin coincidencia (con la lista
  de instituciones de la matriz) y columnas sin identificar (con los títulos de columnas libres de ese Excel). Copia el
  mensaje y abre gemini.google.com. «Revisar qué se envía ›» deja quitar lo que no sea una institución: en los reportes
  reales la columna de institución a veces trae un cargo («Coordinador de investigación de…») o «Docente Investigadora».
- La respuesta se lee con un formato flexible («I1 → X», «1. nombre → X», «nombre -> X», con «…» al final). Solo se
  acepta una propuesta que exista tal cual en las opciones (o casi igual, 98 %); si Gemini inventa un nombre queda
  «No está en la lista» y no se puede guardar. Las instituciones se guardan con origen Gemini.
- **Confirmar sugerencias** reúne los avisos con un nombre parecido (instituciones, programas y columnas por
  confirmar). Ninguna viene marcada; «Marcar las muy parecidas» marca las de 95 % o más. Se abre con el botón
  «Confirmar sugerencias (n)» del grupo «Se resuelven aquí» en Ver revisión.

## Pendiente

El empaquetado en .exe y el manual.
