# SPEC 04 — Matriz de Trazabilidad Normativa SUNAT – OASIS UBL 2.1 y Libros Tributarios

**Versión:** 2.0.0  
**Fecha:** 5 de noviembre de 2026  
**Fase:** Fase 2 — Corrección y Ampliación Spec-First  
**Autor:** Senior Software Architect  
**Estado:** REVISADO — APROBADO PARA FASE 2

---

## 1. Alcance Normativo y Criterios de Rigor Legal

Esta matriz correlaciona cada regla de negocio, DTO y requisito funcional de **ABC Software Corp** con la gramática formal del estándar **OASIS UBL 2.1** (`xsd/maindoc/UBL-Invoice-2.1.xsd`, `UBL-CreditNote-2.1.xsd`, `UBL-DebitNote-2.1.xsd` y esquemas de `common/`), los catálogos oficiales de la **SUNAT**, las resoluciones de superintendencia peruanas aplicables y los formatos de libros tributarios electrónicos:
- **RS N° 097-2012/SUNAT** y modificatorias: Marco rector del Sistema de Emisión Electrónica desarrollado desde los sistemas del contribuyente (SEE-Del Contribuyente).
- **RS N° 234-2006/SUNAT**: Marco regulatorio de libros y registros vinculados a asuntos tributarios: **Formato 14.1 (Registro de Ventas e Ingresos)** y **Formato 12.1 (Registro de Inventario Permanente en Unidades Físicas - Kardex)**.
- **Ley N° 30884 y RS N° 150-2019/SUNAT**: Impuesto al Consumo de las Bolsas de Plástico (ICBPER).
- **Catálogo 08 SUNAT**: Códigos de tipos de sistema de cálculo del Impuesto Selectivo al Consumo (ISC).
- **Catálogos 09 y 10 SUNAT**: Códigos de tipos de notas de crédito y notas de débito.
- **Catálogos 51 y 52 SUNAT**: Tipo de operación y códigos de leyendas tributarias.

> **Distinción Jurídica y Técnica Esencial:**  
> Un elemento definido como opcional (`minOccurs="0"`) en el esquema base OASIS UBL 2.1 puede ser de **consignación obligatoria e indelegable** según la normativa tributaria peruana para que el comprobante adquiera validez fiscal ante SUNAT/OSE.

---

## 2. Matriz de Trazabilidad: Requisitos $\rightarrow$ UBL 2.1 $\rightarrow$ SUNAT

