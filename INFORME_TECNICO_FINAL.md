# INFORME TÉCNICO FINAL DE ARQUITECTURA DE SOFTWARE (FASE 1 — SPEC-FIRST)

**Entidad Académica:** Universidad Nacional Agraria de la Selva — Facultad de Ingeniería en Informática y Sistemas  
**Curso:** Arquitectura de Software  
**Caso de Estudio:** ABC Software Corp — Sistema de Facturación Electrónica y Migración de Almacén  
**Fecha:** 22 de octubre de 2026  
**Autor:** Senior Software Architect  
**Estado:** INFORME TÉCNICO FINAL CONCLUIDO  
**Repositorio Oficial:** [https://github.com/zadidhc/ABC-SPEC-FIRST](https://github.com/zadidhc/ABC-SPEC-FIRST)

---

## 1. Resumen Ejecutivo

El presente informe consolida los resultados técnicos de la **Fase 1 (Spec-First)** desarrollada para la empresa **ABC Software Corp**. El objetivo central consistió en diseñar la arquitectura técnica, modelos de dominio, contratos de interfaz y matrices de cumplimiento normativo necesarios para reemplazar un software básico e informal de almacén por un sistema formal de emisión electrónica compatible con el estándar internacional **OASIS UBL 2.1** y las resoluciones de la **SUNAT** (**RS N° 097-2012/SUNAT** y **RS N° 234-2006/SUNAT**), garantizando además la migración e inmutabilidad de los datos históricos.

Siguiendo el rigor de la metodología *Spec-First*, todo el diseño fue formalizado y validado sintácticamente antes de escribir una sola línea de código de implementación de aplicación, base de datos o interfaces gráficas.

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

## 5. Conclusión General

La Fase 1 Spec-First se completó satisfactoriamente, proveyendo a **ABC Software Corp** de un conjunto de especificaciones técnicas consistentes, formalmente verificadas, con trazabilidad normativa rigurosa y preparadas para la fase de implementación de software.
