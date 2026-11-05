# INFORME TÉCNICO FINAL DE ARQUITECTURA DE SOFTWARE — FASES 1 Y 2

**Entidad Académica:** Universidad Nacional Agraria de la Selva — Facultad de Ingeniería en Informática y Sistemas  
**Curso:** Arquitectura de Software  
**Caso de Estudio:** ABC Software Corp — Sistema de Facturación Electrónica y Migración de Almacén  
**Fechas:** 22 de octubre de 2026 (Fase 1) y 5 de noviembre de 2026 (Fase 2)  
**Autor:** Senior Software Architect  
**Estado:** Fase 1 especificada y Fase 2 implementada y validada localmente  
**Repositorio Oficial:** [https://github.com/zadidhc/ABC-SPEC-FIRST](https://github.com/zadidhc/ABC-SPEC-FIRST)

---

## 1. Resumen Ejecutivo

El presente informe integra los resultados de la **Fase 1 (Spec-First)** y la **Fase 2 (implementación del generador XML Invoice UBL 2.1)** para la empresa **ABC Software Corp**. El objetivo central consistió en diseñar la arquitectura técnica, modelos de dominio, contratos de interfaz y matrices de cumplimiento normativo necesarios para reemplazar un software básico e informal de almacén por un sistema formal de emisión electrónica compatible con el estándar internacional **OASIS UBL 2.1** y las resoluciones de la **SUNAT** (**RS N° 097-2012/SUNAT** y **RS N° 234-2006/SUNAT**), garantizando además la migración e inmutabilidad de los datos históricos.

En la Fase 1 se formalizaron las especificaciones y contratos antes de implementar el software. Posteriormente, en la Fase 2, se desarrolló en Python el generador de documentos XML UBL 2.1 y se comprobó su funcionamiento mediante pruebas automatizadas.

---

## 2. Metodología de Trabajo y Fuentes de Información

El proyecto se estructuró conforme al principio de prioridad de fuentes establecido:
1. **Caso de estudio del examen:** Delimitación estricta de alcance, restricciones y problemas operativos.
2. **Esquema OASIS UBL Invoice 2.1 XSD:** Inspección de gramáticas, namespaces (`cac`, `cbc`, `ext`, `ds`), cardinalidades y tipos de datos.
3. **Normativa Oficial SUNAT:** Catálogos oficiales (01, 02, 03, 06, 07, 08, 16), regulaciones para SEE-Del Contribuyente / OSE y libros tributarios de inventario.
4. **Validación Automatizada:** Contratos OpenAPI 3.1.0 validados mediante herramientas de análisis estático (`swagger-cli`).

---

## 3. Detalle de Entregables Elaborados y Aportes Técnicos

### 3.1 Especificación 01 — Requisitos y Casos de Uso (`01-requisitos-casos-uso.md`)
- **Requisitos Formales:** 9 Requisitos Funcionales (`RF-01` a `RF-09`) y 5 Requisitos No Funcionales (`RNF-01` a `RNF-05`).
- **Reglas de Negocio Tributarias:**
  - `RN-01` a `RN-02`: Exigencia de RUC de 11 dígitos para facturas electrónicas (`01`) y formato estricto de serie/correlativo (`F001-00000001`).
  - `RN-03` a `RN-06`: Formulación de cálculos aritméticos para IGV (18%), Impuesto Selectivo al Consumo (ISC) según los tres sistemas del **Catálogo 08 de SUNAT**, e Impuesto al Consumo de las Bolsas de Plástico (ICBPER).
  - `RN-08`: **Regla de No Equivalencia:** Los documentos internos legados no se promueven automáticamente a comprobantes fiscales SUNAT.
- **Casos de Uso Especificados:**
  - `CU-01`: Registrar y Validar Factura (Borrador).
  - `CU-02`: Solicitar Emisión Electrónica (UBL 2.1 / Firma XAdES-BES / Envío SOAP / Recepción de CDR).
  - `CU-03`: Consultar Comprobante y Estado Tributario.
  - `CU-04`: Iniciar Migración de Datos Legados de Almacén.
  - `CU-05`: Inspeccionar Trazabilidad y Errores de Migración.

### 3.2 Especificación 02 — Modelo de Dominio y Mapeo Legado (`02-modelo-dominio.md`)
- **Arquitectura DDD (Domain-Driven Design):** Entidades fuertemente tipadas (`CompanyIssuer`, `Customer`, `Product`, `Invoice`, `InvoiceLine`, `InventoryMovement`, `MigrationBatch`, `MigrationRecord`).
- **Mapeo de los 5 Campos Legados:**
  - `fecha` $\rightarrow$ `InventoryMovement.movement_date` (formato ISO 8601).
  - `ingreso` $\rightarrow$ `InventoryMovement.movement_type = INBOUND` con valor absoluto.
  - `salida` $\rightarrow$ `InventoryMovement.movement_type = OUTBOUND` con valor absoluto.
  - `producto` $\rightarrow$ Homologación contra catálogo de `Product` o clasificación auditable.
  - `nro_documento` $\rightarrow$ `InventoryMovement.reference_source_number` con tipo `INTERNAL_LEGACY_RECORD`.
- **Frontera de Desacoplamiento:** Distinción conceptual entre **Entidades de Dominio**, **DTOs de API REST** y **Estructuras XML OASIS UBL 2.1**.

### 3.3 Especificación 03 y 05 — Contratos de API y DTOs (`03-dtos-schemas.yaml` y `05-endpoints-openapi.yaml`)
- **Estándar OpenAPI 3.1.0:** Especificación completa de contratos, modelos y códigos HTTP (200, 201, 202, 400, 404, 409, 422, 502).
- **Operaciones Formalizadas:**
  - `POST /invoices`: Creación y validación de facturas.
  - `GET /invoices/{id}`: Consulta integral de comprobante y estado CDR.
  - `POST /invoices/{id}/issuance`: Orquestación de firma, envío y recepción de constancia de recepción (CDR).
  - `GET /invoices/{id}/xml` y `GET /invoices/{id}/cdr`: Descarga segura de artefactos normativos.
  - `POST /migration/batches`, `GET /migration/batches/{batchId}` y `GET /migration/traceability/{legacyDocumentNumber}`: Ingesta batch y auditoría histórica.
- **Resultado de Validación:** Aprobado con cero errores sintácticos mediante `@apidevtools/swagger-cli`.

### 3.4 Especificación 04 — Arquitectura de Software y Diagramas (`04-arquitectura.md` y `specs/diagramas/`)
- **Monolito Modular Inicial (MVC):** Capas desacopladas mediante interfaces mandatorias:
  - `IUblBuilderService`: Aislamiento de serialización XML.
  - `IDigitalSignatureService`: Aislamiento de firma XAdES-BES y certificados PKCS#12 (`.p12` / `.pfx`).
  - `ISunatOseClient`: Aislamiento del protocolo SOAP y webservices de SUNAT/OSE.
  - `IDocumentStorageService`: Aislamiento de almacenamiento físico (local o nube).
- **Evolución Hexagonal (Ports & Adapters):** Promoción de interfaces a puertos de entrada (`IRegisterInvoiceUseCase`, etc.) y puertos de salida (`IInvoiceRepositoryPort`, `IUblGeneratorPort`, etc.) preparando la futura segregación en microservicios (*CPE Service*, *Warehouse Service*, *Migration Worker*).
- **Estrategia Multiplataforma (Windows MSI / Android APK):**
  - **Decisión de Ciberseguridad:** Centralización de la firma digital y el envío a OSE/SUNAT en el backend central para evitar la fuga o exposición del certificado digital tributario en dispositivos cliente o terminales móviles.
  - Clientes ricos ligeros (.NET WPF / WinUI 3 y Android Jetpack Compose) comunicados vía HTTPS/REST contra la API OpenAPI 3.1.

### 3.5 Especificación 06 — Matriz de Trazabilidad SUNAT – UBL 2.1 (`06-matriz-sunat-ubl.md` y Excel)
- **Matriz de Cruce Integral:** Relaciona requisitos, rutas UBL (`cbc:ID`, `cbc:IssueDate`, `cac:TaxTotal`, `cac:InvoiceLine`), cardinalidades XSD OASIS y base legal SUNAT.
- **Entregable Tabular Adicional:** Archivo Excel oficial [`specs/Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx`](specs/Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx).
- **Análisis Regulatorio Específico:**
  - **RS N° 097-2012/SUNAT:** Regulación del sistema SEE y validez legal exclusiva mediante constancia CDR aceptada (`código 0`).
  - **RS N° 234-2006/SUNAT:** Marco legal de kardex e inventarios físicos, demostrando que los datos legados corresponden a controles internos de almacén amparados por esta norma, pero no a facturas tributarias de la RS 097-2012.
  - **Catálogo 08 de SUNAT:** Detalle de los 3 sistemas de cálculo del ISC (`01` Al Valor, `02` Específico, `03` Al Precio de Venta al Público).

---

## 4. Estado de Verificación y Asuntos Pendientes (`PENDIENTE DE VERIFICACIÓN`)

1. **Plazo Límite de Envío a SUNAT:** Se incorporó una regla preventiva de 3 días calendario posteriores a la emisión, sujeta a confirmación del calendario específico del contribuyente.
2. **Designación OSE Obligatoria:** La arquitectura permite emitir directamente a SUNAT o utilizar un Operador de Servicios Electrónicos (OSE) mediante configuración de la interfaz `ISunatOseClient` sin alterar el dominio.

---

## 5. Conclusión de la Fase 1

La Fase 1 Spec-First se completó satisfactoriamente, proveyendo a **ABC Software Corp** de un conjunto de especificaciones técnicas consistentes, formalmente verificadas, con trazabilidad normativa rigurosa y preparadas para la fase de implementación de software.

---

## 6. Implementación de la Fase 2 — XML Invoice UBL 2.1

**Fecha de entrega:** 05 de noviembre de 2026.

### 6.1 Objetivo

Implementar en Python la generación de documentos XML de comprobantes electrónicos utilizando las clases obtenidas a partir del esquema OASIS Invoice XSD 2.1.

La implementación debe representar los datos del dominio, validar sus reglas, calcular los importes y producir un documento XML que supere la validación estructural XSD.

### 6.2 Tecnologías utilizadas

- Python como lenguaje de implementación.
- OASIS UBL 2.1 como estándar estructural del XML.
- xsdata para generar clases Python desde los esquemas XSD.
- lxml para serialización y validación estructural.
- Decimal para cálculos monetarios.
- pytest para pruebas unitarias y de integración.

### 6.3 Organización de la implementación

El código se encuentra en el directorio `implementacion/abc_cpe/`.

**Dominio:**
- `dominio/modelos.py`: modelos de comprobante, emisor, cliente y líneas.
- `dominio/catalogos.py`: tipos de comprobante, documentos y categorías tributarias.
- `dominio/validaciones.py`: reglas de negocio y validación de datos.
- `dominio/calculo.py`: cálculo de importes e impuestos.
- `dominio/errores.py`: errores del dominio.

**Aplicación:**
- `aplicacion/servicio.py`: servicio `GenerarXmlComprobanteService`.
- `aplicacion/puertos.py`: interfaces para desacoplar la generación y validación.

**Infraestructura:**
- `infraestructura/generador_ubl.py`: construcción y serialización del XML.
- `infraestructura/validador_xsd.py`: validación mediante lxml.

**Artefactos derivados del esquema:**
- `implementacion/abc_cpe/ubl_generado/`: clases generadas desde XSD.
- `implementacion/xsd/maindoc/UBL-Invoice-2.1.xsd`: esquema principal Invoice.
- `implementacion/xsd/common/`: esquemas de componentes y tipos compartidos.

### 6.4 Flujo de generación

1. Construir un comprobante a partir de los modelos del dominio.
2. Verificar emisor, cliente, serie, correlativo y líneas de detalle.
3. Validar cantidades, precios y reglas de negocio.
4. Calcular bases imponibles, impuestos y totales.
5. Construir el objeto UBL Invoice 2.1.
6. Serializar el objeto a XML.
7. Validar el documento generado contra Invoice XSD 2.1.

El servicio devuelve el nombre del comprobante, los bytes XML y el resultado del cálculo.

### 6.5 Pruebas automatizadas

Las pruebas se encuentran en `tests_specs/`.

- `test_generacion_xml.py`: pruebas básicas de generación y rechazo de entradas inválidas.
- `test_xsd_integration.py`: pruebas de generación completa, estructura UBL, impuestos y validación XSD.
- `test_domain_validation.py`: reglas del dominio.
- `test_financial_correctness.py`: cálculos, redondeos y coherencia con XML.
- `test_adversarial.py`: entradas inválidas y casos especiales.
- `test_specs_validation.py`: validación de especificaciones y contratos.

**Resultados verificados localmente:**
- 49 pruebas específicas de generación XML e integración XSD aprobadas.
- 225 pruebas automatizadas aprobadas en la suite completa.
- Sin fallos ni advertencias de pytest en la última ejecución completa.

### 6.6 Ejecución de las pruebas

Desde la raíz del proyecto, en PowerShell:

Instalar dependencias:

`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

Configurar la ruta del código:

`$env:PYTHONPATH = (Resolve-Path .\implementacion).Path`

Ejecutar las pruebas de generación XML:

`.\.venv\Scripts\python.exe -m pytest -v tests_specs/test_generacion_xml.py tests_specs/test_xsd_integration.py`

Ejecutar la suite completa:

`.\.venv\Scripts\python.exe -m pytest -q tests_specs`

### 6.7 Alcance y limitaciones

La implementación permite generar documentos XML Invoice UBL 2.1 y comprobar su estructura mediante el XSD.

No incluye firma digital criptográfica, transmisión a SUNAT/OSE ni procesamiento de CDR.

La conformidad con el esquema XSD no constituye una aceptación tributaria de SUNAT.

La fórmula del ISC al precio de venta al público permanece pendiente de verificación normativa. El ICBPER figura en el diseño de la Fase 1, pero no forma parte del alcance implementado y verificado del generador actual.

---

## 7. Conclusión general de las Fases 1 y 2

La Fase 1 estableció las especificaciones de requisitos, arquitectura, dominio, API y trazabilidad normativa del sistema ABC Software Corp.

La Fase 2 convirtió parte de ese diseño en una implementación ejecutable en Python, capaz de construir documentos XML Invoice UBL 2.1 a partir de modelos del dominio y validarlos contra el esquema XSD correspondiente.

Los resultados locales de 49 pruebas específicas y 225 pruebas totales aprobadas respaldan el funcionamiento de los casos implementados. No representan certificación tributaria ni sustituyen las validaciones oficiales de SUNAT.

La implementación, las pruebas y la documentación se publicaron en la rama principal `main` del repositorio ABC-SPEC-FIRST.
