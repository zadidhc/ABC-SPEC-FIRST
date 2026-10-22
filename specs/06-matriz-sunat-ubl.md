# SPEC 04 — Matriz de Trazabilidad Normativa SUNAT – OASIS UBL 2.1

**Versión:** 1.0.0  
**Fecha:** 22 de octubre de 2026  
**Fase:** Fase 1 — Especificación Técnica Spec-First  
**Autor:** Senior Software Architect  
**Estado:** BORRADOR — PENDIENTE DE REVISIÓN

---

## 1. Alcance Normativo y Criterios de Rigor Legal

Esta matriz correlaciona cada regla de negocio y requisito funcional de **ABC Software Corp** con la gramática formal del estándar **OASIS UBL Invoice 2.1** (`referencias/UBL-Invoice-2.1.xml`), los catálogos oficiales de la **SUNAT**, y las resoluciones de superintendencia peruanas aplicables:
- **RS N° 097-2012/SUNAT** y modificatorias: Crea el Sistema de Emisión Electrónica desarrollado desde los sistemas del contribuyente (SEE-Del Contribuyente), estableciendo las especificaciones técnicas de los comprobantes de pago electrónicos.
- **RS N° 234-2006/SUNAT**: Marco regulatorio histórico de libros y registros vinculados a asuntos tributarios (control de inventario permanente / kardex valorizado).
- **Ley N° 30884 y RS N° 150-2019/SUNAT**: Regula el Impuesto al Consumo de las Bolsas de Plástico (ICBPER).
- **Catálogo 08 SUNAT**: Códigos de tipos de sistema de cálculo del Impuesto Selectivo al Consumo (ISC).

> **Distinción Jurídica y Técnica Esencial:**  
> Un elemento definido como opcional (`minOccurs="0"`) en el esquema base OASIS UBL 2.1 puede ser de **consignación obligatoria e indelegable** según la normativa tributaria peruana para que el comprobante adquiera validez fiscal ante SUNAT/OSE.

---

## 2. Matriz de Trazabilidad: Requisitos $\rightarrow$ UBL 2.1 $\rightarrow$ SUNAT