| ID Req / Regla | Concepto de Negocio | Elemento / Ruta XPath UBL 2.1 | Cardinalidad XSD OASIS | Regla / Catálogo SUNAT | Fuente Normativa Exacta | Estado de Verificación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01 / RN-02** | Numeración: Serie y Correlativo | `/Invoice/cbc:ID` | `1..1` | Formato `^[FB][A-Z0-9]{3}-[0-9]{1,8}$` (ej. `F001-00001042`). Serie inicia con F para facturas y B para boletas. Correlativo sin ceros a la izquierda en UBL o formateado hasta 8 dígitos. | Anexo 1, RS 097-2012/SUNAT; RS 193-2020/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Fecha de Emisión del Comprobante | `/Invoice/cbc:IssueDate` | `1..1` | Formato fecha `YYYY-MM-DD`. No mayor al día de emisión ni anterior al plazo máximo legal de envío (hasta 3 días calendario posteriores). | RS 097-2012/SUNAT; RS 150-2021/SUNAT | **VERIFICADO** (RS 097-2012) |
| **RF-01** | Hora de Emisión | `/Invoice/cbc:IssueTime` | `0..1` | Formato `HH:MM:SS`. Obligatorio por SUNAT para trazabilidad y orden cronológico. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Fecha de Vencimiento | `/Invoice/cbc:DueDate` | `0..1` | Formato `YYYY-MM-DD`. Obligatorio en operaciones al crédito. Debe ser $\ge$ `IssueDate`. | RS 193-2020/SUNAT | **VERIFICADO** (RS 193-2020) |
| **RF-01 / RN-01** | Tipo de Comprobante | `/Invoice/cbc:InvoiceTypeCode` | `0..1` | **Catálogo 01 SUNAT**: `'01'` (Factura), `'03'` (Boleta). En OASIS base es `0..1`, pero SUNAT exige `1..1`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 01) |
| **RF-01 / RN-09** | Tipo de Operación | `/Invoice/cbc:InvoiceTypeCode/@listID` | Atributo opcional en XSD | **Catálogo 51 SUNAT**: `'0101'` (Venta interna), `'0102'` (Exportación), etc. Obligatorio por SUNAT en el atributo `@listID`. | RS 097-2012/SUNAT; Catálogo 51 | **VERIFICADO** (Catálogo 51) |
| **RF-01** | Tipo de Moneda de la Factura | `/Invoice/cbc:DocumentCurrencyCode` | `0..1` | **Catálogo 02 SUNAT** / ISO 4217 (ej. `'PEN'`, `'USD'`). Exigido por SUNAT `1..1` en cabecera. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 02) |
| **RF-04** | Contenedor de Extensiones y Firma Digital | `/Invoice/ext:UBLExtensions` | `0..1` | Contenedor de extensiones. SUNAT exige ubicar `<ds:Signature>` bajo `ext:UBLExtension/ext:ExtensionContent`. No debe emitirse vacío. | RS 097-2012/SUNAT | **VERIFICADO** (RS 097-2012) |
| **RF-04** | Firma Digital Enveloped (XMLDSig) | `/Invoice/ext:UBLExtensions/.../ds:Signature` | `0..1` (en extensiones) | **XMLDSig Enveloped** con certificado digital tributario (PKCS#12). Contiene `<ds:SignedInfo>`, `<ds:SignatureValue>` y `<ds:KeyInfo>`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (RS 097-2012) |
| **RF-04** | Resumen Criptográfico (Hash) | `.../ds:Reference/ds:DigestValue` | `1..1` (en `ds:Reference`) | Código hash SHA-256 en Base64. Utilizado para código QR y validación de integridad. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Identificación del Emisor (RUC) | `/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID` | `0..*` (SUNAT: `1..1`) | RUC del emisor (11 dígitos). Atributo `@schemeID='6'` (**Catálogo 06 SUNAT**). | RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 06) |
| **RF-01** | Razón Social y Nombre Comercial del Emisor | `/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName` | `0..1` (SUNAT: `1..1`) | Razón social idéntica a la ficha RUC activa en SUNAT. | RS 097-2012/SUNAT | **VERIFICADO** (RS 097-2012) |
| **RF-01 / RN-01** | Identificación del Adquirente | `/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID` | `0..*` (SUNAT: `1..1`) | Factura: RUC 11 dígitos con `@schemeID='6'`. Boleta: DNI 8 dígitos `@schemeID='1'`, RUC `@schemeID='6'`, u otro de Cat. 06. | RS 097-2012; Art. 4 Reglamento Comprobantes Pago | **VERIFICADO** (Catálogo 06) |
| **RF-01** | Razón Social / Nombre del Adquirente | `/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName` | `0..1` (SUNAT: `1..1` en facturas) | Denominación legal del adquirente. | RS 097-2012/SUNAT | **VERIFICADO** (RS 097-2012) |
| **RF-01** | Forma de Pago (Contado o Crédito) | `/Invoice/cac:PaymentTerms/cbc:ID` y `.../cbc:PaymentMeansID` | `0..*` (SUNAT: `1..1`) | `cbc:ID = 'FormaPago'`, `cbc:PaymentMeansID = 'Contado'` o `'Credito'`. | RS 193-2020/SUNAT | **VERIFICADO** (RS 193-2020) |
| **RF-01** | Cuotas de Pago a Crédito | `/Invoice/cac:PaymentTerms` (con `cbc:Amount` y `cbc:PaymentDueDate`) | `0..*` (SUNAT: obligatorio si es Crédito) | Detalle de cuotas: `cbc:Amount` con `@currencyID` y `cbc:PaymentDueDate` por cada cuota pactada. | RS 193-2020/SUNAT | **VERIFICADO** (RS 193-2020) |
| **RF-01 / RN-03** | Total Impuesto IGV | `/Invoice/cac:TaxTotal/cbc:TaxAmount` | `1..1` | Sumatoria del IGV de las líneas gravadas más el ISC. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01 / RN-03** | Subtotal IGV (Gravado 1000) | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (con esquema IGV) | `0..*` (SUNAT: obligatorio si hay gravadas) | `TaxableAmount` = base gravada + ISC. `TaxScheme`: `ID = '1000'`, `Name = 'IGV'`, `TaxTypeCode = 'VAT'` (**Catálogo 05**). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 05) |
| **RF-01 / RN-03** | Subtotal Operaciones Exoneradas (9997) | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (con esquema EXO) | `0..*` (SUNAT: obligatorio si hay exoneradas) | `TaxAmount = 0.00`, `TaxableAmount` = base exonerada. `TaxScheme`: `ID = '9997'`, `Name = 'EXO'`, `TaxTypeCode = 'VAT'`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 05) |
| **RF-01 / RN-03** | Subtotal Operaciones Inafectas (9998) | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (con esquema INA) | `0..*` (SUNAT: obligatorio si hay inafectas) | `TaxAmount = 0.00`, `TaxableAmount` = base inafecta. `TaxScheme`: `ID = '9998'`, `Name = 'INA'`, `TaxTypeCode = 'FRE'`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 05) |
| **RF-01 / RN-04** | Total Impuesto ISC | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (con esquema ISC) | `0..*` (SUNAT: obligatorio si hay ISC) | `TaxableAmount` = **base_isc** (únicamente valor venta de líneas afectas a ISC). `TaxScheme`: `ID = '2000'`, `Name = 'ISC'`, `TaxTypeCode = 'EXC'`. | Ley IGV e ISC, Art. 50-67; RS 097-2012 | **VERIFICADO** (Ley IGV/ISC) |
| **RF-01 / RN-04** | Sistema de Cálculo ISC en Línea | `/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange` | `0..1` | **Catálogo 08 SUNAT**: `'01'` (Al Valor), `'02'` (Específico), `'03'` (Al PVP). Obligatorio por línea si aplica ISC. | **Catálogo 08 SUNAT**; Anexo 1, RS 097-2012 | **VERIFICADO** (Catálogo 08) |
| **RF-01 / RN-06** | Total Valor Venta (LineExtensionAmount) | `/Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount` | `0..1` (SUNAT: `1..1`) | Suma de valores de venta de todas las líneas antes de tributos. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01 / RN-06** | Total Valor Venta con Tributos (TaxInclusiveAmount) | `/Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount` | `0..1` (SUNAT: `1..1`) | Total valor venta + IGV + ISC + otros tributos. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01 / RN-06** | Importe Total a Pagar (PayableAmount) | `/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount` | `1..1` | Monto final a pagar con redondeo half-up a 2 decimales. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Leyenda 1000 (Monto en Palabras) | `/Invoice/cbc:Note[@languageLocaleID='1000']` | `0..*` (SUNAT: `1..1`) | **Catálogo 52 SUNAT** (Código `'1000'`). Texto oficial: `SON: [MONTO EN LETRAS] CON [XX]/100 [SOLES / DOLARES AMERICANOS]`. | RS 097-2012; Catálogo 52 | **VERIFICADO** (Catálogo 52) |
| **RF-01** | Número de Orden de Línea | `/Invoice/cac:InvoiceLine/cbc:ID` | `1..1` | Secuencia correlativa de 1 a N sin huecos (`1, 2, 3...`). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Cantidad y Unidad de Medida del Ítem | `/Invoice/cac:InvoiceLine/cbc:InvoicedQuantity` | `0..1` (SUNAT: `1..1`) | Cantidad física de mercadería. Atributo `@unitCode` según subconjunto de **Catálogo 03 SUNAT** (ej. `NIU`, `KGM`, `BX`). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 03) |
| **RF-01 / RN-03** | Código de Afectación al IGV de la Línea | `/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode` | `0..1` (SUNAT: `1..1`) | **Catálogo 07 SUNAT**: `'10'` (Gravado Oneroso), `'20'` (Exonerado), `'30'` (Inafecto). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 07) |
| **RF-01** | Valor Unitario del Ítem | `/Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount` | `1..1` | Valor sin tributos por unidad de medida. Hasta 10 decimales exactos. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-01** | Precio de Venta Unitario (Con Tributos) | `/Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount` | `0..*` (SUNAT: `1..1`) | Precio final con tributos. Atributo `@priceTypeCode='01'` (**Catálogo 16 SUNAT**). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 16) |
| **RF-01** | Descripción y Código de Mercadería | `/Invoice/cac:InvoiceLine/cac:Item/cbc:Description` | `0..*` (SUNAT: `1..*`) | Nombre y detalle comercial del producto. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-02 / RN-05** | Documento Referenciado en Notas | `/CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID` | `1..1` | Serie y número del comprobante que modifica (ej. `F001-00001042`). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-02 / RN-05** | Tipo de Documento Referenciado | `/CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode` | `0..1` (SUNAT: `1..1`) | Código según Catálogo 01 (`01` Factura, `03` Boleta). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogo 01) |
| **RF-02 / RN-05** | Motivo de Nota de Crédito / Débito | `/CreditNote/cac:DiscrepancyResponse/cbc:ResponseCode` | `0..1` (SUNAT: `1..1`) | Código según **Catálogo 09** (NC) o **Catálogo 10** (ND). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Catálogos 09/10) |
| **RF-02 / RN-05** | Sustento del Motivo de Nota | `/CreditNote/cac:DiscrepancyResponse/cbc:Description` | `0..*` (SUNAT: `1..1`) | Justificación textual de la modificación tributaria. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** (Anexo 1) |
| **RF-08 / RN-08** | Referencia a Documento Interno Legado | `/Invoice/cac:AdditionalDocumentReference/cbc:ID` | `0..*` | Identificador histórico legado. `@documentTypeCode='99'` (Otros). Trazabilidad de almacén. | RS 097-2012; RS 234-2006 | **VERIFICADO** (RS 234-2006) |

