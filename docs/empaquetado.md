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

## Material de marca (decisión: opción 3, secreto de GitHub)

El logotipo de Areandina, el logo del CNA y Brown Std no se publican en el repositorio. Van cifrados en
`empaquetado/marca.cifrada` (AES, Fernet) y la clave está en el secreto **MARCA_CLAVE** del repositorio
(Settings › Secrets and variables › Actions). Un secreto de GitHub admite hasta 48 KB y el material pesa unos 290 KB:
por eso se sube cifrado y el secreto guarda solo la clave, que es lo que recomienda GitHub para archivos grandes.

- Sin el secreto, el .exe se arma igual: Segoe UI y el cuadro sin el logo del CNA (aviso en la ejecución).
- Para cambiar el material: poner los archivos en `assets/` y correr `python tools/marca.py cifrar` con la misma clave
  en la variable `MARCA_CLAVE` (o sin ella para crear una clave nueva, que luego hay que poner en el secreto).
- El icono del programa es la «A» del logotipo; se crea al empaquetar (`tools/empaquetar.py`).

## En el equipo de la persona

- La configuración se guarda en `%APPDATA%\Cuadro maestro internacional` y en la carpeta `Configuración` junto al .exe.
- Windows SmartScreen puede avisar «Windows protegió su PC» la primera vez, porque el .exe no está firmado:
  «Más información › Ejecutar de todas formas». Firmarlo requiere un certificado de firma de código de la institución.
- Las propiedades del archivo (clic derecho › Propiedades › Detalles) dicen el nombre, la versión y la institución.
