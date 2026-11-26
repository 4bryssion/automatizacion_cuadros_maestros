"""Textos de los signos «?» (iguales a docs/textos_ayuda.md y a los mockups).

Cada ayuda tiene título y bloques: ("p", partes) párrafo, ("b", partes) viñeta, ("h", texto) subtítulo,
("chips", [textos]), ("ok", partes) y ("mal", partes). Las partes son (texto, negrita).
"""


def R(t):
    return (t, False)


def B(t):
    return (t, True)


AYUDAS = {
    "carpeta": {
        "titulo": "Carpeta con los Excel",
        "bloques": [
            ("p", [R("Reúne en "), B("una sola carpeta"), R(" todos los Excel que usará el programa: el de convenios y, "
                    "por cada año de la vigencia, el de movilidad y los dos de internacionalización en casa.")]),
            ("p", [B("Por qué: "), R("el programa lee la carpeta completa y elige solo los archivos del rango que pidas. "
                    "Si están repartidos en varias carpetas no los encuentra y tendrías que buscarlos uno por uno.")]),
            ("p", [B("Cómo nombrarlos "), R("(propuesta; se ajusta en Configuración):")]),
            ("chips", ["Convenios.xlsx", "Movilidad_2021.xlsx", "IntCasa_2021-1.xlsx", "IntCasa_2021-2.xlsx"]),
            ("p", [R("El "), B("año debe ir en el nombre"), R(": de ahí lo lee el programa.")]),
            ("h", "Para evitar errores"),
            ("b", [R("Cierra los Excel antes de generar.")]),
            ("b", [R("Un solo archivo por año y tipo: sin “copia”, “(1)” ni “final2”.")]),
            ("b", [R("Formato .xlsx y sin contraseña.")]),
            ("b", [R("Si la carpeta está en OneDrive o Drive, que los archivos estén descargados en el equipo.")]),
            ("b", [R("Evita símbolos como # % & en los nombres y rutas muy largas.")]),
        ],
    },
    "vigencia": {
        "titulo": "Vigencia (años completos)",
        "bloques": [
            ("p", [R("La vigencia se pide en "), B("años completos"), R(": del año inicial al año final, "),
                   B("ambos incluidos"), R(". De 2019 a 2023 son 5 años.")]),
            ("p", [R("Cada año aporta 3 archivos: la movilidad anual y los dos semestres de internacionalización en casa. "
                     "Por eso "), B("no se aceptan rangos a mitad de año"), R(", ni fechas con día o mes, ni un solo semestre.")]),
            ("p", [R("Si el programa te entrega fechas con mes o día, confirma con la oficina qué años corresponden "
                     "antes de generar.")]),
            ("p", [R("“Desde” no puede ser mayor que “Hasta”. No hay límite de años: de 2019 a 2026 son 8 años y 24 archivos.")]),
        ],
    },
    "config": {
        "titulo": "Configuración",
        "bloques": [
            ("p", [R("Define "), B("cómo lee el programa cada Excel"), R(": columnas, filtros y reglas de cruce. "
                     "Cámbiala solo si los Excel cambiaron de formato.")]),
            ("p", [R("Dentro encontrarás el detalle de cada opción y una guía para editarla.")]),
        ],
    },
    "previsualizar": {
        "titulo": "Previsualizar cuadro",
        "bloques": [
            ("p", [R("Muestra "), B("cómo quedaría el cuadro"), R(" con tus archivos y la configuración actual, "
                     "sin crear ningún archivo.")]),
            ("p", [R("Sirve para detectar problemas antes de generar. Se activa al elegir la carpeta y el programa.")]),
            ("p", [R("Dentro encontrarás las cifras, los avisos y las primeras filas del cuadro.")]),
        ],
    },
    "revision": {
        "titulo": "Ver revisión",
        "bloques": [
            ("p", [R("Informe de lo que el programa "), B("no pudo cruzar o dejó dudoso"), R(" al generar el cuadro. "
                     "Se activa después de generar y se conserva al volver a abrir el programa.")]),
            ("p", [R("Dentro encontrarás el detalle de cada aviso y cómo resolverlo.")]),
        ],
    },
    "archivos": {
        "titulo": "Archivos que se usarán",
        "bloques": [
            ("p", [R("Es la lista de comprobación antes de generar. Cada "), B("fila"), R(" es un año de la vigencia y cada "),
                   B("columna"), R(" es un archivo que el programa necesita:")]),
            ("b", [B("Movilidad (anual): "), R("movilidad entrante y saliente de personas de todo el año.")]),
            ("b", [B("Int. en casa · 1.º y 2.º semestre: "), R("internacionalización en casa, un archivo por semestre.")]),
            ("p", [B("Para qué sirve: "), R("con estos archivos el programa cuenta cuántas personas, y de qué tipo, "
                     "pertenecen a cada convenio del programa durante su vigencia.")]),
            ("h", "Qué significa cada marca"),
            ("ok", [B("Encontrado: "), R("el archivo está en la carpeta y se puede leer.")]),
            ("mal", [B("Falta este archivo: "), R("no se encontró o no se pudo abrir. Ese año quedará incompleto en el conteo.")]),
            ("p", [B("“14 de 15 encontrados”: "), R("archivos hallados sobre los esperados. Naranja = faltan; verde = completo.")]),
            ("p", [R("Puedes generar igual con archivos faltantes; lo que falte quedará anotado en la revisión.")]),
            ("p", [R("Si agregas o cambias un archivo, pulsa "), B("Actualizar"),
                   R(" (también se actualiza al volver a esta ventana).")]),
        ],
    },

    # ---- ayudas de Configuración (la misma tarjeta sale en la tarjeta de Configuración y en el modal) ----
    "prog": {
        "titulo": "Programas",
        "bloques": [
            ("p", [R("Lista de los "), B("25 programas de Pereira"), R(" que aparecen en el desplegable "), B("Programa"),
                   R(" de la ventana principal. Parte de la matriz de convenios y se puede ajustar aquí.")]),
            ("p", [R("Crea, edita o elimina programas si la oficina abre o cierra alguno.")]),
            ("b", [R("El nombre debe coincidir con el de la matriz. Si un reporte lo escribe distinto, resuélvelo en "),
                   B("Equivalencias de programas"), R(".")]),
            ("b", [R("Eliminar solo quita el programa de la lista; tus Excel no se tocan.")]),
        ],
    },
    "campos": {
        "titulo": "Campos del cuadro maestro",
        "bloques": [
            ("p", [R("Define las "), B("columnas del Excel que se genera"), R(", en el orden en que aparecen.")]),
            ("b", [R("Arrastra el agarre de seis puntos para cambiar el orden.")]),
            ("b", [R("Cada campo indica de dónde sale: "), B("Matriz"), R(", "), B("Reportes"), R(", "), B("Calculado"),
                   R(" o "), B("Vacío"), R(".")]),
            ("b", [R("Los "), B("campos base"), R(" (Institución, Resultados concretos, Vigencia y Activo) se pueden renombrar, "
                    "pero no eliminar: el programa los necesita para calcular.")]),
            ("p", [R("Los cambios se guardan al instante y se usan la próxima vez que generes.")]),
        ],
    },
    "fuentes": {
        "titulo": "Fuentes de datos",
        "bloques": [
            ("p", [R("Define "), B("cómo reconoce el programa cada tipo de Excel"),
                   R(": matriz de convenios, movilidad e internacionalización en casa.")]),
            ("h", "Qué significa el semáforo"),
            ("b", [B("Exacta (verde): "), R("la columna se encontró con el nombre esperado.")]),
            ("b", [B("Por confirmar (naranja): "), R("hay una columna parecida; confirma que es la correcta.")]),
            ("b", [B("Sin identificar (magenta): "), R("elige la columna con "), B("Elegir columna…"),
                   R("; queda guardada para los próximos archivos.")]),
            ("p", [B("Probar lectura de la carpeta"), R(" muestra cómo lee cada archivo, sin crear nada.")]),
        ],
    },
    "eq_inst": {
        "titulo": "Equivalencias de instituciones",
        "bloques": [
            ("p", [R("Une "), B("nombres distintos de una misma universidad"),
                   R(": «como aparece en el Excel» → «es esta». Sirve, por ejemplo, para un nombre con error de escritura.")]),
            ("p", [R("Se aplica a "), B("todos los archivos"), R(", de este año y de otros.")]),
            ("b", [B("Origen: "), R("indica quién la creó: Tú, Gemini o Revisión (la confirmaste desde un aviso).")]),
            ("b", [R("Eliminarla no toca tus Excel: el programa volverá a preguntar la próxima vez que vea ese nombre.")]),
        ],
    },
    "eq_prog": {
        "titulo": "Equivalencias de programas",
        "bloques": [
            ("p", [R("Une "), B("nombres de programa distintos"), R(" entre la matriz de convenios y los reportes. "
                    "Por ejemplo: Ingeniería Industrial Distancia = Ingeniería Industrial.")]),
            ("p", [R("Se aplica a "), B("todos los archivos"), R(", de este año y de otros.")]),
            ("b", [B("Origen: "), R("indica quién la creó: Tú, Gemini o Revisión.")]),
            ("b", [R("Eliminarla no toca tus Excel: el programa volverá a preguntar la próxima vez que vea ese nombre.")]),
        ],
    },
    "tipos": {
        "titulo": "Tipos de persona",
        "bloques": [
            ("p", [R("Cada tipo del cuadro (Docente saliente, Experto internacional…) reconoce una "), B("lista de valores"),
                   R(" de la columna de vínculo de los Excel.")]),
            ("b", [R("Quita un valor con la X y agrega otros con "), B("Agregar valor"), R(".")]),
            ("b", [R("En naranja ves los valores que el programa "), B("vio y no reconoció"),
                   R("; al tocar uno se agrega al tipo.")]),
            ("b", [B("Internacionalización en casa"), R(" es un tipo base: se puede renombrar, no eliminar.")]),
        ],
    },
    "reglas": {
        "titulo": "Reglas de cruce",
        "bloques": [
            ("p", [R("Cómo se asigna cada registro a un convenio y cómo se cuenta. Vienen "),
                   B("confirmadas por la jefatura (23-nov-2026)"), R(".")]),
            ("p", [R("Puedes cambiarlas; lo que cambies queda marcado como "), B("Cambiada"),
                   R(" y se puede volver a lo confirmado con "), B("Restablecer"), R(".")]),
            ("b", [R("Lo que muestra un candado no se puede cambiar.")]),
            ("p", [B("Ver cómo se aplican"), R(" muestra qué decidió cada regla y qué efecto tienen tus cambios, sin crear nada.")]),
        ],
    },
    "gemini": {
        "titulo": "Asistente con Gemini",
        "bloques": [
            ("p", [R("Ayuda "), B("opcional"), R(" para emparejar columnas y nombres usando Gemini en el navegador.")]),
            ("b", [R("El programa prepara el mensaje con "), B("solo títulos de columnas y nombres de instituciones"),
                   R(": nunca datos de personas.")]),
            ("b", [R("Pegas la respuesta de vuelta y marcas las sugerencias que quieres guardar.")]),
            ("p", [R("Gemini solo sugiere: no se guarda nada sin tu confirmación.")]),
        ],
    },
    # ---- ayudas de los modales de vista previa y pruebas ----
    "vista_previa": {
        "titulo": "Vista previa del cuadro",
        "bloques": [
            ("p", [R("Muestra "), B("cómo quedaría el cuadro"),
                   R(" con tus archivos y la configuración actual. No crea archivos ni cambia nada.")]),
            ("b", [B("Las cuatro cifras: "), R("archivos leídos, convenios en el cuadro, movilidades contadas y avisos.")]),
            ("b", [B("Avisos: "), R("están todos en la lista (desplázate dentro de ella), cada uno con su botón para resolverlo aquí. "
                                     "Después de corregir, pulsa "),
                   B("Volver a leer los archivos"), R(". También quedan en Ver revisión, después de generar.")]),
            ("b", [B("Ver cómo se leyó cada archivo ›"), R(" abre el detalle de la lectura.")]),
            ("p", [R("Si todo se ve bien, pulsa "), B("Generar cuadro maestro"), R(".")]),
        ],
    },
    "aplican": {
        "titulo": "Ver cómo se aplican",
        "bloques": [
            ("p", [R("Explica "), B("por qué el cuadro sale como sale"),
                   R(". Lee tus archivos solo para leer: no crea archivos ni guarda cambios.")]),
            ("b", [B("Efecto de tus cambios: "), R("compara lo confirmado por la jefatura con tus reglas actuales.")]),
            ("b", [B("Qué decidió cada regla: "), R("el resultado de cada una.")]),
            ("b", [B("Ejemplos reales: "), R("registros concretos y la regla que decidió. Lo que no se pudo asignar va a Ver revisión.")]),
            ("p", [R("Para ver el cuadro completo usa "), B("Previsualizar cuadro"), R(" en la ventana principal.")]),
        ],
    },
    "lectura": {
        "titulo": "Probar lectura de la carpeta",
        "bloques": [
            ("p", [R("Muestra "), B("cómo lee el programa cada archivo"), R(" de la carpeta. Es solo lectura: no crea nada.")]),
            ("b", [B("Cómo se leyó: "), R("la fuente usada, la fila de encabezados y las columnas reconocidas.")]),
            ("b", [B("Estados: "), R("Listo, Por confirmar, Sin identificar o No se encontró.")]),
            ("b", [B("Arreglar ›"), R(" abre la fuente para confirmar o elegir la columna. "
                    "Un archivo que no se encontró se agrega a la carpeta.")]),
        ],
    },
    "exportar": {
        "titulo": "Exportar e importar configuración",
        "bloques": [
            ("p", [R("Guarda "), B("toda la configuración en un archivo .json"),
                   R(" (para otro equipo o como respaldo) o carga una que ya tengas.")]),
            ("b", [R("Incluye programas, campos, fuentes, equivalencias, tipos de persona y reglas. "),
                   B("No incluye"), R(" Excel, datos de personas ni cuadros ya generados.")]),
            ("b", [R("Al importar ves "), B("Qué cambiaría"), R(" antes de decidir: "), B("Reemplazar todo"), R(" o "),
                   B("Combinar (recomendado)"), R(".")]),
            ("b", [R("Antes de importar se guarda una copia de la configuración actual.")]),
        ],
    },
    "elegir_inst": {
        "titulo": "Elegir institución",
        "bloques": [
            ("p", [R("Indica a qué institución de la matriz corresponde el nombre que aparece en el Excel y que no coincidió con ninguna.")]),
            ("b", [B("Sugeridas por el programa: "), R("las más parecidas, con su porcentaje. Ninguna viene elegida: decides tú.")]),
            ("b", [R("Si no está, búscala entre todas las instituciones de la matriz.")]),
            ("b", [R("Revisa que sea la misma universidad: el parecido de nombres puede engañar.")]),
            ("p", [R("Al guardar se crea una equivalencia (origen: Revisión) que se usa en todos los archivos. Luego pulsa "),
                   B("Recargar archivos"), R(".")]),
        ],
    },
    "sugerencias": {
        "titulo": "Confirmar sugerencias del programa",
        "bloques": [
            ("p", [R("Reúne en un solo lugar los nombres que "), B("se parecen sin ser idénticos"),
                   R(": instituciones, programas y columnas. El programa los propone; "), B("tú decides"), R(".")]),
            ("b", [R("Ninguna viene marcada. "), B("Marcar las muy parecidas"), R(" marca las de 95 % o más.")]),
            ("b", [B("Cambiar ›"), R(" abre la lista para elegir otra opción.")]),
            ("b", [R("Solo se guarda lo marcado; lo demás sigue como aviso en Ver revisión.")]),
            ("p", [R("Lo guardado se puede editar o eliminar después en Equivalencias o en Fuentes de datos.")]),
        ],
    },
    "copias": {
        "titulo": "Copias y almacenamiento",
        "bloques": [
            ("p", [R("La configuración se guarda en "), B("dos lugares a la vez"),
                   R(": la carpeta del usuario y junto al programa. Al abrir se usa la más reciente.")]),
            ("b", [R("Si falta una copia o está dañada, se restaura desde la otra y se avisa.")]),
            ("b", [R("Se conservan las "), B("últimas 10 copias de seguridad"),
                   R(". Restaurar pide confirmación y guarda antes la actual.")]),
            ("b", [R("Si la carpeta del programa no permite escribir, se usa solo la del usuario.")]),
        ],
    },
}
