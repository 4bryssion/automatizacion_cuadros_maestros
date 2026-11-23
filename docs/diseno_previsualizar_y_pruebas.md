# Previsualizar cuadro, pruebas, exportar/importar y copias

Boceto v1.0. Todas las imágenes están en [`mockups/`](../mockups/) y se regeneran con `tools/boceto_todos.py`. Cómo se guarda la configuración está en [decisiones_de_proyecto.md](decisiones_de_proyecto.md).

## Cada prueba vive donde se usa

Hay tres pruebas distintas, todas de solo lectura (no crean archivos ni cambian la configuración):

| Prueba | Dónde está | Qué responde |
|---|---|---|
| **Previsualizar cuadro** | Ventana principal, junto a Generar cuadro maestro | ¿Cómo quedaría el cuadro con mis archivos y mi configuración? |
| **Ver cómo se aplican** | Configuración › Reglas de cruce | ¿Qué decidió cada regla y qué efecto tienen mis cambios? |
| **Probar lectura de la carpeta** | Configuración › Fuentes de datos | ¿Cómo lee el programa cada archivo? |

Se enlazan entre sí: la vista previa del cuadro tiene un enlace **Ver cómo se leyó cada archivo ›** que abre la prueba de lectura.

## Previsualizar cuadro (ventana principal)

- Botón secundario junto a **Generar cuadro maestro**, con su "?". Se activa al elegir carpeta y programa. Imagen: `modal_previsualizar_cuadro.png`.
- Etiqueta **Solo vista previa**, contexto (programa, vigencia, carpeta) y un aviso que repite que no crea nada.
- Cuatro cifras: archivos leídos, convenios en el cuadro, movilidades contadas y avisos para revisar (7 en el ejemplo, los mismos de Ver revisión).
- **Lectura de archivos** en una sola línea (listos, por confirmar, sin identificar, no se encontró) y el enlace al detalle.
- **Avisos de la vista previa:** los primeros, cada uno con el **mismo botón de acción** que en Ver revisión (Abrir Convenios.xlsx, Abrir carpeta, Elegir institución…).
  Así se pueden resolver antes de generar. El resto se ve completo en Ver revisión, después de generar. Los avisos solo informativos no llevan botón.
- **Así quedaría el cuadro:** primeras filas con el formato del cuadro final.
- Botones: **Cerrar**, **Volver a leer los archivos** (después de corregir un aviso) y **Generar cuadro maestro** (abre la alerta de confirmación;
  como ya se previsualizó, la alerta no repite la sugerencia de previsualizar).
- Los botones de los avisos y **Ver cómo se leyó cada archivo ›** abren su modal **encima de la vista previa** (imagen `vista_previa_con_lectura_encima.png`).
  El botón final del modal dice a dónde se vuelve (**Volver a la vista previa**).

## Ver cómo se aplican (Reglas de cruce)

Descrito en [diseno_reglas_de_cruce.md](diseno_reglas_de_cruce.md). Imagen: `modal_reglas_ver_como_se_aplican.png`.

## Probar lectura de la carpeta (Fuentes de datos)

- Imagen: `modal_fuentes_probar_lectura.png`. Contexto: vigencia y carpeta.
- Resumen de estados y filtro **Todos / Con problemas**. Si se abre desde la vista previa, el botón final es **Volver a la vista previa**.
- Tabla: archivo, cómo se leyó (fuente), fila de encabezados, columnas reconocidas y estado. Los que tienen problema ofrecen **Arreglar ›**,
  que abre la fuente para confirmar o elegir la columna. Un archivo que no se encontró no tiene acción: se agrega a la carpeta.

## Exportar e importar configuración

Imagen: `modal_exportar_importar.png`. Se abre desde **Exportar / importar** en Configuración.

- **Exportar:** un solo archivo `.json` con programas, campos, fuentes, equivalencias, tipos de persona y reglas de cruce, con cuántos hay de cada uno.
  Nombre editable y **Elegir carpeta…** / **Exportar**. Aviso de lo que no incluye: Excel, datos de personas ni cuadros ya generados.
- **Importar:** **Elegir archivo…** muestra nombre, fecha y versión; la tabla **Qué cambiaría** compara Hoy contra Archivo
  (Igual, +n, n distinta); se elige **Reemplazar todo** o **Combinar (recomendado)**. Antes de importar se guarda una copia de la actual.
- Los botones de ambos paneles van en una fila común, a la misma altura.

## Copias y almacenamiento

Imagen: `modal_copias_y_almacenamiento.png`. Se abre desde el enlace **Copias y almacenamiento ›** de la barra inferior de Configuración.

- Los **dos lugares** donde se guarda (carpeta del usuario y junto al programa): ruta, hora, estado (En uso, Al día) y **Abrir carpeta**.
- Aviso: al abrir se usa la copia más reciente; si falta una o está dañada, se restaura desde la otra y se avisa.
- **Copias de seguridad:** las últimas 10, con fecha y motivo (automática, antes de importar, creada por ti), **Restaurar** con confirmación
  (la configuración actual se guarda antes como copia nueva) y **Crear copia ahora**.
