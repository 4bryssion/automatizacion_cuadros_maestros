# Empaquetado del .exe

El programa se entrega como **un solo archivo** `Cuadro maestro internacional.exe` (portable: no se instala; se copia y
se abre con doble clic). Lo arma GitHub Actions en Windows (`.github/workflows/empaquetar.yml`) con PyInstaller.

## Cuándo se arma

- En cada cambio en `main`: queda como artefacto «Cuadro maestro internacional (Windows)» de esa ejecución
  (Actions › Empaquetar .exe › la ejecución › Artifacts). Los artefactos duran 90 días.
- Con una etiqueta `v…` (por ejemplo `git tag v0.1.0 && git push --tags`): además se publica en **Releases**, que es
  el lugar estable para descargarlo.
- A mano: Actions › Empaquetar .exe › Run workflow.

Después de armarlo, el flujo abre el .exe con `--comprobar` (sin ventana) y falla si no arranca o si, habiendo clave,
no trae el logo del CNA y Brown Std.

## Material de marca (decisión del 24-nov-2026)

- **Logotipo de Areandina:** está en el repositorio (`assets/marca/logotipo_verde.png`) y va dentro del .exe (cabecera
  de las pantallas e icono del programa, que es la «A» del logotipo y se crea al empaquetar).
- **Logo del CNA:** no se publica. El .exe arma el cuadro sin ese logo; quien tenga el archivo puede ponerlo en
  `assets/logo_cna.png` y empaquetar en su equipo (`pip install -e ".[empaquetado]"` y `python tools/empaquetar.py`).
- **Brown Std:** tipografía comercial (Lineto). La oficina confirmó el 25-nov-2026 que la institución tiene permiso para
  usarla en el programa, así que está en `assets/marca/fuentes/` y va dentro del .exe (se carga solo para el programa,
  sin instalarla en Windows). La comprobación del .exe falla si no la carga.

## En el equipo de la persona

- La configuración se guarda en `%APPDATA%\Cuadro maestro internacional` y en la carpeta `Configuración` junto al .exe.
- Windows SmartScreen puede avisar «Windows protegió su PC» la primera vez, porque el .exe no está firmado:
  «Más información › Ejecutar de todas formas». Firmarlo requiere un certificado de firma de código de la institución.
- Las propiedades del archivo (clic derecho › Propiedades › Detalles) dicen el nombre, la versión y la institución.