| ID Req / Regla | Concepto de Negocio | Elemento / Ruta UBL 2.1 | Cardinalidad XSD OASIS | Regla / Catálogo SUNAT | Fuente Normativa Exacta | Estado de Verificación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01 / RN-02** | Numeración: Serie y Correlativo | `/Invoice/cbc:ID` | `1..1` | Formato `F[A-Z0-9]{3}-[0-9]{1,8}` (ej. `F001-00001042`). Serie inicia con F para facturas. | Anexo 1, RS 097-2012/SUNAT; RS 193-2020/SUNAT | **VERIFICADO** |
| **RF-01** | Fecha de Emisión del Comprobante | `/Invoice/cbc:IssueDate` | `1..1` | Formato fecha `YYYY-MM-DD`. No mayor al día de emisión ni anterior al plazo máximo de envío (3 días calendario). | RS 097-2012/SUNAT; RS 150-2021/SUNAT | **VERIFICADO** |
| **RF-01** | Hora de Emisión | `/Invoice/cbc:IssueTime` | `0..1` | Formato `HH:MM:SS`. Obligatorio según normativa vigente para trazabilidad horaria. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-01** | Tipo de Comprobante | `/Invoice/cbc:InvoiceTypeCode` | `0..1` | **Catálogo 01 SUNAT**: Código `'01'` (Factura). En UBL base es `0..1`, pero SUNAT exige `1..1`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Tipo de Moneda de la Factura | `/Invoice/cbc:DocumentCurrencyCode` | `0..1` | **Catálogo 02 SUNAT** / ISO 4217 (ej. `'PEN'`, `'USD'`). Exigido por SUNAT en la cabecera. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-04** | Contenedor de Extensiones y Firma Digital | `/Invoice/ext:UBLExtensions` | `0..1` | Contenedor para `ext:UBLExtension/ext:ExtensionContent/ds:Signature`. Resguardo de XAdES-BES. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-04** | Resumen Criptográfico (Hash) | `.../ds:DigestValue` | `1..1` (en `ds:Reference`) | Código hash SHA-256 en Base64. Utilizado para generar el código QR y validar autenticidad. | RS 097-2012/SUNAT; Anexo 1 | **VERIFICADO** |
| **RF-01** | Identificación del Emisor (RUC) | `/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID` | `0..*` | RUC del emisor (11 dígitos). Atributo `@schemeID='6'` (**Catálogo 06 SUNAT**). | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Razón Social del Emisor | `/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName` | `0..1` | Nombre o razón social idéntica a la ficha RUC activa en SUNAT. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-01** | Identificación del Adquirente (RUC) | `/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID` | `0..*` | Para Facturas ('01'), obligatorio RUC de 11 dígitos, `@schemeID='6'`. SUNAT rechaza si no es RUC activo/habido. | RS 097-2012/SUNAT; Art. 4 Reglamento Comprobantes Pago | **VERIFICADO** |
| **RF-01** | Razón Social del Adquirente | `/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName` | `0..1` | Denominación legal del adquirente. Exigido por SUNAT `1..1`. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-03** | Total Impuesto IGV | `/Invoice/cac:TaxTotal/cbc:TaxAmount` | `1..1` | Sumatoria del IGV liquidado en las líneas gravadas. Atributo `@currencyID`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-03** | Subtotal IGV y Esquema Tributario | `/Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme` | `1..1` | `cbc:ID = '1000'`, `cbc:Name = 'IGV'`, `cbc:TaxTypeCode = 'VAT'` (**Catálogo 05 SUNAT**). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-04** | Total Impuesto ISC | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (con esquema ISC) | `0..*` | `cbc:ID = '2000'`, `cbc:Name = 'ISC'`, `cbc:TaxTypeCode = 'EXC'`. Aplicable si existen bienes afectos a ISC. | Ley del IGV e ISC, Art. 50-67; RS 097-2012 | **VERIFICADO** |
| **RF-01 / RN-04** | Sistema de Cálculo ISC | `/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange` | `0..1` | **Catálogo 08 SUNAT**: Código del sistema: `'01'` (Al Valor), `'02'` (Específico), `'03'` (Al Precio Venta al Público). | **Catálogo 08 SUNAT**; Anexo 1, RS 097-2012 | **VERIFICADO** |
| **RF-01 / RN-05** | Total Impuesto a las Bolsas (ICBPER) | `/Invoice/cac:TaxTotal/cac:TaxSubtotal` (esquema OTH) | `0..*` | `cbc:ID = '7152'`, `cbc:Name = 'ICBPER'`, `cbc:TaxTypeCode = 'OTH'`. Monto fijo por cantidad de bolsas plásticas. | Ley N° 30884; RS 150-2019/SUNAT | **VERIFICADO** |
| **RF-01 / RN-06** | Total Valor Venta (Base Imponible) | `/Invoice/cac:LegalMonetaryTotal/cbc:LineExtensionAmount` | `0..1` | Suma de los valores de venta de cada ítem antes de tributos y después de descuentos de línea. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-06** | Importe Total a Pagar | `/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount` | `1..1` | Monto final adeudado: Valor Venta + IGV + ISC + ICBPER - Descuentos Globales + Otros Cargos. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Número de Orden de Línea | `/Invoice/cac:InvoiceLine/cbc:ID` | `1..1` | Secuencia correlativa de 1 a N sin huecos (`1, 2, 3...`). | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Cantidad y Unidad de Medida del Ítem | `/Invoice/cac:InvoiceLine/cbc:InvoicedQuantity` | `0..1` | Cantidad física de la mercadería. Atributo `@unitCode` según **Catálogo 03 SUNAT** (ej. `NIU`, `KGM`, `BX`). SUNAT exige `1..1`. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01 / RN-03** | Código de Afectación al IGV de la Línea | `/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode` | `0..1` | **Catálogo 07 SUNAT**: Códigos `'10'` (Gravado Oneroso), `'20'` (Exonerado), `'30'` (Inafecto), etc. Obligatorio por línea. | Anexo 1, RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Valor Unitario del Ítem | `/Invoice/cac:InvoiceLine/cac:Price/cbc:PriceAmount` | `1..1` | Valor sin tributos por unidad de medida. Hasta 10 decimales según catálogo SUNAT. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Precio de Venta Unitario (Con Tributos) | `/Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount` | `0..*` | Precio final al consumidor por unidad (incluye IGV e ISC si aplica). `@priceTypeCode='01'` (**Catálogo 16 SUNAT**). | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-01** | Descripción de la Mercadería | `/Invoice/cac:InvoiceLine/cac:Item/cbc:Description` | `0..*` | Nombre y detalle del producto vendido. SUNAT exige al menos 1 ocurrencia. | RS 097-2012/SUNAT | **VERIFICADO** |
| **RF-07 / RN-08** | Referencia a Documento Interno Legado | `/Invoice/cac:DespatchDocumentReference/cbc:ID` o `/Invoice/cac:AdditionalDocumentReference/cbc:ID` | `0..*` | Mapeo de trazabilidad si una factura formal ampara despachos antiguos. `@documentTypeCode='99'` (Otros). | RS 097-2012/SUNAT; RS 234-2006/SUNAT | **VERIFICADO** |

