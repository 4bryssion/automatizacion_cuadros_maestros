# Reglas de cruce

Boceto v0.9. Imagen generada con `tools/boceto_reglas_de_cruce.py`: `modal_reglas_de_cruce.png`.
Las reglas de fondo están en [reglas_de_negocio.md](reglas_de_negocio.md); aquí solo se describe cómo se muestran y qué se puede cambiar.

## Idea

Las reglas vienen **confirmadas por la jefatura** (23-nov-2026). Se pueden cambiar porque las reglas de una oficina cambian, pero
cualquier cambio queda marcado para que no pase inadvertido.

- Cada regla es una tarjeta numerada con título, una frase que la explica y sus opciones.
- Etiqueta de estado: **Confirmada · 23-nov-2026** (verde) o **Cambiada** (naranja, con borde naranja y el enlace
  **Restablecer a lo confirmado**).
- Las opciones se cambian con desplegables e interruptores. Lo que no se puede cambiar se muestra bloqueado, con candado.
- Abajo: **Restablecer todas a lo confirmado**, **Ver cómo se aplican** (abre la prueba de las reglas, ver abajo) y **Listo**.

## Las 5 reglas y sus opciones

| # | Regla | Opciones editables | Fijo |
|---|---|---|---|
| 1 | Qué convenios entran al cuadro | Valor que significa que aplica (APLICA); vigentes: con o sin resultados; vencidos: solo con resultados / todos | — |
| 2 | A qué convenio va cada registro | Solo dentro de los años de vigencia (sí/no); convenio preferido para movilidad (Específico) y para internacionalización en casa (Marco); desempate (el de inicio más reciente) | Si ningún convenio cubre el año del registro, se omite y se lista en Ver revisión |
| 3 | Qué se cuenta | Movilidad cuenta movilidades (una por fila); internacionalización en casa cuenta actividades (una por fila); una fila con varios programas cuenta para cada uno | — |
| 4 | Vigencia y fecha de fin | Si la fecha de fin es texto, vacía o solo un año: año de inicio + vigencia en años | Sin fecha de inicio válida: va a Ver revisión |
| 5 | Activo o No activo | Se decide según el estado de la matriz el día de generar | — |

En el boceto la regla 1 aparece como "Cambiada" (vencidos: "Entran todos") solo para mostrar ese estado; no es una recomendación.
Los valores por defecto son los confirmados: vencidos entran solo si tuvieron resultados.

## Por definir

- Qué otras opciones de cada desplegable existirán (por ejemplo, otros criterios de desempate).

## Ver cómo se aplican

Segundo modal, se abre encima de Reglas de cruce. Imagen: `modal_reglas_ver_como_se_aplican.png`.
Lee los archivos reales de la carpeta, **solo para leer** (no crea archivos ni guarda cambios), y explica qué decidió cada regla.

- **Efecto de tus cambios:** tabla *Lo confirmado → Con tus cambios → Diferencia* (convenios en el cuadro, convenios sin resultados,
  movilidades, actividades) y un aviso que dice qué cambio produjo la diferencia. Si no hay reglas cambiadas, dice que todo está como lo confirmó la jefatura.
- **Qué decidió cada regla:** una fila por regla con su resultado (cuántos convenios entran, cuántos registros se asignan, qué se cuenta,
  cuántas vigencias se calculan, cuántos activos) y la etiqueta Confirmada o Cambiada.
- **Ejemplos reales, paso a paso:** registros concretos con la decisión y la regla que la tomó. Lo que no se pudo asignar se explica y va a Ver revisión.
- No muestra el cuadro completo: eso es **Previsualizar cuadro**, en la ventana principal ([diseno_previsualizar_y_pruebas.md](diseno_previsualizar_y_pruebas.md)).
