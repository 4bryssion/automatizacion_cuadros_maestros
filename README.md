# Automatización de cuadros maestros internacionales

Programa portable que genera el **cuadro maestro internacional** de un programa académico a partir de los
Excel de la Oficina de Relaciones Internacionales (Areandina, sede Pereira), sin instalación y sin enviar datos a internet.

> **Estado: en diseño.** Ya están definidos el diseño de la interfaz y las reglas de negocio, y hay
> prototipos de lectura y cruce de datos. Todavía no existe un ejecutable.

## Qué resuelve

Hoy el cuadro de cada programa se arma a mano cruzando tres tipos de Excel. Este programa lo hace
en minutos para cualquiera de los programas y deja un informe con todo lo que no pudo cruzar.

| Archivo de entrada | Qué aporta |
|---|---|
| **Matriz de convenios** | Convenios, tipo (marco o específico), fechas, vigencia, estado y a qué programas aplican |
| **Consolidado de movilidad** (uno por año) | Personas que salieron o llegaron: estudiantes, docentes, administrativos y expertos |
| **Reporte de internacionalización en casa** (uno por semestre) | Actividades internacionales realizadas en el campus |

Salida: un Excel con el cuadro maestro del programa (instituciones, objeto, resultados por año y tipo,
vigencia, activo o no activo) y un informe de revisión.

## Cómo se usa

1. Elegir la carpeta con los Excel.
2. Elegir el programa.
3. Indicar la vigencia en años completos (por ejemplo 2019 a 2023).
4. Revisar la tabla de archivos encontrados y los que faltan.
5. Pulsar **Generar cuadro maestro** y confirmar la alerta.
6. Abrir **Ver revisión** y resolver lo que quedó dudoso: unos avisos se corrigen en el Excel (se guarda, se cierra y se pulsa **Recargar archivos**) y otros se resuelven dentro del programa.
7. Si hubo correcciones, pulsar **Generar cuadro de nuevo**: crea un archivo nuevo y no toca el anterior.

## Principios de diseño

- **Portable:** un ejecutable de Windows que no pide instalación ni permisos de administrador. Probado en un equipo restringido (Windows muestra el aviso de SmartScreen la primera vez).
- **Local:** lee los Excel en el mismo equipo y nunca los modifica; crea archivos nuevos.
- **Se adapta a los cambios:** columnas, filtros y reglas viven en una configuración editable, no en el código. Los reportes cambian de un año a otro (fila de encabezado, columnas corridas, nombres distintos) y el programa detecta y propone el mapeo.
- **No falla en silencio:** lo dudoso va al informe de revisión. Lo exacto se aplica solo; lo parecido se propone y una persona lo confirma. Lo que se confirma queda guardado.
- **Sin datos personales en las salidas:** el cuadro y la revisión solo traen conteos y referencias a filas, nunca nombres, documentos ni correos.
- **Imagen de Areandina:** colores y tipografías según el manual de marca 2026-2027.

## Configuración

Pantalla para adaptar el programa sin tocar código:

Ocho tarjetas; cada lista se administra en un modal con una fila por elemento (editar y eliminar dentro de la fila) y un botón Crear:

1. **Programas** (25 de Pereira, tomados de la matriz).
2. **Campos del cuadro maestro:** crear, editar o eliminar columnas (directo, calculado, fijo o manual).
3. **Fuentes de datos:** columna encontrada para cada campo, con semáforo (seguro, por confirmar, no encontrado).
4. **Equivalencias de instituciones** y 5. **de programas.**
6. **Tipos de persona.**
7. **Reglas de cruce.**
8. **Asistente con Gemini** (opcional): el programa prepara un mensaje, se pega en Gemini y la respuesta se pega de vuelta; un modal lo explica en 4 pasos.

Además: exportar la configuración y probar el cruce con los archivos antes de generar. Detalle en [docs/diseno_configuracion.md](docs/diseno_configuracion.md).

## Reglas de negocio

