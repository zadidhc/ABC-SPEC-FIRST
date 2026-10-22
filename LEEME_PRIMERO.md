# Qué hacer en Google Antigravity

1. Descarga y descomprime `ABC-SPEC-FIRST.zip` en Windows.
2. Abre Google Antigravity → **Open Folder / Abrir carpeta** → selecciona `ABC-SPEC-FIRST` (la carpeta descomprimida, no el ZIP).
3. En el chat del agente, escribe: **«Lee `PROMPT_PARA_ANTIGRAVITY.md`, sigue sus instrucciones y genera los cuatro entregables Spec-First dentro de `specs/`. Toma `referencias/caso-estudio-examen.png` como fuente principal.»**
4. El agente tiene los archivos locales y debe crear `specs/`. Si pide acceso a archivos del proyecto, autorízalo después de revisar que no sean acciones destructivas.
5. Cuando termine, comprime **solo `specs/`** y súbelo a ChatGPT para revisar.

`referencias/` = fuentes. `CONTEXTO_ANALISIS_PREVIO.md` = lo conversado, solo propuestas. `PROMPT_PARA_ANTIGRAVITY.md` = instrucciones al agente. `specs/` = salida final que pide el profesor.

No hace falta adjuntar los mismos archivos por separado al chat del agente si este puede leer la carpeta abierta. **No enviar tokens de Nubefact ni activar emisión real SUNAT**.


ACLARACIÓN SOBRE FORMATOS: `specs/` contendrá varios documentos `.md`, diagramas `.puml` y un contrato `openapi.yaml`. No se requieren archivos `.json`, intercambios HTTP, ni implementación. La documentación JSON de Nubefact solo sirve como referencia contextual.
