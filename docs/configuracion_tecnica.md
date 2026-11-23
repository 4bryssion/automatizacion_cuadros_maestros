# Configuración: archivo, guardado doble y copias (técnico)

Código: `src/cuadro_maestro/configuracion/`. Pruebas: `tests/test_configuracion.py`. Este documento es para quien mantenga
el programa; lo que ve la persona usuaria está en [diseno_errores.md](diseno_errores.md) y
[diseno_previsualizar_y_pruebas.md](diseno_previsualizar_y_pruebas.md).

## Dónde se guarda

| Lugar | Ruta | Para qué |
|---|---|---|
| Carpeta del usuario | `%APPDATA%\Cuadro maestro internacional\configuracion.json` | Copia principal |
| Junto al programa | `<carpeta del .exe>\Configuración\configuracion.json` | Sobrevive si el equipo borra el perfil; viaja con el programa si se copia la carpeta |

Cada lugar tiene su subcarpeta `copias\` con las copias de seguridad (las mismas en los dos). Si se ejecuta desde el código
fuente, «junto al programa» es la carpeta `Configuración/` en la raíz del repositorio (está en `.gitignore`).

## El archivo

JSON en UTF-8. Metadatos: `formato` (`cuadro-maestro-configuracion`), `version_esquema` (hoy 1), `guardado_en`
(fecha y hora UTC con microsegundos), `revision` (sube en cada guardado) y `version_programa`. Secciones:

| Sección | Contenido |
|---|---|
| `programas` | Los 25 programas de Pereira: nombre en pantalla y encabezado exacto de su columna en la matriz |
| `campos` | Columnas del cuadro: nombre, fuente (`matriz`, `reportes`, `calculado`, `vacio`), dato, tipo y si es campo base |
| `fuentes` | Matriz, Movilidad e Internacionalización en casa: cómo se reconoce el archivo, hoja preferida, fila de encabezados, sinónimos de cada columna (normalizados) y la columna elegida por la persona, filtros |
| `equivalencias_instituciones`, `equivalencias_programas` | Pares «como aparece» → «es», con origen `tu`, `gemini` o `revision` |
| `tipos_persona` | Nombre en el cuadro y valores del vínculo que lo identifican |
| `reglas` | Las 5 reglas confirmadas el 23-nov-2026 con sus opciones |

La configuración inicial está en `valores_iniciales.py`; salió de los encabezados de los Excel reales, nunca de filas de datos.
La configuración no guarda datos de personas.

## Al abrir (`AlmacenConfiguracion.cargar`)

1. Se prueba si cada lugar permite escribir y se lee y valida cada copia: `ok`, `falta`, `danada` o `version_nueva`.
2. Una copia ilegible se guarda aparte como copia de seguridad (motivo `danada` o `version_nueva`) antes de que nada la sobrescriba; si el mismo contenido ya se había apartado, no se repite.
3. Situación resultante (cada una corresponde a un aviso):

| Situación | Cuándo | Aviso |
|---|---|---|
| `primera_vez` | No hay copias ni copias de seguridad | Ninguno (mockup 34). Se escribe la configuración inicial en los dos lugares |
| `normal` | Las dos copias iguales, o la del programa no se puede escribir | Ninguno |
| `restaurada` | Una copia faltaba o no se podía leer y se reescribió con la otra | Mockup 46 |
| `distintas` | Las dos válidas y con contenido distinto | Informativo: se usó la más reciente. La otra se guarda como copia `descartada` |
| `no_encontrada` | Ninguna copia se pudo leer | Mockup 47. No se escribe nada hasta que la persona elija `restaurar(copia)` o `seguir_con_la_inicial()` |

«Más reciente» se decide por `guardado_en` dentro del archivo (y `revision` si empatan), nunca por la fecha del archivo en Windows.

## Al guardar (`guardar`)

- Se valida el documento completo; si no es válido no se escribe nada (error de programación, no de la persona).
- Antes del **primer cambio de cada sesión** se crea una copia `automatica` con lo que había. Escribir la configuración inicial no cuenta como cambio.
- Se escribe en los dos lugares con `escribir_atomico`: archivo temporal en la misma carpeta, `fsync` y renombrado. En Windows se reintenta el renombrado unas veces porque un antivirus puede tener el archivo abierto un instante.
- Si un lugar falla se sigue con el otro; si fallan los dos, `ErrorDeGuardado`.

## Copias de seguridad

- Nombre `AAAAMMDD-HHMMSS-ffffff_<motivo>.json`, con la configuración completa o, si era ilegible, su contenido crudo y su huella SHA-256.
- Motivos: `automatica`, `antes_de_importar`, `antes_de_restaurar`, `creada_por_ti`, `danada`, `version_nueva`, `descartada`.
- Se conservan las 10 más recientes en cada lugar. `copias_de_seguridad()` junta las de los dos lugares sin repetir.
- `restaurar(copia)` guarda antes la configuración actual como `antes_de_restaurar`.

## Cambios de esquema

Si un día cambia la estructura, se sube `VERSION_ESQUEMA` y se agrega el paso de migración en `esquema.migrar`. Un archivo
de una versión más nueva que la del programa no se interpreta ni se sobrescribe sin guardarlo aparte.