---

## 3. Análisis de Resoluciones de Superintendencia y Reglas Históricas

### 3.1 Resolución de Superintendencia N° 097-2012/SUNAT
- **Vigencia y Relevancia:** Es la norma madre que crea el Sistema de Emisión Electrónica desarrollado desde los sistemas del contribuyente (SEE-Del Contribuyente). Regula la obligatoriedad de la firma digital, el uso del estándar UBL, los formatos XML, y las validaciones de estructura (Anexo 1).
- **Mecanismo de Validación:** Establece que la constancia de recepción (CDR) con código `'0'` es la única prueba legal de que la factura fue válidamente emitida y recibida por SUNAT u OSE.

### 3.2 Resolución de Superintendencia N° 234-2006/SUNAT (Kardex e Inventarios)
- **Vigencia y Relevancia:** Regula las normas referidas a libros y registros vinculados a asuntos tributarios, en particular el **Registro de Inventario Permanente Valorizado** y el **Registro de Inventario Permanente en Unidades Físicas** (Art. 13).
- **Impacto en el Legado de ABC Software Corp:**
  - Los campos históricos `fecha`, `ingreso`, `salida`, `producto` y `nro_documento` responden conceptualmente a los requerimientos del control de entradas y salidas de almacén físico exigidos en el Art. 13 de la RS 234-2006.
  - La RS 234-2006 permite registrar movimientos internos de mercadería con "comprobante de pago, guía de remisión o documento interno de control".
  - **Dictamen del Arquitecto:** Los registros migrados cumplen con el régimen de inventario de la RS 234-2006 como documentos internos, pero **no satisfacen por sí mismos las obligaciones de emisión de comprobantes de pago de la RS 097-2012**. Por ende, la separación entre `MovimientoAlmacen` y `Factura` está 100% justificada por la normativa tributaria.

---

## 4. Estado de Verificación Regulatoria y Alertas

1. **Catálogo 08 de SUNAT (Sistema de Cálculo del ISC):**
   - **Estado:** `VERIFICADO`.
   - **Contenido Oficial:**
     - `01`: Sistema al Valor (tasa porcentual sobre valor de venta).
     - `02`: Sistema Específico (monto fijo en moneda nacional por unidad física).
     - `03`: Sistema al Precio de Venta al Público (tasa porcentual sobre precio final sugerido).
   - **Aclaración Crítica:** No confundir el *Catálogo 08* (tabla de códigos para ISC) con el *Anexo 8* de la RS 097-2012 (referido a comunicaciones de baja y resúmenes de boletas).

2. **Tasa y Mecánica del ICBPER (Ley 30884):**
   - **Estado:** `VERIFICADO`.
   - **Mecanismo:** Monto fijo por bolsa plástica cobrado al adquirente (S/ 0.50 en ejercicios recientes). Se declara en el esquema de tributos bajo el código `'7152'` y código de tipo `'OTH'`.

3. **Plazo Máximo de Envío de Facturas a SUNAT/OSE:**
   - **Estado:** `PENDIENTE DE VERIFICACIÓN` (según calendario tributario específico del contribuyente y cambios entre 1 y 3 días calendario posteriores a la fecha de emisión decretados en resoluciones recientes). Se asume como política de diseño una validación preventiva de máximo 3 días calendario en el validador de negocio.

4. **Homologación con Operador de Servicios Electrónicos (OSE):**
   - **Estado:** `PENDIENTE DE VERIFICACIÓN` (respecto a la designación formal de ABC Software Corp como emisor obligatorio OSE según su volumen de ingresos o si mantiene opción de envío directo a SUNAT). La interfaz `ISunatOseClient` diseñada en SPEC 02 desacopla esta decisión sin impacto en el dominio.
