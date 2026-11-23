# Hoja de errores y avisos de arranque

Boceto v0.13. Imágenes generadas con `tools/boceto_errores.py` (`python3 -I tools/boceto_errores.py <carpeta_marca> <salida>`).

## Generación detenida y Hoja de errores (43, 44, 45)

Cuando la generación no puede terminar se abre una sola ventana, "La generación se detuvo", con tres partes: los cinco pasos (el que falló en magenta, los siguientes "No se llegó"), la **Hoja de errores** y los botones.

- **Siempre:** no se crea ningún archivo, los cambios pendientes siguen pendientes y los Excel originales no se tocan.
- **Hoja de errores:** lista con todo lo que impide generar. Cada error es una tarjeta con **Dónde / Qué pasó / Qué hacer** y botones de ayuda (**Abrir carpeta**, **Abrir Convenios.xlsx**, **Abrir Equivalencias de programas**).
- **Botones:** **Reintentar** (principal), **Cerrar** y **Copiar detalle del error** (texto plano con archivo, paso y causa, para enviarlo a Sistemas).
- **Lectura (43):** los pasos 1 a 3 leen todos sus archivos y recogen todos los problemas; se detiene al final del paso 3, para corregirlos de una vez. Causas: archivo en uso, con contraseña, dañado o no es un .xlsx de verdad.
- **Escritura (44):** el cuadro se escribe en un archivo temporal y se renombra al final. Si Windows no deja crearlo (sin permiso o disco lleno), el temporal se borra y no queda nada a medias.
- **Sin convenios (45):** se detiene en el paso 1 con el mismo aviso de la vista previa (mockup 42).

### Reglas

- **Un archivo que existe pero no se puede leer detiene la generación.** No se omite en silencio, porque un cuadro con datos faltantes sin que se note sería peor que no tener cuadro. Un archivo que falta sigue siendo solo un aviso.
- **Nombre repetido:** si dos cuadros se generan en el mismo minuto, el segundo lleva ` (2)` al final del nombre (`… 1432 (2).xlsx`), y así sucesivamente. Nunca se sobrescribe.
- **Excel abierto:** Windows a veces deja leer un archivo abierto. Si existe `~$nombre.xlsx` junto al Excel, se muestra un aviso informativo (gris) en la revisión: "Este archivo está abierto en Excel; lo que no se haya guardado no se lee". No detiene la generación.
- La vista previa y "Probar lectura de la carpeta" muestran los mismos errores, con los mismos textos.

## Avisos al abrir el programa (46, 47, 48)

- **Configuración restaurada (46):** informativo (icono verde). La copia de AppData estaba dañada o faltaba y se restauró desde la copia junto al programa. Muestra el estado de cada copia y la fecha de la usada. La copia dañada se guarda aparte y cuenta entre las 10 copias. Botones: **Entendido** y **Ver copias de seguridad**.
- **Configuración no encontrada (47):** aviso naranja. Ninguna de las dos copias se pudo leer; mientras se decide, el programa usa la configuración inicial. Lista las copias de seguridad encontradas, con la más reciente marcada. Botones: **Restaurar la más reciente**, **Elegir otra copia…** y **Seguir con la inicial**. Si no hay copias de seguridad, el aviso solo informa que se cargó la configuración inicial y tiene el botón **Entendido**.
- **Carpeta no encontrada (48):** la carpeta de la vez pasada ya no existe (disco, USB o red desconectados, o cambió de nombre). Se conservan programa y vigencia. Botones: **Elegir otra carpeta…**, **Reintentar** y **Cerrar**. El último cuadro estaba en esa carpeta y no se podrá abrir hasta que vuelva.

## Abrir un cuadro que ya no está (49)

Si **Abrir cuadro** (franja "Último cuadro" o ventanas de cuadro generado) no encuentra el archivo, se muestra "No se encontró el cuadro" con el nombre y la carpeta. Botones: **Generar cuadro de nuevo** (crea un archivo nuevo), **Abrir carpeta** y **Cerrar**. La revisión y la configuración no cambian.

## Imágenes

| Archivo | Qué muestra |
|---|---|
| `43_generacion_detenida_lectura.png` | Tres errores de lectura: en uso, con contraseña, dañado |
| `44_generacion_detenida_escritura.png` | No se pudo guardar el cuadro |
| `45_generacion_detenida_sin_convenios.png` | Programa sin convenios al generar directo |
| `46_configuracion_restaurada.png` | Aviso de configuración restaurada desde la otra copia |
| `47_configuracion_perdida.png` | Ninguna copia legible; copias de seguridad disponibles |
| `48_carpeta_no_encontrada.png` | La carpeta de la vez pasada no existe |
| `49_cuadro_no_encontrado.png` | El último cuadro ya no está en su carpeta |
