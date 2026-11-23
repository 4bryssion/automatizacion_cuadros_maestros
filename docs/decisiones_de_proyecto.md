# Decisiones de proyecto

Registro de lo decidido con la persona responsable del proyecto. Las reglas de cruce y conteo están en
[reglas_de_negocio.md](reglas_de_negocio.md).

## 23-nov-2026

| Tema | Decisión |
|---|---|
| Dónde se guarda la configuración | En **dos lugares a la vez**: la carpeta de datos del usuario (`%APPDATA%`) y la carpeta donde está el programa portable. No se pudo comprobar si los equipos borran el perfil al cerrar sesión; por eso se guarda en ambos. |
| Salir con cambios sin incluir | Obligatorio generar el cuadro de nuevo (ver [diseno_revision.md](diseno_revision.md)). Excepción: si la generación falla, se deja salir y el estado pendiente se conserva. |
| Quién mantendrá el programa | Probablemente una persona del área de Sistemas (por confirmar). |
| Manual de usuario y de mantenimiento | Se redactan al final del proyecto. |
| Tipografía Brown Std dentro del .exe | Sin objeción. |
| Repositorio | Público por ahora. Por definir si se transfiere a una cuenta de la institución. |

## Cómo funciona el guardado en dos lugares

1. **Al guardar** (cada cambio, al instante): se escribe en ambos lugares. Se escribe primero un archivo temporal y luego se
   renombra, para que un corte no deje el archivo a medias.
2. **Al abrir el programa:** se lee y se valida cada copia. Se usa la **más reciente** (por la fecha guardada dentro del archivo, no
   por la fecha del archivo en Windows).
3. **Si falta una copia o está dañada:** se restaura desde la otra y se avisa en pantalla.
4. **Si la carpeta del programa no permite escribir** (por ejemplo, un disco protegido): se usa solo `%APPDATA%` y Configuración lo indica.
5. **Copias de seguridad:** se conservan las últimas 10, con opción de restaurar una desde Configuración.
6. **Si las dos copias son válidas pero distintas** (por ejemplo, el programa se copió a otro equipo): gana la más reciente y se avisa
   cuál se usó.
7. La configuración no contiene datos de personas: solo nombres de columnas, instituciones, programas, equivalencias y reglas.

## Dónde vive cada prueba (23-nov-2026)

Las pruebas son de solo lectura y cada una está en la pantalla donde se usa; no hay una sola prueba general en Configuración.

- **Previsualizar cuadro:** ventana principal, junto a Generar cuadro maestro (ver cómo quedaría el cuadro).
- **Ver cómo se aplican:** dentro de Reglas de cruce (qué decidió cada regla y qué efecto tienen los cambios).
- **Probar lectura de la carpeta:** dentro de Fuentes de datos (cómo lee el programa cada archivo).
- Detalle en [diseno_previsualizar_y_pruebas.md](diseno_previsualizar_y_pruebas.md).
- Los mockups definitivos se suben a Drive al aprobarse y, cuando todos estén definidos, al repositorio.

## Ajustes de la tarde del 23-nov-2026

- **Programas:** se trabaja con los **25 programas** de Pereira; la lista es editable en Configuración › Programas, así que el número puede cambiar sin tocar el código.
- **Ventana principal:** el botón de la carpeta se llama **Elegir carpeta…** (antes "Buscar…").
- **Alerta de confirmación:** incluye la sugerencia de usar **Previsualizar cuadro** antes de generar. Solo aparece si todavía no se usó la vista previa en esa sesión.
- **Ayudas "?":** todas las tarjetas de Configuración y sus modales, la vista previa, las pruebas, Exportar/importar y Copias tienen su texto de ayuda en [textos_ayuda.md](textos_ayuda.md). La tarjeta de Configuración y su modal muestran la misma ayuda.
- **Versión del boceto:** v0.12.

## Correcciones de flujo (23-nov-2026, tarde)

Revisión de incongruencias entre pantallas; las siete se aprobaron.

| # | Qué se detectó | Decisión |
|---|---|---|
| 1 | Ver revisión solo existía "después de generar", pero el estado de cambios pendientes se guarda y se pide al reabrir | Se guarda la **última generación** (programa, vigencia, carpeta, hora, avisos, pendientes). Ver revisión sigue activo al reabrir. |
| 2 | Los avisos de la vista previa no se podían resolver sin generar | Cada aviso lleva su botón de acción y la vista previa tiene **Volver a leer los archivos**. |
| 3 | Camino de vuelta desde Configuración | Los modales de Configuración se abren **encima** de la revisión o de la vista previa y su botón final dice a dónde vuelven. No hay "Volver a la revisión" en la pantalla de Configuración. |
| 4 | La tabla de archivos no se podía refrescar | Enlace **Actualizar**; además se actualiza al volver a la ventana. |
| 5 | Cambios de configuración posteriores a generar no obligaban a regenerar | Cuentan igual que los cambios de archivos; el modal de salida los lista. |
| 6 | "Probar con un archivo…" duplicaba la prueba de lectura | Se quitó; quedan las tres pruebas definidas. |
| 7 | Un programa nuevo en la matriz no avisaba | Nuevo aviso en Ver revisión (grupo "Resuélvelo aquí") con **Abrir Programas**. |

