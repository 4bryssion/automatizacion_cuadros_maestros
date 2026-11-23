# Probar con mis archivos, exportar/importar y copias

Boceto v0.10. Imágenes generadas con `tools/boceto_prueba_exportar_copias.py`:
`modal_probar_con_mis_archivos.png`, `modal_exportar_importar.png` y `modal_copias_y_almacenamiento.png`.
Cómo se guarda la configuración está decidido en [decisiones_de_proyecto.md](decisiones_de_proyecto.md); aquí solo se muestra.

## Probar con mis archivos

Vista previa sin efectos: lee la carpeta y muestra cómo quedaría el cuadro, **sin crear ningún archivo ni cambiar la configuración**.

- Etiqueta fija **Solo vista previa** y un aviso verde que lo repite.
- Contexto: programa, vigencia y carpeta usados.
- Cuatro cifras: archivos leídos (ej. 14 de 15), convenios en el cuadro, movilidades contadas y avisos para revisar.
- **Cómo se leyó cada archivo**: fila de encabezados, columnas reconocidas, filas leídas y estado (Listo, por confirmar, sin identificar, no se encontró).
- **Así quedaría el cuadro**: primeras filas con el mismo formato del cuadro final (institución, resultados concretos, vigencia, activo).
- Botones: **Cerrar** y **Ver avisos (n)**. Si algo no cuadra se corrige en Configuración y se vuelve a probar.

## Exportar e importar configuración

- **Exportar**: un solo archivo `.json` con programas, campos, fuentes, equivalencias, tipos de persona y reglas de cruce (con cuántos hay de cada uno).
  Nombre editable, **Elegir carpeta…** y **Exportar**. Aviso de lo que no incluye: Excel, datos de personas ni cuadros ya generados.
- **Importar**: **Elegir archivo…** muestra nombre, fecha y versión; la tabla **Qué cambiaría** compara Hoy contra Archivo por elemento
  (Igual, +n, n distinta); se elige **Reemplazar todo** o **Combinar (recomendado)**.
- Antes de importar siempre se guarda una copia de la configuración actual.

## Copias y almacenamiento

- Muestra los **dos lugares** donde se guarda (carpeta del usuario y junto al programa), con ruta, hora de guardado, estado (En uso, Al día) y **Abrir carpeta**.
- Aviso: al abrir se usa la copia más reciente; si falta una o está dañada, se restaura desde la otra y se avisa.
- **Copias de seguridad**: últimas 10, con fecha y motivo (automática, antes de importar, creada por ti), **Restaurar** con confirmación
  (la configuración actual se guarda antes como copia nueva) y **Crear copia ahora**.

## Puntos de entrada (pendiente en Configuración)

El botón **Exportar configuración** abrirá Exportar/Importar, **Probar con mis archivos** abrirá la vista previa y el texto
"Última modificación" pasará a ser un enlace a **Copias y almacenamiento**. Falta reflejarlo en `configuracion.png`.
