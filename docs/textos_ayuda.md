# Textos de ayuda de la ventana (signos de interrogación)

Texto de cada ayuda tal como se muestra en la ventana. Se editan aquí y se copian al programa.

## Carpeta con los Excel

Reúne en **una sola carpeta** todos los Excel que usará el programa: el de convenios y, por cada año de la vigencia, el de movilidad y los dos de internacionalización en casa.

**Por qué:** el programa lee la carpeta completa y elige solo los archivos del rango que pidas. Si están repartidos en varias carpetas no los encuentra y tendrías que buscarlos uno por uno.

**Cómo nombrarlos** (propuesta; se ajusta en Configuración):

Ejemplos: `Convenios.xlsx`, `Movilidad_2021.xlsx`, `IntCasa_2021-1.xlsx`, `IntCasa_2021-2.xlsx`

El **año debe ir en el nombre**: de ahí lo lee el programa.

**Para evitar errores**

- Cierra los Excel antes de generar.
- Un solo archivo por año y tipo: sin “copia”, “(1)” ni “final2”.
- Formato .xlsx y sin contraseña.
- Si la carpeta está en OneDrive o Drive, que los archivos estén descargados en el equipo.
- Evita símbolos como # % & en los nombres y rutas muy largas.


## Vigencia (años completos)

La vigencia se pide en **años completos**: del año inicial al año final, **ambos incluidos**. De 2019 a 2023 son 5 años.

Cada año aporta 3 archivos: la movilidad anual y los dos semestres de internacionalización en casa. Por eso **no se aceptan rangos a mitad de año**, ni fechas con día o mes, ni un solo semestre.

Si el programa te entrega fechas con mes o día, confirma con la oficina qué años corresponden antes de generar.

“Desde” no puede ser mayor que “Hasta”. No hay límite de años: de 2019 a 2026 son 8 años y 24 archivos.



## Configuración

Define **cómo lee el programa cada Excel**: columnas, filtros y reglas de cruce. Cámbiala solo si los Excel cambiaron de formato.

Dentro encontrarás el detalle de cada opción y una guía para editarla.



## Previsualizar cuadro

Muestra **cómo quedaría el cuadro** con tus archivos y la configuración actual, sin crear ningún archivo.

Sirve para detectar problemas antes de generar. Se activa al elegir la carpeta y el programa.

Dentro encontrarás las cifras, los avisos y las primeras filas del cuadro.



## Ver revisión

Informe de lo que el programa **no pudo cruzar o dejó dudoso** al generar el cuadro. Se activa después de generar.

Dentro encontrarás el detalle de cada aviso y cómo resolverlo.



## Archivos que se usarán

Es la lista de comprobación antes de generar. Cada **fila** es un año de la vigencia y cada **columna** es un archivo que el programa necesita:

- **Movilidad (anual):** movilidad entrante y saliente de personas de todo el año.
- **Int. en casa · 1.º y 2.º semestre:** internacionalización en casa, un archivo por semestre.
**Para qué sirve:** con estos archivos el programa cuenta cuántas personas, y de qué tipo, pertenecen a cada convenio del programa durante su vigencia.

**Qué significa cada marca**

- ✔ **Encontrado:** el archivo está en la carpeta y se puede leer.
- ✖ **Falta este archivo:** no se encontró o no se pudo abrir. Ese año quedará incompleto en el conteo.
**“14 de 15 encontrados”:** archivos hallados sobre los esperados. Naranja = faltan; verde = completo.

Puedes generar igual con archivos faltantes; lo que falte quedará anotado en la revisión.



## Programas

Lista de los **25 programas de Pereira** que aparecen en el desplegable **Programa** de la ventana principal. Parte de la matriz de convenios y se puede ajustar aquí.

Crea, edita o elimina programas si la oficina abre o cierra alguno.

- El nombre debe coincidir con el de la matriz. Si un reporte lo escribe distinto, resuélvelo en **Equivalencias de programas**.
- Eliminar solo quita el programa de la lista; tus Excel no se tocan.


## Campos del cuadro maestro

Define las **columnas del Excel que se genera**, en el orden en que aparecen.

- Arrastra el agarre de seis puntos para cambiar el orden.
- Cada campo indica de dónde sale: **Matriz**, **Reportes**, **Calculado** o **Vacío**.
- Los **campos base** (Institución, Resultados concretos, Vigencia y Activo) se pueden renombrar, pero no eliminar: el programa los necesita para calcular.
Los cambios se guardan al instante y se usan la próxima vez que generes.



## Fuentes de datos

Define **cómo reconoce el programa cada tipo de Excel**: matriz de convenios, movilidad e internacionalización en casa.

**Qué significa el semáforo**

- **Exacta (verde):** la columna se encontró con el nombre esperado.
- **Por confirmar (naranja):** hay una columna parecida; confirma que es la correcta.
- **Sin identificar (magenta):** elige la columna con **Elegir columna…**; queda guardada para los próximos archivos.
**Probar lectura de la carpeta** muestra cómo lee cada archivo, sin crear nada.



## Equivalencias de instituciones

Une **nombres distintos de una misma universidad**: «como aparece en el Excel» → «es esta». Sirve, por ejemplo, para un nombre con error de escritura.

Se aplica a **todos los archivos**, de este año y de otros.

- **Origen:** indica quién la creó: Tú, Gemini o Revisión (la confirmaste desde un aviso).
- Eliminarla no toca tus Excel: el programa volverá a preguntar la próxima vez que vea ese nombre.


## Equivalencias de programas

