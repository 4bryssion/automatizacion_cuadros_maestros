# Decisiones de proyecto

Registro de lo decidido con la persona responsable del proyecto. Las reglas de cruce y conteo están en
[reglas_de_negocio.md](reglas_de_negocio.md).

## 23-nov-2026

| Tema | Decisión |
|---|---|
| Dónde se guarda la configuración | En **dos lugares a la vez**: la carpeta de datos del usuario (`%APPDATA%`) y la carpeta donde está el programa portable. No se pudo comprobar si los equipos borran el perfil al cerrar sesión; por eso se guarda en ambos. |
| Salir con cambios sin incluir | Obligatorio generar el cuadro de nuevo (ver [diseno_revision.md](diseno_revision.md)). Excepción: si la generación falla, se deja salir y el estado pendiente se conserva. |
| Quién mantendrá el programa | Probablemente una persona del área de Sistemas (por confirmar). |
| Manual de usuario y de mantenimiento | Se redactan al final del proyecto. |
| Tipografía Brown Std dentro del .exe | Sin objeción. |
| Repositorio | Público por ahora. Por definir si se transfiere a una cuenta de la institución. |

## Cómo funciona el guardado en dos lugares

1. **Al guardar** (cada cambio, al instante): se escribe en ambos lugares. Se escribe primero un archivo temporal y luego se
   renombra, para que un corte no deje el archivo a medias.
2. **Al abrir el programa:** se lee y se valida cada copia. Se usa la **más reciente** (por la fecha guardada dentro del archivo, no
   por la fecha del archivo en Windows).
3. **Si falta una copia o está dañada:** se restaura desde la otra y se avisa en pantalla.
4. **Si la carpeta del programa no permite escribir** (por ejemplo, un disco protegido): se usa solo `%APPDATA%` y Configuración lo indica.
5. **Copias de seguridad:** se conservan las últimas 10, con opción de restaurar una desde Configuración.
6. **Si las dos copias son válidas pero distintas** (por ejemplo, el programa se copió a otro equipo): gana la más reciente y se avisa
   cuál se usó.
7. La configuración no contiene datos de personas: solo nombres de columnas, instituciones, programas, equivalencias y reglas.

## Dónde vive cada prueba (23-nov-2026)

Las pruebas son de solo lectura y cada una está en la pantalla donde se usa; no hay una sola prueba general en Configuración.

- **Previsualizar cuadro:** ventana principal, junto a Generar cuadro maestro (ver cómo quedaría el cuadro).
- **Ver cómo se aplican:** dentro de Reglas de cruce (qué decidió cada regla y qué efecto tienen los cambios).
- **Probar lectura de la carpeta:** dentro de Fuentes de datos (cómo lee el programa cada archivo).
- Detalle en [diseno_previsualizar_y_pruebas.md](diseno_previsualizar_y_pruebas.md).
- Los mockups definitivos se suben a Drive al aprobarse y, cuando todos estén definidos, al repositorio.
