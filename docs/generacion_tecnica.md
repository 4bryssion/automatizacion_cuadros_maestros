# Generación del cuadro (técnico)

Código: `src/cuadro_maestro/generacion/`. Pruebas: `tests/test_generacion.py`. `generar(carpeta, config, programa,
año inicial, año final)` hace los 5 pasos del modal de progreso (mockup 30) y devuelve la ruta del cuadro, el resultado
del cruce y la lectura; o lanza `GeneracionDetenida` (Hoja de errores) o `Cancelado`.

## Pasos y estados

| Paso | Qué hace | Estados posibles |
|---|---|---|
| `matriz`, `movilidad`, `ic` | Lectura (ver [lectura_tecnica.md](lectura_tecnica.md)) | hecho · con aviso («falta 2021») · error |
| `cruce` | Cruce (ver [cruce_tecnico.md](cruce_tecnico.md)) | hecho («88 convenios») · error (sin convenios) |
| `escritura` | Excel en `Cuadros generados` | hecho (nombre del archivo) · error |

Los pasos después del que falló quedan «No se llegó». La interfaz recibe cada cambio por `al_avanzar(paso, estado, texto)`.

## Cuándo se detiene (Hoja de errores)

| Caso | Paso | Tarjeta |
|---|---|---|
| Archivos que existen pero no se pueden leer (todos juntos) | el de cada archivo | Archivo en uso · Con contraseña · Dañado (mockup 43) |
| Falta la matriz | matriz | Falta la matriz |
| Ningún convenio dice APLICA para el programa | matriz | Sin convenios (mockup 45) |
| Hay convenios que aplican pero ninguno queda en el cuadro | cruce | Sin convenios |
| Windows no deja crear el archivo (permiso, disco lleno) | escritura | No se pudo escribir (mockup 44) |

Cada tarjeta trae título, dónde, qué pasó, qué hacer, botones y causa técnica. `detalle_para_sistemas` arma el texto de
«Copiar detalle del error». En ningún caso queda un archivo creado.

## El archivo

- Carpeta `Cuadros generados` dentro de la de los Excel; nombre `Cuadro maestro - <Programa> - <vigencia> - <AAAA-MM-DD> <HHMM>.xlsx`
  (la vigencia es un solo año si empieza y termina igual; se quitan los caracteres que Windows no acepta).
- Si el nombre ya existe (mismo minuto) se agrega « (2)», « (3)»…; el renombrado final nunca sobrescribe.
- Se escribe a `.~cuadro-xxxx.xlsx` en la misma carpeta y se renombra al final. Si algo falla o se cancela, el temporal se borra.

## Formato (como el cuadro hecho a mano, CNA cuadro No. 10)

- Hoja «Convenios»: títulos del CNA en las filas 1 a 3; «Convenios activos nacionales de cooperación» (fila 5) con sus
  encabezados y las filas de ejemplo 1, 2, 3, 4, ., ., N, vacías (P13); «Convenios internacionales de cooperación»
  (fila 16), encabezados en la 17 y convenios desde la 18.
- Century Gothic 10, centrado, ajuste de texto; marco exterior grueso y líneas finas por dentro; sin cuadrícula,
  zoom 70 %, A4 vertical ajustado al ancho de la página.
- Las columnas son las de Configuración › Campos del cuadro maestro: encabezado, orden, ancho y de dónde sale cada dato.
  Un campo de la matriz puede tomar cualquier dato leído de la fila del convenio (por ejemplo, el código).
- Alto de fila calculado por la cantidad de texto (12,5 puntos por línea, con margen por si falta la letra Century Gothic).
- Logo del CNA en B1 si existe `assets/logo_cna.png` (no está en el repositorio; ver decisiones).
- Hoja «Acerca de este cuadro»: programa, sede, vigencia, fecha, carpeta, archivos leídos, cifras y cantidad de avisos por
  grupo. Ninguna de las dos hojas tiene datos de personas.