Otros ajustes: la sugerencia de Previsualizar en la alerta solo se muestra si no se usó la vista previa en la sesión; el aviso de "movilidades sin convenio" aparece
como informativo (gris) en todas las pantallas; versión del boceto v0.12.

## Elegir institución y Confirmar sugerencias (23-nov-2026, noche)

- **Elegir institución…** (modal, 860 px): muestra el nombre tal como viene en el Excel, un buscador y tres sugerencias con porcentaje de parecido
  (97 % «Muy parecida», 71 %, 64 %). Advierte cuando dos instituciones se parecen y pueden confundirse. La equivalencia se guarda con origen **Revisión**.
- **Confirmar sugerencias** (modal, 1100 px): confirma en bloque lo que el programa propone (institución, programa, columna). Botón **Marcar las muy parecidas**;
  las dudosas quedan sin marcar y se revisan con **Cambiar ›**.
- **Incongruencia nueva:** la lectura y la vista previa mostraban "1 por confirmar" sin aviso equivalente en la revisión. Se añadió el aviso
  **Columna por confirmar «PROGRAMA ACADÉMICO»** (grupo "Resuélvelo aquí"), con **Confirmar sugerencia** y **Abrir Fuentes de datos**.
  Los conteos quedan en **8 avisos** en la vista previa y en la revisión; tras recargar: "Antes 8, ahora 7".
- Mockups 28 y 29 subidos a Drive; 10, 11, 12, 13, 20 y 26 reemplazados.

## Generación y cuadro generado (23-nov-2026, tarde)

- **Dónde se guarda:** subcarpeta `Cuadros generados` dentro de la carpeta de los Excel; nombre `Cuadro maestro - Programa - vigencia - fecha hora.xlsx`; siempre archivo nuevo.
- **Cancelar durante la generación:** inmediato, sin crear archivo y sin cambiar la última generación guardada. La X del modal hace lo mismo.
- **Cuadro generado:** tres casos (con avisos, de nuevo desde la revisión, sin avisos); el botón principal cambia según el caso. Detalle en [diseno_generacion.md](diseno_generacion.md).
- **Ver revisión activo:** enlace verde subrayado; gris mientras no haya generación guardada.
- Alerta de confirmación: ahora dice que el archivo se crea en la subcarpeta Cuadros generados. Versión de los mockups nuevos: v0.13 (al cerrar la fase de mockups se unifica la versión en todos).

## Primera apertura y reapertura (23-nov-2026, tarde)

- Se guarda **solo la última generación** (no una por programa); la franja "Último cuadro" y Ver revisión nombran su programa.
- Al reabrir con cambios sin incluir (cierre inesperado o generación fallida) aparece un aviso con **Generar cuadro de nuevo** y **Ver revisión**; se puede cerrar y seguir en la ventana principal, con la franja naranja.
- Los cambios hechos con el programa cerrado (Excel editados) no se detectan; Previsualizar o Recargar los revelan.
- La tabla de archivos depende de carpeta y vigencia, no del programa. Detalle en [diseno_apertura.md](diseno_apertura.md).
- **Decidido:** al cambiar la **carpeta**, el **programa** o la **vigencia** con cambios sin incluir se muestra un aviso (mockup 38) con **Generar cuadro de nuevo** y **Cancelar el cambio**. Tras generar se aplica el cambio y se vuelve a leer la tabla de archivos. Sin cambios sin incluir, los tres campos se cambian libremente.

## Estados vacíos (23-nov-2026, tarde)

- **Matriz de convenios** visible en la ventana principal, como fila aparte; sin ella se desactivan Generar y Previsualizar. Los archivos por año faltantes no bloquean.
- **Carpeta sin archivos reconocibles:** cuadro con los nombres esperados y tres acciones (otra carpeta, abrir carpeta, revisar nombres en Fuentes de datos).
- **Revisión sin avisos:** pantalla propia, con Recargar archivos y Abrir cuadro.
- **Programa sin convenios:** la vista previa lo explica y bloquea Generar; la generación directa se detiene con el mismo mensaje.
- **Pendiente al cerrar la fase de mockups:** regenerar con una sola versión todos los mockups de la ventana principal (y los que la tienen de fondo) para incluir la fila de la Matriz. Detalle en [diseno_estados_vacios.md](diseno_estados_vacios.md).

## Hoja de errores y avisos de arranque (23-nov-2026, tarde)