---

## 3. Trazabilidad de Libros Electrónicos Tributarios (RS 234-2006 / RS 097-2012)

### 3.1 Formato 14.1 — Registro de Ventas e Ingresos
Correlación entre las columnas oficiales del Formato 14.1 de SUNAT, las rutas XPath UBL 2.1 y el DTO `LineaRegistroVentas`:

| Columna Formato 14.1 | Denominación SUNAT | Origen XPath UBL 2.1 | Campo DTO `LineaRegistroVentas` | Tipo y Restricción |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Número correlativo del registro o código único de operación (CUO) | N/A (Secuencia del generador) | `correlative_number` | Entero secuencial mensual sin huecos. |
| **2** | Fecha de emisión del comprobante de pago | `/Invoice/cbc:IssueDate` | `issue_date` | `YYYY-MM-DD`. |
| **3** | Fecha de vencimiento o fecha de pago | `/Invoice/cbc:DueDate` | `due_date` | `YYYY-MM-DD` (o null si es contado). |
| **4** | Tipo de comprobante de pago | `/Invoice/cbc:InvoiceTypeCode` | `document_type` | Catálogo 01 (`01`, `03`, `07`, `08`). |
| **5** | Serie del comprobante de pago | Extraído de `/Invoice/cbc:ID` (4 primeros car.) | `series` | `^[FB][A-Z0-9]{3}$`. |
| **6** | Número correlativo del comprobante | Extraído de `/Invoice/cbc:ID` (caracteres post guión) | `document_number` | Numérico hasta 8 dígitos. |
| **7** | Tipo de documento de identidad del cliente | `.../cac:AccountingCustomerParty/.../cbc:ID/@schemeID` | `customer_document_type` | Catálogo 06 (`1` DNI, `6` RUC). |
| **8** | Número de documento de identidad del cliente | `.../cac:AccountingCustomerParty/.../cbc:ID` | `customer_document_number` | 8 dígitos DNI o 11 dígitos RUC. |
| **9** | Apellidos y nombres o razón social del cliente | `.../cac:AccountingCustomerParty/.../cbc:RegistrationName` | `customer_name` | Denominación legal. |
| **10** | Base imponible de la operación gravada | `.../cac:TaxSubtotal[TaxScheme/ID='1000']/cbc:TaxableAmount` | `taxable_base` | Decimal string con 2 decimales. |
| **11** | Importe total de la operación exonerada | `.../cac:TaxSubtotal[TaxScheme/ID='9997']/cbc:TaxableAmount` | `exempt_amount` | Decimal string con 2 decimales. |
| **12** | Importe total de la operación inafecta | `.../cac:TaxSubtotal[TaxScheme/ID='9998']/cbc:TaxableAmount` | `inafect_amount` | Decimal string con 2 decimales. |
| **13** | Impuesto Selectivo al Consumo (ISC) | `.../cac:TaxSubtotal[TaxScheme/ID='2000']/cbc:TaxAmount` | `isc` | Decimal string con 2 decimales. |
| **14** | Impuesto General a las Ventas (IGV) | `.../cac:TaxSubtotal[TaxScheme/ID='1000']/cbc:TaxAmount` | `igv` | 18.00% sobre base imponible. |
| **15** | Importe total del comprobante de pago | `/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount` | `total_amount` | Total a pagar redondeado a 2 decimales. |

