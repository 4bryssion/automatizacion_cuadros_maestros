# Interfaz (técnico)

Código: `src/cuadro_maestro/interfaz/`. Se abre con `python -m cuadro_maestro` (en el .exe, al hacer doble clic).
Pruebas: `tests/test_interfaz.py` (la lógica sin Tkinter y una prueba de arranque si hay pantalla).

| Archivo | Qué tiene |
|---|---|
| `app.py` | Arranque: tipografías, configuración (avisos 46 y 47), estado guardado y carpeta perdida (48) |
| `ventana.py` | Ventana principal (mockups 01, 02, 34, 35, 39, 40), con la fecha de modificación de la matriz |
| `dialogos.py` | Confirmar (03), progreso con cancelar (30), cuadro generado (31, 33), generación detenida (43-45), avisos (46-49) |
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

## Pendiente

Previsualizar cuadro, Configuración y Ver revisión (con Recargar, Elegir institución y Confirmar sugerencias), el aviso
de cambios sin incluir al salir o al cambiar carpeta, programa o vigencia, y el empaquetado en .exe.
