# Guía de Validación Automatizada de Especificaciones (Spec-First)

**Proyecto:** ABC Software Corp — Facturación Electrónica UBL 2.1 & Migración Legada  
**Fecha:** 5 de noviembre de 2026  
**Entorno:** OpenAPI 3.1.0 / Redocly CLI / Python 3.11+ / Pytest / JSON Schema 2020-12  

---

## 1. Propósito y Alcance

Este flujo de validación automatizada garantiza el cumplimiento estricto del enfoque **Spec-First** sin tolerar advertencias silenciadas ni reglas degradadas. Comprueba:
1. **Conformidad OpenAPI 3.1.0:** Parseo formal de YAML, resolución de `$ref` internos, eliminación total de la directiva obsoleta `nullable: true` (reemplazada por tipos unión OpenAPI 3.1 `type: [string, "null"]`).
2. **Linter Oficial Redocly CLI:** Verificación sin errores ni advertencias contra el conjunto de reglas recomendadas de Redocly.
3. **Generación de Bundle:** Compilación unificada de la especificación completa en `dist/openapi-bundled.yaml`.
4. **Auditoría de Seguridad y Unicidad:**
   - Todos los endpoints declaran identificadores únicos en inglés (`operationId`).
   - El esquema `bearerAuth` (JWT) está declarado en la raíz y todos los endpoints exponen respuestas estandarizadas `401 Unauthorized` y `403 Forbidden` basadas en RFC 7807 (`ProblemDetails`).
   - Las operaciones de emisión formal (`/issue`) contemplan `409 Conflict`, `202 Accepted` y `502/503` ante caídas de SUNAT/OSE.
   - El endpoint de migración batch `/migration/batches` retorna `202 Accepted`.
5. **Paridad DTOs vs OpenAPI:** Coherencia exacta entre los esquemas de `specs/03-dtos-schemas.yaml` y `specs/05-endpoints-openapi.yaml`.
6. **Pruebas de Contrato (Positivas y Negativas):** Validación estricta con JSON Schema Draft 2020-12:
   - Cargas útiles válidas de facturas, boletas, notas y migración pasan limpiamente.
   - Cargas con campos requeridos ausentes, tipos incorrectos, unidades no contempladas en Catálogo 03, formatos decimales inválidos (se exige string `^[0-9]+\.[0-9]{2}$`), o inconsistencias en series cruzadas son rechazadas inmediatamente.

---

## 2. Requisitos Previos

- **Node.js** $\ge 18$ y **npm**
- **Python** $\ge 3.11$ (con entorno virtual `.venv` activado)
- Dependencias instaladas:
  ```bash
  # Node.js (Redocly CLI)
  npm install

  # Python (OpenAPI Spec Validator, Pytest, PyYAML, JSONSchema)
  pip install -r requirements.txt
  ```

---

## 3. Comandos de Ejecución

### Ejecución Integral (Recomendada)
Para correr toda la suite de validación (Linter Redocly + Bundle + Pruebas de Contrato Pytest):
```bash
npm run validate:specs
```

### Ejecución por Etapas Individuales
- **Linter de OpenAPI:**
  ```bash
  npm run lint:specs
  ```
- **Generación del bundle unificado:**
  ```bash
  npm run bundle:specs
  ```
- **Pruebas de contrato y auditoría semántica en Python:**
  ```bash
  npm run test:contracts
  # O directamente:
  python -m pytest -v tests_specs/test_specs_validation.py
  ```

---

## 4. Criterios de Aceptación de Integración Continua (CI)

La suite de validación se ejecuta automáticamente en cada `push` o `pull_request` a través de GitHub Actions (`.github/workflows/validate-specs.yml`). El pipeline requiere:
- **0 errores** y **0 advertencias** en Redocly CLI.
- Resolución del 100% de referencias `$ref`.
- Generación exitosa de `dist/openapi-bundled.yaml`.
- 16 de 16 pruebas de contrato aprobadas sin ejecuciones vacías.

