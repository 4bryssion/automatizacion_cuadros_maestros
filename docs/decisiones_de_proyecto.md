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
