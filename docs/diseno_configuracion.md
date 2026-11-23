# Diseño de la pantalla de Configuración (boceto v0.5)

Las imágenes del boceto salen de `tools/boceto_configuracion.py` (`python3 -I tools/boceto_configuracion.py <carpeta_marca> <salida>`).

## Pantalla principal
Ocho tarjetas, cada una con título, signo "?", descripción, etiqueta de conteo y botón:

| Tarjeta | Qué administra |
|---|---|
| Programas | Los 25 programas de Pereira que se pueden elegir al generar un cuadro |
| Campos del cuadro maestro | Columnas del cuadro: crear, editar, eliminar y definir de dónde sale cada una |
| Fuentes de datos | Cómo se lee cada Excel: fila de encabezados, columnas, filtros; semáforo de confianza |
| Equivalencias de instituciones | Nombres distintos de una misma universidad |
| Equivalencias de programas | Nombres de programa distintos entre matriz y reportes |
| Tipos de persona | Cómo se nombra cada tipo en el cuadro (Docente saliente, Experto internacional…) |
| Reglas de cruce | Cómo se asigna cada registro a un convenio y cómo se cuenta |
| Asistente con Gemini | Ayuda opcional para emparejar columnas y nombres |

Barra inferior: **Última modificación** con el enlace **Copias y almacenamiento ›**, **Exportar / importar** y **Volver al cuadro maestro**.
La vista previa del cuadro no está aquí: vive en la ventana principal (**Previsualizar cuadro**). Los cambios se guardan al instante.

## Modal de lista editable (ejemplo: Programas)
- Encabezado con título, "?" y conteo; buscador y botón **Crear programa**.
- Lista con desplazamiento: **una fila por elemento, dentro de un input**, con lápiz (editar) y papelera (eliminar) dentro de la fila.
- Estados de fila: normal, hover (borde verde y tooltip "Editar"), edición (Enter guarda, Esc cancela) y confirmación de eliminación inline
  ("Solo se quita de la lista; tus Excel no se tocan").
- Pie: "Mostrando N de M" y botón **Listo**.
- El mismo patrón se usa en campos, equivalencias, tipos de persona y reglas.

## Asistente con Gemini
1. **Copia el mensaje** que prepara el programa (solo títulos de columnas y nombres de instituciones).
2. **Abre Gemini** en el navegador.
3. **Pega y envía** (Ctrl + V).
4. **Vuelve y pega la respuesta**; el programa muestra las sugerencias con casillas, estado ("Por confirmar" o "No coincide")
   y guarda solo las que la persona marque.

Avisos fijos: Gemini solo sugiere y no se pegan datos de personas.