- **Hoja de errores:** una ventana única "La generación se detuvo" con pasos, lista de errores (Dónde / Qué pasó / Qué hacer), **Reintentar**, **Cerrar** y **Copiar detalle del error**. Sin archivo creado y con los cambios pendientes intactos.
- **Archivo existente pero ilegible** (en uso, con contraseña, dañado): detiene la generación, se recogen todos los de la lectura y se muestran juntos. Un archivo ausente sigue siendo solo aviso.
- **Nombre repetido en el mismo minuto:** el segundo lleva ` (2)`; nunca se sobrescribe.
- **Excel abierto (`~$nombre.xlsx` presente):** aviso informativo gris en la revisión, sin detener la generación.
- **Al abrir:** avisos de configuración restaurada (46), configuración no encontrada con restauración de copias (47) y carpeta no encontrada (48). **Abrir cuadro** sin archivo muestra el aviso 49.
- Mockups 43 a 49 subidos a Drive. Detalle en [diseno_errores.md](diseno_errores.md).

## Cierre de la fase de mockups (23-nov-2026, tarde)

- **Boceto v1.0:** los 49 mockups se regeneraron en una sola pasada con un único pie de versión y la fila de la **Matriz de convenios** en todas las ventanas principales (y en los modales que las tienen de fondo). Se corrigió un solape del nombre de la Matriz con su visto bueno en ventanas angostas.
- Las 49 imágenes están en [`mockups/`](../mockups/) (con un índice) y en la carpeta Mockups de Drive; se generan con `tools/boceto_todos.py`.
- La fase de diseño de pantallas queda cerrada. Sigue la construcción real: esquema de configuración con guardado doble, motor de cruce, interfaz Tkinter, pruebas con datos sintéticos, empaquetado con PyInstaller y GitHub Actions, y manual al final.

## Inicio de la construcción: configuración (23-nov-2026, tarde)

- **Datos de prueba:** se autorizó apoyarse en los Excel reales (ver «Datos de prueba a partir de los Excel reales»).
- **Repositorio:** sigue en la cuenta personal mientras no haya decisión sobre la cuenta institucional.
- **Carpetas:** `%APPDATA%\Cuadro maestro internacional` y la subcarpeta `Configuración` junto al .exe; cada una con su carpeta `copias`.
- **Copia automática:** antes del primer cambio de cada sesión (no en cada cambio), para no llenar las 10 copias con un solo día de trabajo.
- **Nada se pierde al sobrescribir:** si al abrir una copia está dañada, es de una versión más nueva del programa, o es válida pero más antigua y distinta, se guarda aparte como copia de seguridad antes de reescribirla.
- **Configuración no encontrada:** no se escribe nada hasta que la persona elija restaurar una copia o seguir con la inicial.
- Las pruebas automáticas corren en Windows y Linux con GitHub Actions. Detalle técnico en [configuracion_tecnica.md](configuracion_tecnica.md).

## Datos de prueba a partir de los Excel reales (23-nov-2026, tarde)

- Autorizado por la persona responsable: las pruebas se apoyan en los Excel reales de 2022.
- `tools/anonimizar_reales.py` crea copias anonimizadas: conserva estructura y rarezas y reemplaza los datos de personas.
  Usa una lista blanca de columnas; la ciudad y el país de origen de la persona y las fechas exactas de su movilidad no
  se conservan. Quita macros, tablas dinámicas y validaciones de datos, que en los reales guardaban correos y nombres
  fuera de las celdas. La verificación revisa todo el contenido interno de cada copia y se comprobó que detecta las
  fugas en los originales. El prototipo de cruce da el mismo resultado con las copias que con los originales.
- **Decidido: las copias anonimizadas no se suben al repositorio público** (opción 1). Aunque no traen nombres ni
  correos, cada fila de movilidad conserva año, programa, institución y tipo de persona, y eso podría bastar para
  reconocer a alguien. Viven solo en el equipo local (`tests/datos/reales_anonimizados`, en `.gitignore`).
- En GitHub las pruebas usan una **muestra inventada** (`tests/muestra_sintetica.py`) con las mismas rarezas; las
  pruebas con copias o con originales (`CUADRO_EXCEL_REALES`) corren en el equipo local y en GitHub se saltan.

## Motor de lectura (23-nov-2026, tarde)

- **Nombre de la matriz:** se reconoce por contener «convenios» (sirve para `MATRIZ CONVENIOS…` y para `Convenios.xlsx`,
  como en los mockups) y se excluyen los nombres con «cuadro» o «cm», porque el cuadro hecho a mano también lleva «Convenios».
- **Dos archivos para el mismo año o semestre** (p. ej. una «Copia de…»): se usa el modificado más recientemente y la
  revisión avisa cuáles se dejaron de lado.
- **Un .xls antiguo** cuenta como «dañado o no es un .xlsx de verdad», con el mismo texto del mockup 43.
- La lectura no depende del programa: cambiar de programa no obliga a volver a leer los archivos.
- Solo se lee la carpeta elegida, sin subcarpetas. Detalle técnico en [lectura_tecnica.md](lectura_tecnica.md).