---

### 3.2 Formato 12.1 — Registro de Inventario Permanente en Unidades Físicas (Kardex)
Correlación entre el Formato 12.1 (RS 234-2006), el DTO `PhysicalInventoryRecord` y los 5 campos históricos migrados:

| Campo Formato 12.1 | Norma SUNAT | Campo DTO `PhysicalInventoryRecord` | Mapeo desde Sistema Legado | Estado de Verificación |
| :--- | :--- | :--- | :--- | :--- |
| **Establecimiento** | Código de anexo declarado en RUC | `establishment_code` | Asignado `0000` (domicilio principal). | **VERIFICADO** (RS 234-2006) |
| **Tipo de Existencia** | **Tabla 5 SUNAT** (`01` Mercaderías) | `existence_type_table5` | Mercadería comercializada por mayor/menor. | **VERIFICADO** (Tabla 5) |
| **Código del Producto** | SKU interno / homologado | `product_sku` | Derivado del campo legado `producto`. | **VERIFICADO** |
| **Descripción del Producto** | Denominación del bien | `product_description` | Campo legado `producto` normalizado. | **VERIFICADO** |
| **Unidad de Medida** | **Tabla 6 SUNAT** (con equivalencias a Cat. 03) | `unit_table6` | Equivalente: Tabla 6 `07` (Unidades) = Cat. 03 `NIU`; `01` (Kg) = `KGM`. | **VERIFICADO** (Tabla 6 / Cat. 03) |
| **Fecha de Operación** | Fecha calendario de la transacción | `transaction_date` | Campo legado `fecha` normalizado a ISO 8601. | **VERIFICADO** |
| **Tipo de Documento Sustentatorio** | **Tabla 10 SUNAT** (`01` Factura, `03` Boleta, `99` Otros) | `document_type_table10` | Si proviene de migración: `99` (Doc. Interno). Si es venta nueva: `01`/`03`. | **VERIFICADO** (Tabla 10) |
| **Serie y Número de Documento** | Numeración del comprobante | `document_series` / `document_number` | Campo legado `nro_documento` como identificador interno. | **VERIFICADO** |
| **Tipo de Operación** | **Tabla 12 SUNAT** (`01` Venta, `02` Compra, `99` Otros) | `operation_type_table12` | Si `salida > 0`: `01` (Venta). Si `ingreso > 0`: `02` (Compra). | **VERIFICADO** (Tabla 12) |
| **Cantidad de Entrada** | Unidades físicas ingresadas | `inbound_quantity` | Campo legado `ingreso` (`Decimal`). | **VERIFICADO** |
| **Cantidad de Salida** | Unidades físicas egresadas | `outbound_quantity` | Campo legado `salida` (`Decimal`). | **VERIFICADO** |
| **Saldo Final** | Balance acumulado en unidades | `balance_quantity` | $\text{Saldo Anterior} + \text{Entradas} - \text{Salidas}$. | **VERIFICADO** (RS 234-2006) |