Une **nombres de programa distintos** entre la matriz de convenios y los reportes. Por ejemplo: Ingeniería Industrial Distancia = Ingeniería Industrial.

Se aplica a **todos los archivos**, de este año y de otros.

- **Origen:** indica quién la creó: Tú, Gemini o Revisión.
- Eliminarla no toca tus Excel: el programa volverá a preguntar la próxima vez que vea ese nombre.


## Tipos de persona

Cada tipo del cuadro (Docente saliente, Experto internacional…) reconoce una **lista de valores** de la columna de vínculo de los Excel.

- Quita un valor con la X y agrega otros con **Agregar valor**.
- En naranja ves los valores que el programa **vio y no reconoció**; al tocar uno se agrega al tipo.
- **Internacionalización en casa** es un tipo base: se puede renombrar, no eliminar.


## Reglas de cruce

Cómo se asigna cada registro a un convenio y cómo se cuenta. Vienen **confirmadas por la jefatura (23-nov-2026)**.

Puedes cambiarlas; lo que cambies queda marcado como **Cambiada** y se puede volver a lo confirmado con **Restablecer**.

- Lo que muestra un candado no se puede cambiar.
**Ver cómo se aplican** muestra qué decidió cada regla y qué efecto tienen tus cambios, sin crear nada.



## Asistente con Gemini

Ayuda **opcional** para emparejar columnas y nombres usando Gemini en el navegador.

- El programa prepara el mensaje con **solo títulos de columnas y nombres de instituciones**: nunca datos de personas.
- Pegas la respuesta de vuelta y marcas las sugerencias que quieres guardar.
Gemini solo sugiere: no se guarda nada sin tu confirmación.



## Vista previa del cuadro

Muestra **cómo quedaría el cuadro** con tus archivos y la configuración actual. No crea archivos ni cambia nada.

- **Las cuatro cifras:** archivos leídos, convenios en el cuadro, movilidades contadas y avisos.
- **Avisos:** se muestran los primeros; la lista completa está en Ver revisión, que existe después de generar.
- **Ver cómo se leyó cada archivo ›** abre el detalle de la lectura.
Si todo se ve bien, pulsa **Generar cuadro maestro**.



## Ver cómo se aplican

Explica **por qué el cuadro sale como sale**. Lee tus archivos solo para leer: no crea archivos ni guarda cambios.

- **Efecto de tus cambios:** compara lo confirmado por la jefatura con tus reglas actuales.
- **Qué decidió cada regla:** el resultado de cada una.
- **Ejemplos reales:** registros concretos y la regla que decidió. Lo que no se pudo asignar va a Ver revisión.
Para ver el cuadro completo usa **Previsualizar cuadro** en la ventana principal.



## Probar lectura de la carpeta

Muestra **cómo lee el programa cada archivo** de la carpeta. Es solo lectura: no crea nada.

- **Cómo se leyó:** la fuente usada, la fila de encabezados y las columnas reconocidas.
- **Estados:** Listo, Por confirmar, Sin identificar o No se encontró.
- **Arreglar ›** abre la fuente para confirmar o elegir la columna. Un archivo que no se encontró se agrega a la carpeta.


## Exportar e importar configuración

Guarda **toda la configuración en un archivo .json** (para otro equipo o como respaldo) o carga una que ya tengas.

- Incluye programas, campos, fuentes, equivalencias, tipos de persona y reglas. **No incluye** Excel, datos de personas ni cuadros ya generados.
- Al importar ves **Qué cambiaría** antes de decidir: **Reemplazar todo** o **Combinar (recomendado)**.
- Antes de importar se guarda una copia de la configuración actual.


## Copias y almacenamiento

La configuración se guarda en **dos lugares a la vez**: la carpeta del usuario y junto al programa. Al abrir se usa la más reciente.

- Si falta una copia o está dañada, se restaura desde la otra y se avisa.
- Se conservan las **últimas 10 copias de seguridad**. Restaurar pide confirmación y guarda antes la actual.
- Si la carpeta del programa no permite escribir, se usa solo la del usuario.

## Alerta al pulsar «Generar cuadro maestro»

Ventana modal: el usuario debe confirmar o cancelar. El foco inicial está en **Cancelar** (Enter cancela). Los datos del resumen son de ejemplo; en el programa salen de lo elegido.

**¿Generar el cuadro maestro?**

- Programa: Fisioterapia
- Vigencia: 2019 a 2023
- Archivos: 14 de 15 encontrados
- Configuración: modificada hoy, 13:52

> ⚠ Falta 1 de 15 archivos (Movilidad 2021). Ese año quedará incompleto en el conteo. *(solo aparece si faltan archivos)*

Se usará la **configuración de cruce de datos actual** de los Excel: las columnas, filtros y reglas guardadas en Configuración.

**Antes de continuar, ten en cuenta**

- El resultado depende de esa configuración. Si los Excel cambiaron de columnas, nombres o filtros y la configuración no se actualizó, el cuadro puede quedar **incompleto o con datos incorrectos**.
- El programa **no modifica tus Excel originales**: solo los lee y crea un archivo nuevo.
- ¿Dudas del resultado? Cancela y usa **Previsualizar cuadro**: muestra cómo quedaría sin crear ningún archivo.
- Después de generarlo, abre **Ver revisión** y confirma lo que no se pudo cruzar antes de entregar el cuadro.

*La viñeta «¿Dudas del resultado?» solo aparece si todavía no se usó Previsualizar cuadro en esta sesión; si la alerta se abre desde la propia vista previa, no se muestra.*

**¿Quieres continuar?**

Botones: [Cancelar] [Sí, generar cuadro maestro]
