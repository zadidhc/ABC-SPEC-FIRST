# SPEC — Requisitos del Sistema y Casos de Uso (ABC Software Corp)

**Versión:** 2.0.0  
**Fecha:** 5 de noviembre de 2026  
**Fase:** Fase 2 — Corrección y Ampliación Spec-First  
**Autor:** Senior Software Architect  
**Estado:** REVISADO — APROBADO PARA FASE 2

---

## 1. Introducción y Propósito

El presente documento define los requisitos funcionales, requisitos no funcionales, reglas de negocio y casos de uso formalizados para la transformación del software básico de almacén de **ABC Software Corp** en un sistema robusto de facturación electrónica compatible con el estándar internacional **OASIS UBL 2.1** y las normativas de la **Superintendencia Nacional de Aduanas y de Administración Tributaria (SUNAT)** de Perú.

Esta especificación cubre la emisión de **Facturas Electrónicas (01)**, **Boletas de Venta Electrónicas (03)**, **Notas de Crédito Electrónicas (07)** y **Notas de Débito Electrónicas (08)**, así como los mecanismos de contingencia y reporte masivo (**Resumen Diario de Boletas** y **Comunicación de Baja**), junto con la generación de libros contables electrónicos (**Registro de Ventas e Ingresos - Formato 14.1** y **Registro de Inventario Permanente en Unidades Físicas - Formato 12.1**).

---

## 2. Requisitos Funcionales (RF)

| ID | Requisito Funcional | Descripción | Casos de Uso Asociados |
| :--- | :--- | :--- | :--- |
| **RF-01** | Emisión de Facturas y Boletas | Registrar y validar comprobantes tipo Factura (`01`, serie `F...`, receptor con RUC) y Boleta de Venta (`03`, serie `B...`, receptor con DNI, RUC o sin documento) bajo estándar UBL 2.1. | CU-01, CU-02 |
| **RF-02** | Emisión de Notas de Crédito y Débito | Emitir Notas de Crédito (`07`) y Débito (`08`) referenciando documentos válidos previos y especificando motivos normativos según Catálogos 09 y 10 de SUNAT. | CU-06 |
| **RF-03** | Generación de XML UBL 2.1 | Producir estructuras XML estrictas mediante clases fuertemente tipadas generadas desde los esquemas XSD oficiales de OASIS UBL 2.1, validadas contra XSD antes de su firma. | CU-02, CU-06 |
| **RF-04** | Firma Digital Enveloping XMLDSig | Firmar digitalmente los comprobantes mediante el estándar XMLDSig Enveloped (`ds:Signature` embebido en `ext:UBLExtensions`), generando `ds:DigestValue` y `ds:SignatureValue`. | CU-02, CU-06 |
| **RF-05** | Comunicación con OSE / SUNAT | Gestionar el empaquetado ZIP, envío síncrono/asíncrono vía SOAP, recepción de Constancia de Recepción (CDR) y clasificación de estados según rangos de respuesta. | CU-02, CU-03, CU-06, CU-07, CU-08 |
| **RF-06** | Resumen Diario y Comunicación de Baja | Enviar paquetes de Resumen Diario para Boletas de Venta y emitir Comunicaciones de Baja para anulación de Facturas y Notas vinculadas, gestionando tickets asíncronos (`202 Accepted`). | CU-07, CU-08 |
| **RF-07** | Libros Tributarios Electrónicos (14.1 y 12.1) | Generar el Registro de Ventas (Formato 14.1) derivado de los comprobantes emitidos y el Registro de Inventario Permanente en Unidades Físicas (Formato 12.1 - Kardex) vinculado a la información migrada. | CU-09, CU-10 |
| **RF-08** | Migración de Datos Legados | Ingerir lotes históricos del almacén básico (`fecha`, `ingreso`, `salida`, `producto`, `nro_documento`) garantizando trazabilidad y preservando `INTERNAL_LEGACY_RECORD`. | CU-04, CU-05 |
| **RF-09** | Gestión de Catálogos Tributarios | Soportar los catálogos normativos SUNAT: 01 (Tipo Documento), 02 (Moneda), 03 (Unidades de Medida), 06 (Doc. Identidad), 07 (Afectación IGV), 08 (Sistemas ISC), 09/10 (Notas), 51 (Tipo de Operación), 52 (Leyendas). | CU-01, CU-02, CU-06 |

---

## 3. Requisitos No Funcionales (RNF)

