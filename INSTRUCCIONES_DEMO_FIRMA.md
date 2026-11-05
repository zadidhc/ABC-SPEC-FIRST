# Generación XML UBL 2.1 y firma de prueba

Este complemento **no reemplaza el generador existente**. Lo reutiliza y añade una demostración de firma XMLDSig RSA-SHA256 con **certificado autofirmado temporal**.

1. Extraer las carpetas `implementacion/`, `ejemplos/` y `tests_specs/` de este paquete **en la raíz de ABC-SPEC-FIRST**, conservando las rutas. Ningún archivo existente debería ser reemplazado.
2. Instalar el módulo criptográfico:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install "cryptography>=43"
   ```
3. Agregar `cryptography>=43` a `requirements.txt`, solo si aún no está.
4. Generar y firmar el documento:
   ```powershell
   .\.venv\Scripts\python.exe .\ejemplos\generar_factura_firmada_demo.py
   ```
5. Ejecutar las pruebas nuevas:
   ```powershell
   $env:PYTHONPATH = (Resolve-Path .\implementacion).Path
   .\.venv\Scripts\python.exe -m pytest -v tests_specs/test_firma_demo.py
   ```
6. Ejecutar todas las pruebas:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q tests_specs
   ```

La factura de ejemplo calcula 2 unidades × S/100 de valor unitario + 18 % IGV = **S/236**.
Los dos archivos producidos quedan en `ejemplos/salida/`:
- XML original sin firma, generado por la implementación real.
- XML con `ds:Signature` insertado en `ext:UBLExtensions`, validado contra Invoice XSD 2.1 y con firma verificada.

## Límites

La verificación criptográfica solo demuestra que el documento no fue alterado y que la clave firmante corresponde al **certificado incluido en el propio XML**. No demuestra la confianza en ese certificado; no es firma fiscal SUNAT ni XML aceptado por SUNAT. No se implementa XAdES-BES ni un proceso real con certificado de contribuyente.

Tampoco se implementan en este complemento ICBPER ni modalidades de crédito. Son características tributarias distintas y fuera del alcance expreso del examen comunicado.