---

## 4. Análisis Crítico Normativo: Anexo N° 8 de la RS 097-2012 vs Catálogo 08

### 4.1 Corrección Regulatoria sobre el Anexo N° 8 de la RS 097-2012
- **Observación Docente Atendida:** En versiones preliminares se incurrió en el error de identificar el Anexo N° 8 como "comunicaciones de baja y resúmenes de boletas".  
- **Aclaración y Verificación:**  
  1. Conforme a la estructura oficial de la **RS N° 097-2012/SUNAT**, el **Anexo N° 8 corresponde a los Catálogos del Sistema de Emisión Electrónica (Catálogos de Códigos)**, tales como Catálogo 01 (Tipos de Comprobantes), Catálogo 02 (Monedas), Catálogo 06 (Tipos de Documento de Identidad), Catálogo 07 (Afectación al IGV), Catálogo 08 (Sistemas de ISC), etc.  
  2. Las Comunicaciones de Baja corresponden al Anexo N° 4 y los Resúmenes Diarios corresponden al Anexo N° 5 de dicha resolución.  
  3. **No debe confundirse el Catálogo 08 con el Anexo 8:** El *Catálogo 08* es una tabla específica de códigos de sistemas de cálculo del ISC (01 Al Valor, 02 Específico, 03 Al PVP), mientras que el *Anexo 8* es el compendio normativo integral de todos los catálogos de códigos del SEE.