| ID | Requisito No Funcional | Criterio de Aceptación / Restricción Técnica |
| :--- | :--- | :--- |
| **RNF-01** | Arquitectura Limpia y Desacoplada | Núcleo de dominio ciego a detalles de infraestructura. Evolución planificada de Monolito Modular MVC a Arquitectura Hexagonal mediante interfaces/puertos explícitos. |
| **RNF-02** | Multiplataforma y Distribución | Clientes delgados de escritorio Windows (C# .NET 8 / WPF / WinUI 3 con instalador MSI) y móvil Android (Kotlin Jetpack Compose en APK), consumiendo la API centralizada. |
| **RNF-03** | Idempotencia y Reintentos Seguros | Operaciones de emisión y migración soportan cabecera `X-Idempotency-Key` para evitar comprobantes duplicados y garantizar concurrencia segura. |
| **RNF-04** | Seguridad y Criptografía Centralizada | El certificado digital tributario (PKCS#12) y las operaciones de firma XMLDSig y envío a SUNAT residen exclusivamente en el servidor central seguro; la API requiere `bearerAuth` (JWT). |
| **RNF-05** | Rigor Normativo y Esquemas Abiertos | API descrita formalmente en OpenAPI 3.1.0 y XMLs producidos exclusivamente mediante clases generadas del XSD oficial de OASIS, sin motores de plantillas de texto. |

---

## 4. Reglas de Negocio (RN)

- **RN-01 (Identificación del Receptor - Catálogo 06):**
  - Facturas (`01`): Obligatorio RUC de 11 dígitos numéricos válido (Tipo Documento `'6'`), verificado mediante algoritmo Módulo 11 y con prefijos autorizados (10, 15, 16, 17, 20).
  - Boletas de Venta (`03`): DNI de 8 dígitos numéricos (Tipo Documento `'1'`), RUC (Tipo `'6'`), Carnet de Extranjería (`'4'`), Pasaporte (`'7'`), o sin documento (`'0'`) para operaciones menores al umbral normativo.
- **RN-02 (Series y Correlativos):**
  - Facturas y sus notas asociadas: Serie con patrón `^F[A-Z0-9]{3}$` (ej. `F001`).
  - Boletas y sus notas asociadas: Serie con patrón `^B[A-Z0-9]{3}$` (ej. `B001`).
  - Correlativo: Entero secuencial entre 1 y 99,999,999, sin huecos dentro de la misma serie.
- **RN-03 (Afectación al IGV - Catálogo 07):** Toda línea debe declarar su código de afectación. Para gravadas (`10`), tasa del 18.00%. Para exoneradas (`20` / `9997`) e inafectas (`30` / `9998`), impuesto 0.00 pero base imponible desglosada en sus respectivos subtotales.
- **RN-04 (Impuesto Selectivo al Consumo - ISC y Catálogo 08):**
  - Sistema 01 (Al Valor): $\text{ISC} = \text{round2}(\text{valor\_venta} \times \text{tasa})$.
  - Sistema 02 (Específico): $\text{ISC} = \text{round2}(\text{cantidad} \times \text{monto\_fijo})$.
  - Sistema 03 (Al PVP): $\text{ISC} = \text{round2}(\text{cantidad} \times \text{PVP} \times \text{tasa})$ *(Fórmula sujeta a confirmación en referencias: PENDIENTE DE VERIFICACIÓN)*.
  - El ISC forma parte de la base imponible del IGV: $\text{Base IGV} = \text{Valor Venta Gravada} + \text{ISC}$. La base del ISC (`base_isc`) corresponde exclusivamente a la suma del valor venta de las líneas afectas a ISC.
- **RN-05 (Notas de Crédito y Débito):** Deben referenciar un comprobante previo existente (`referenced_document_series_number` y `referenced_document_type_code`) y declarar un motivo tipificado según Catálogo 09 (NC) o Catálogo 10 (ND).
- **RN-06 (Totalización Monetaria):** Todos los cálculos deben realizarse con aritmética exacta decimal (`Decimal` de precisión fija, 2 decimales con redondeo `ROUND_HALF_UP` en importes finales; cantidades y valores unitarios con hasta 10 decimales).
- **RN-07 (Trazabilidad de Rangos de CDR):**
  - `0100 - 0999`: Excepción técnica transitoria. Reintento automático seguro.
  - `1000 - 1999`: Error de datos corregible. Se autoriza subsanación y reenvío bajo el mismo número según disposición SUNAT.
  - `2000 - 3999`: Rechazo tributario definitivo. El comprobante carece de validez fiscal y la numeración no puede reutilizarse.
  - `≥ 4000`: Aceptado con observaciones. Comprobante legalmente válido emitido con código 0 y advertencias adjuntas.
- **RN-08 (Tratamiento del Sistema Legado):** Los campos históricos (`fecha`, `ingreso`, `salida`, `producto`, `nro_documento`) alimentan el control de almacén y el Formato 12.1. El campo `nro_documento` se preserva como referencia interna `INTERNAL_LEGACY_RECORD` sin asignarle automáticamente serie ni número fiscal formal de SUNAT.

---

## 5. Especificación Formal de Casos de Uso

```mermaid
usecaseDiagram
    actor "Operador Comercial" as Operador
    actor "Administrador / Auditor" as Admin
    actor "Supervisor Contable" as Contador
    actor "Servicio OSE / SUNAT" as SUNAT

    package "Sistema de Facturación ABC" {
        usecase "CU-01: Registrar Comprobante (Borrador)" as CU01
        usecase "CU-02: Emitir Factura/Boleta (XML/Firma/Envío)" as CU02
        usecase "CU-03: Consultar Comprobante y CDR" as CU03
        usecase "CU-04: Iniciar Migración de Datos Legados" as CU04
        usecase "CU-05: Inspeccionar Trazabilidad de Migración" as CU05
        usecase "CU-06: Emitir Nota de Crédito / Débito" as CU06
        usecase "CU-07: Procesar Resumen Diario de Boletas" as CU07
        usecase "CU-08: Enviar Comunicación de Baja" as CU08
        usecase "CU-09: Generar Registro de Ventas (Formato 14.1)" as CU09
        usecase "CU-10: Generar Kardex Físico (Formato 12.1)" as CU10
    }

    Operador --> CU01
    Operador --> CU02
    Operador --> CU03
    Operador --> CU06
    Admin --> CU04
    Admin --> CU05
    Contador --> CU07
    Contador --> CU08
    Contador --> CU09
    Contador --> CU10

    CU02 ..> SUNAT : Envío SOAP / CDR
    CU06 ..> SUNAT : Envío SOAP / CDR
    CU07 ..> SUNAT : Envío Lote / Ticket
    CU08 ..> SUNAT : Envío Lote / Ticket
```