Resumen: un registro cuenta para un convenio solo dentro de sus años de vigencia; la movilidad va al convenio
específico y la internacionalización en casa al marco; la movilidad cuenta movilidades y la internacionalización en
casa cuenta actividades. El detalle completo está en [docs/reglas_de_negocio.md](docs/reglas_de_negocio.md).

## Contenido del repositorio

| Ruta | Qué es |
|---|---|
| [docs/reglas_de_negocio.md](docs/reglas_de_negocio.md) | Reglas confirmadas por la jefatura |
| [docs/hallazgos_excels_reales.md](docs/hallazgos_excels_reales.md) | Qué se encontró en los Excel reales |
| [docs/diseno_configuracion.md](docs/diseno_configuracion.md) | Pantalla de Configuración, modales de listas y asistente con Gemini |
| [docs/decisiones_de_proyecto.md](docs/decisiones_de_proyecto.md) | Decisiones tomadas y cómo se guarda la configuración |
| [docs/diseno_campos_y_fuentes.md](docs/diseno_campos_y_fuentes.md) | Modales de Campos del cuadro maestro y Fuentes de datos |
| [docs/diseno_equivalencias_y_tipos.md](docs/diseno_equivalencias_y_tipos.md) | Modales de Equivalencias y Tipos de persona |
| [docs/diseno_reglas_de_cruce.md](docs/diseno_reglas_de_cruce.md) | Modal de Reglas de cruce: opciones y estado confirmada/cambiada |
| [docs/diseno_prueba_exportar_y_copias.md](docs/diseno_prueba_exportar_y_copias.md) | Probar con mis archivos, Exportar/Importar configuración y Copias de seguridad |
| [docs/diseno_revision.md](docs/diseno_revision.md) | Pantalla Ver revisión: avisos, cómo resolverlos y recarga |
| [docs/identidad.md](docs/identidad.md) | Colores, tipografías, estados y comportamiento responsivo |
| [docs/textos_ayuda.md](docs/textos_ayuda.md) | Textos de los signos "?" y de la alerta de confirmación |
| `tools/boceto_ventana.py` | Genera las imágenes de la ventana principal y la alerta |
| `tools/boceto_configuracion.py` | Genera las imágenes de Configuración, el modal de listas y el asistente con Gemini |
| `tools/boceto_campos_fuentes.py` | Genera las imágenes de Campos del cuadro maestro y Fuentes de datos |
| `tools/boceto_equivalencias_tipos.py` | Genera las imágenes de Equivalencias y Tipos de persona |
| `tools/boceto_reglas_de_cruce.py` | Genera la imagen de Reglas de cruce |
| `tools/boceto_prueba_exportar_copias.py` | Genera las imágenes de Probar con mis archivos, Exportar/Importar y Copias |
| `tools/boceto_revision.py` | Genera las imágenes de Ver revisión, antes y después de recargar |
| `tools/prototipo_mapeo.py` | Prueba de detección de encabezados y mapeo de columnas |
| `tools/prototipo_cruce.py` | Prueba de las reglas de cruce contra el cuadro de ejemplo |

Los logos, fuentes y Excel reales no se incluyen en el repositorio.

## Hoja de ruta

- [x] Diseño de la interfaz principal, ayudas y alerta de confirmación
- [x] Prueba de portabilidad del ejecutable en un equipo restringido
- [x] Reglas de negocio confirmadas y verificadas con los datos de 2022
- [x] Diseño de la pantalla de Configuración, los modales de listas y el asistente con Gemini
- [x] Diseño de Ver revisión con recarga de archivos
- [ ] Motor de lectura, mapeo y cruce con configuración editable
- [ ] Interfaz real (Tkinter) con la tipografía y colores de la marca
- [ ] Informe de revisión (lógica; el diseño ya está)
- [ ] Empaquetado con GitHub Actions (PyInstaller, Windows) y pruebas con datos ficticios
- [ ] Datos de ejemplo ficticios para pruebas y capacitación

## Tecnología prevista

Python con Tkinter y openpyxl, empaquetado con PyInstaller en un runner de Windows de GitHub Actions.