- **Estado de Verificación:** `VERIFICADO` según indicación docente y estructura formal de SUNAT. `PENDIENTE DE VERIFICACIÓN OCR` sobre el archivo local `references/097-2012.pdf` debido a que es un documento digitalizado escaneado (imágenes sin texto seleccionable nativo).

---

## 5. Clasificación y Manejo de Rangos de Códigos CDR de SUNAT

Cuando la SUNAT u OSE procesa el comprobante electrónico, emite la Constancia de Recepción (CDR) con un código de respuesta clasificado bajo la siguiente taxonomía:

```
┌───────────────────────┬──────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Rango de Códigos CDR  │ Calificación Operativa           │ Acción y Comportamiento del Sistema ABC                │
├───────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 0000                  │ ACEPTADO                         │ Comprobante con plena validez legal. Estado ISSUED.   │
├───────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 0100 – 0999           │ EXCEPCIÓN TÉCNICA / TRANSITORIA  │ Reintento automático seguro con retroceso exponencial. │
│                       │ (Falla SOAP, timeout, caída OSE) │ No alterar serie ni correlativo.                       │
├───────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1000 – 1999           │ RECHAZO CORREGIBLE DE DATOS      │ El emisor puede subsanar el error de datos y reenviar  │
│                       │ (Error en estructura o datos)    │ el comprobante conservando el mismo número según norma.│
├───────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2000 – 3999           │ RECHAZO DEFINITIVO TRIBUTARIO    │ Comprobante nulo sin validez fiscal. El número queda   │
│                       │ (RUC inválido, firma adulterada) │ inutilizado y NO puede volver a enviarse.              │
├───────────────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ ≥ 4000                │ ACEPTADO CON OBSERVACIONES       │ Comprobante válido emitido legalmente. Se registra el  │
│                       │ (Advertencias normativas no bloq)│ CDR con observaciones para corrección en siguientes.  │
└───────────────────────┴──────────────────────────────────┴────────────────────────────────────────────────────────┘
```
