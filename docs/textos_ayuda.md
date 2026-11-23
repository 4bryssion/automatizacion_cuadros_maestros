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
- Después de generarlo, abre **Ver revisión** y confirma lo que no se pudo cruzar antes de entregar el cuadro.

**¿Quieres continuar?**

Botones: [Cancelar] [Sí, generar cuadro maestro]
