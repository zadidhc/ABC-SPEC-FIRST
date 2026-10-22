# ABC Software Corp — Especificación Técnica Spec-First

[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1.0-green.svg)](specs/05-endpoints-openapi.yaml)
[![UBL Standard](https://img.shields.io/badge/OASIS%20UBL-2.1-blue.svg)](https://docs.oasis-open.org/ubl/os-UBL-2.1/)
[![SUNAT Compliance](https://img.shields.io/badge/SUNAT-RS%20097--2012-red.svg)](specs/06-matriz-sunat-ubl.md)
[![Architecture](https://img.shields.io/badge/Architecture-MVC%20%E2%86%92%20Hexagonal-orange.svg)](specs/04-arquitectura.md)
[![Phase](https://img.shields.io/badge/Phase-Spec--First%20(Phase%201)-purple.svg)](#entregables-técnicos)

> **Fase 1 — Especificación Técnica de Requisitos, Dominio, Arquitectura, Contratos de API y Matriz Normativa SUNAT–UBL 2.1 para Facturación Electrónica y Migración de Almacén Legado.**

---

## 📌 Contexto del Proyecto

**ABC Software Corp** es una empresa mediana dedicada a la comercialización de abarrotes y mercadería al por mayor y menor. El sistema histórico de la empresa operaba con fichas básicas de almacén con cinco campos no estructurados (`fecha`, `ingreso`, `salida`, `producto`, `nro_documento`), sin validaciones tributarias ni emisión de comprobantes válidos ante la SUNAT.

Bajo las resoluciones **RS N° 097-2012/SUNAT**, **RS N° 234-2006/SUNAT** y el estándar internacional **OASIS UBL 2.1**, se requiere formalizar la emisión electrónica y migrar limpiamente los datos históricos preservando la trazabilidad.

Siguiendo la metodología **Spec-First**, este repositorio contiene la arquitectura completa, modelos de datos, contratos formales y matrices de trazabilidad antes de escribir código de implementación.

---

## 📂 Estructura del Repositorio

```text
.
├── README.md                           # Documentación principal para GitHub
├── INFORME_TECNICO_FINAL.md            # Informe técnico final consolidado de la Fase 1
├── specs/                              # Entregables técnicos oficiales de la Fase 1
│   ├── 01-requisitos-casos-uso.md      # Requisitos funcionales/no funcionales y casos de uso
│   ├── 02-modelo-dominio.md            # Modelo de dominio DDD y mapeo legado
│   ├── 03-dtos-schemas.yaml            # Contratos DTO y esquemas reutilizables
│   ├── 04-arquitectura.md              # Monolito MVC y evolución hacia hexagonal
│   ├── 05-endpoints-openapi.yaml       # Contrato de API formal OpenAPI 3.1.0 validado
│   ├── 06-matriz-sunat-ubl.md          # Matriz de trazabilidad SUNAT – OASIS UBL 2.1
│   ├── Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx # Matriz de trazabilidad en formato tabular Excel
│   └── diagramas/                      # Fuentes de diagramas PlantUML
│       ├── mvc.puml                    # Diagrama de clases MVC monolítico
│       └── evolucion-hexagonal.puml     # Diagrama de arquitectura hexagonal (Ports & Adapters)
├── references/                         # Fuentes normativas y caso de estudio
│   ├── caso-estudio-examen.md          # Enunciado del caso de estudio
│   ├── UBL-Invoice-2.1.xml             # Esquema XSD OASIS UBL Invoice 2.1
│   └── 097-2012.pdf                    # Resolución de Superintendencia SUNAT 097-2012
├── CONTEXTO_ANALISIS_PREVIO.md         # Notas preliminares de trabajo
├── LEEME_PRIMERO.md                    # Guía de orientación del proyecto
└── PROMPT_PARA_ANTIGRAVITY.md          # Instrucción del caso de estudio
```

---

## 📑 Entregables Técnicos

### 1. [Requisitos y Casos de Uso (`01-requisitos-casos-uso.md`)](specs/01-requisitos-casos-uso.md)
- **Requisitos del Sistema:** 9 Requisitos Funcionales (RF-01 a RF-09) y 5 Requisitos No Funcionales (RNF-01 a RNF-05).
- **Reglas de Negocio Tributarias:**
  - `RN-01`: Identificación obligatoria con RUC activo/habido (Catálogo 06 SUNAT) para Facturas (`01`).
  - `RN-02`: Estructura formal de series (`F001`) y correlativo (1..99999999).
  - `RN-03` a `RN-05`: Tratamiento integral de IGV (Catálogo 07), ISC (**Catálogo 08 SUNAT**) e ICBPER (Ley 30884).
  - `RN-08`: **No equivalencia automática:** Los documentos legados de almacén no generan facturas fiscales automáticas.
- **Casos de Uso Formalizados:**
  - `CU-01`: Registrar y validar factura borrador.
  - `CU-02`: Solicitar emisión electrónica (XML UBL 2.1, firma digital XAdES-BES, SOAP a OSE/SUNAT y recepción de CDR).
  - `CU-03`: Consultar comprobante y constancia CDR.
  - `CU-04`: Iniciar migración de registros legados por lote.
  - `CU-05`: Inspeccionar trazabilidad y errores de migración.

### 2. [Modelo de Dominio y Mapeo Legado (`02-modelo-dominio.md`)](specs/02-modelo-dominio.md)
- **Entidades DDD:** `CompanyIssuer`, `Customer`, `Product`, `Invoice`, `InvoiceLine`, `InventoryMovement`, `MigrationBatch`, `MigrationRecord`.
- **Mapeo de los 5 Campos Legados:**
  - `fecha` $\rightarrow$ `InventoryMovement.movement_date` (ISO 8601).
  - `ingreso` $\rightarrow$ `InventoryMovement.movement_type = INBOUND` y `quantity`.
  - `salida` $\rightarrow$ `InventoryMovement.movement_type = OUTBOUND` y `quantity`.
  - `producto` $\rightarrow$ Homologación a `Product.sku` o producto huérfano auditable.
  - `nro_documento` $\rightarrow$ `InventoryMovement.reference_source_number` con tipo `INTERNAL_LEGACY_RECORD` (aislado de la numeración tributaria).
- **Separación Arquitectónica:** Frontera estricta entre **Entidades de Dominio**, **DTOs de API REST** y **Estructuras XML OASIS UBL 2.1**.

### 3. [Contratos DTO y Esquemas (`03-dtos-schemas.yaml`)](specs/03-dtos-schemas.yaml)
- Esquemas de datos con validaciones, expresiones regulares y tipos base (`CreateInvoiceRequest`, `CustomerDTO`, `CreateInvoiceLineDTO`, `InvoiceResponse`, `MonetaryTotalsDTO`, `TaxEvidenceDTO`, `LegacyRecordDTO`, `ProblemDetails`).

### 4. [Arquitectura de Software y Evolución (`04-arquitectura.md`)](specs/04-arquitectura.md)
- **Fase Base:** Monolito modular MVC con capa de presentación, servicios de aplicación y puertos de abstracción:
  - `IUblBuilderService`: Aislamiento de serialización UBL 2.1.
  - `IDigitalSignatureService`: Aislamiento de firma XAdES-BES y almacén PKCS#12 (`.p12` / `.pfx`).
  - `ISunatOseClient`: Aislamiento de llamadas SOAP al webservice de SUNAT u OSE.
  - `IDocumentStorageService`: Aislamiento de persistencia de archivos binarios (XML, CDR, PDF).
- **Evolución Hexagonal:** Mapeo formal hacia Puertos de Entrada (`IRegisterInvoiceUseCase`, etc.) y Adaptadores Secundarios (Base de Datos, Generador UBL, Firmador, Cliente SOAP, Almacenamiento).
- **Estrategia Multiplataforma (Windows MSI / Android APK):**
  - **Decisión de Seguridad:** La firma digital con certificado tributario y el despacho a OSE/SUNAT se centralizan en el backend.
  - Clientes ricos ligeros (.NET WPF / WinUI 3 para Windows; Jetpack Compose / Kotlin para Android) consumiendo la API centralizada.

### 5. [Contrato de API OpenAPI 3.1.0 (`05-endpoints-openapi.yaml`)](specs/05-endpoints-openapi.yaml)
- Endpoints especificados conforme a estándares REST y respuestas RFC 7807:
  - `POST /invoices`: Registrar y validar comprobante.
  - `GET /invoices/{id}`: Consultar comprobante y estado de emisión.
  - `POST /invoices/{id}/issuance`: Solicitar emisión electrónica oficial ante OSE/SUNAT.
  - `GET /invoices/{id}/xml`: Descarga de XML firmado.
  - `GET /invoices/{id}/cdr`: Descarga de constancia CDR en ZIP.
  - `POST /migration/batches`: Iniciar lote de migración de almacén legado.
  - `GET /migration/batches/{batchId}`: Inspeccionar estado y contadores de lote.
  - `GET /migration/traceability/{legacyDocumentNumber}`: Rastrear destino de ficha interna legada.
- **Validación:** Validado formalmente mediante `@apidevtools/swagger-cli validate`.

### 6. [Matriz de Trazabilidad SUNAT – OASIS UBL 2.1 (`06-matriz-sunat-ubl.md`)](specs/06-matriz-sunat-ubl.md)
- Mapeo punto a punto de cada campo de negocio contra rutas XML UBL 2.1 (`InvoiceType`), cardinalidades del XSD oficial OASIS y artículos de la normativa peruana.
- Énfasis normativo:
  - **Catálogo 08 de SUNAT:** Sistemas de cálculo del ISC (`01` Al Valor, `02` Específico, `03` Al Precio de Venta al Público).
  - **RS N° 097-2012/SUNAT:** Sistema de Emisión Electrónica desde sistemas del contribuyente.
  - **RS N° 234-2006/SUNAT:** Normativa de libros y registros tributarios (Kardex e inventario permanente en unidades físicas).

---

## 🛠️ Validación de Especificaciones

Para verificar la validez sintáctica de los contratos OpenAPI y esquemas YAML:

```bash
# Validación de la especificación OpenAPI 3.1
npx --yes swagger-cli validate specs/05-endpoints-openapi.yaml
```

Para renderizar los diagramas PlantUML:
- [specs/diagramas/mvc.puml](specs/diagramas/mvc.puml)
- [specs/diagramas/evolucion-hexagonal.puml](specs/diagramas/evolucion-hexagonal.puml)

---

## ⚖️ Licencia y Régimen Académico
Documento elaborado con fines de especificación de arquitectura de software bajo metodología Spec-First. No incluye código ejecutable de backend, frontend ni credenciales reales de SUNAT/OSE conforme a las restricciones del proyecto.
