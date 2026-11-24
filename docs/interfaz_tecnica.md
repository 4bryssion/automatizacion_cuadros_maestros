# Interfaz (técnico)

Código: `src/cuadro_maestro/interfaz/`. Se abre con `python -m cuadro_maestro` (en el .exe, al hacer doble clic).
Pruebas: `tests/test_interfaz.py` (la lógica sin Tkinter y una prueba de arranque si hay pantalla).

| Archivo | Qué tiene |
|---|---|
| `app.py` | Arranque: tipografías, configuración (avisos 46 y 47), estado guardado y carpeta perdida (48) |
| `ventana.py` | Ventana principal (mockups 01, 02, 34, 35, 39, 40), con la fecha de modificación de la matriz |
| `dialogos.py` | Confirmar (03), progreso con cancelar (30), cuadro generado (31, 33), generación detenida (43-45), avisos (46-49) |
| `revision.py` | Ver revisión (10-12, 41), Elegir institución (28), salir con cambios sin incluir (13) |
| `flujo.py` | Generar desde cualquier pantalla (confirmar, progreso, errores) y guardar la última generación |
| `modelo.py` | Lógica de la ventana sin Tkinter: tabla de archivos, «x de y encontrados», mensajes, cuándo se puede generar |
| `tema.py` | Colores y estados del manual, Brown Std, botones, enlaces, «?» con su ayuda, símbolos dibujados |
| `ayudas.py` | Textos de los «?» (los mismos de `docs/textos_ayuda.md`) |
| `sistema.py` | Abrir un archivo o carpeta con el programa de Windows |

## Decisiones

- **Símbolos dibujados** (✓, ✗, !, i, anillo de progreso): se dibujan con figuras y no con letras, para que se vean
  igual aunque la tipografía no traiga esos símbolos.
- **Brown Std** se carga solo para el programa con `AddFontResourceExW` (privada, sin instalar). Si no está, Segoe UI.
  Los archivos de marca (logotipo, tipografías, logo del CNA) viven en `assets/`, que no se sube al repositorio.
- **Generación en otro hilo:** la ventana sigue respondiendo; el avance llega por una cola. Cancelar (o la X) es inmediato.
- **Lo que recuerda la ventana** (carpeta, programa, vigencia y la última generación) se guarda en `estado.json` en los
  mismos dos lugares que la configuración; gana el más reciente.
- **Ventana angosta** (menos de 760 px): Programa y Vigencia se apilan, la tabla muestra solo las marcas y el texto de lo
  que falta, y la fecha de la matriz pasa debajo del nombre.
- Los avisos de arranque se muestran sin ventana dueña (la principal aún no está visible), centrados en la pantalla.

## Capturas en Windows

`tools/captura_ventana.py <carpeta>` abre la interfaz con la muestra inventada y guarda una imagen de cada ventana.
GitHub Actions lo corre en Windows en cada push y las sube como artefacto «capturas-windows» (sin la tipografía de
marca ni el logo, que no están en el repositorio).

## Ver revisión y cambios sin incluir

La lógica está en `src/cuadro_maestro/revision.py` (se prueba sin ventanas en `tests/test_revision.py`):

- Con la última generación se guardan sus avisos, una huella de cada fila del cuadro y de cada sección de la
  configuración. Ver revisión funciona al reabrir el programa sin volver a leer.
- **Recargar archivos** lee y cruza de nuevo sin escribir; compara los avisos por su clave (resueltos, siguen, nuevos) y
  cuenta las filas del cuadro que cambiarían. Si un archivo no se puede leer, muestra la Hoja de errores.
- **Cambios sin incluir** = alguna fila cambiaría, o la configuración cambió después de generar. Se guarda al instante.
- Con cambios sin incluir: volver al cuadro maestro o cerrar la ventana obliga a generar (13); al reabrir aparece el aviso
  36; cambiar carpeta, programa o vigencia pide generar antes o cancelar el cambio (38). Si la generación falla (no si
  se cancela) se deja salir y lo pendiente queda guardado.
- **Resolver aquí:** Elegir institución guarda una equivalencia de instituciones (origen Revisión); Confirmar sugerencia
  guarda la columna elegida en Fuentes de datos, la columna del programa o una equivalencia de programas. Los botones que
  abren Configuración (Fuentes, Programas, Tipos, Gemini) quedan desactivados hasta que exista esa pantalla.
- Generar de nuevo usa el programa, la vigencia y la carpeta del último cuadro, pasa por la alerta y muestra el mockup 32.

## Pendiente

Previsualizar cuadro, Configuración (con sus modales), Confirmar sugerencias en bloque (29) y el empaquetado en .exe.
