import openpyxl
from openpyxl.styles import Font, PatternFill

wb = openpyxl.load_workbook('specs/Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx')
ws_matriz = wb['Matriz SUNAT UBL']

# Update row 2 version
ws_matriz.cell(2, 1, 'ABC Software Corp  •  Spec-First  •  Versión 2.0.0  •  05/11/2026')

max_r = ws_matriz.max_row
print('Current max row in Matriz:', max_r)

for r in range(5, max_r + 1):
    val = ws_matriz.cell(r, 5).value or ''
    if 'XAdES-BES' in val:
        ws_matriz.cell(r, 5, val.replace('XAdES-BES', 'XMLDSig Enveloped'))
        print(f'Updated XAdES-BES in row {r}')

new_rows = [
    ('RF-01 / RN-09', 'Tipo de Operación', '/Invoice/cbc:InvoiceTypeCode/@listID', 'Atributo opcional en XSD', 'Catálogo 51 SUNAT: Código 0101 (Venta interna), etc. Obligatorio por SUNAT.', 'RS 097-2012/SUNAT; Catálogo 51', 'VERIFICADO'),
    ('RF-01', 'Forma de Pago (Contado o Crédito)', '/Invoice/cac:PaymentTerms/cbc:ID y cbc:PaymentMeansID', '0..* (SUNAT: 1..1)', 'FormaPago: Contado o Credito según RS 193-2020.', 'RS 193-2020/SUNAT', 'VERIFICADO'),
    ('RF-01', 'Cuotas de Pago a Crédito', '/Invoice/cac:PaymentTerms (con cbc:Amount y cbc:PaymentDueDate)', '0..* (Obligatorio si Crédito)', 'Monto y fecha de vencimiento por cuota pactada.', 'RS 193-2020/SUNAT', 'VERIFICADO'),
    ('RF-01 / RN-03', 'Subtotal Operaciones Exoneradas (9997)', '/Invoice/cac:TaxTotal/cac:TaxSubtotal (esquema EXO)', '0..* (SUNAT: obligatorio si aplica)', 'TaxAmount = 0.00, TaxableAmount = base exonerada. TaxScheme ID 9997, Name EXO, TaxTypeCode VAT.', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO'),
    ('RF-01 / RN-03', 'Subtotal Operaciones Inafectas (9998)', '/Invoice/cac:TaxTotal/cac:TaxSubtotal (esquema INA)', '0..* (SUNAT: obligatorio si aplica)', 'TaxAmount = 0.00, TaxableAmount = base inafecta. TaxScheme ID 9998, Name INA, TaxTypeCode FRE.', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO'),
    ('RF-01 / RN-06', 'Total Valor Venta con Tributos (TaxInclusiveAmount)', '/Invoice/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount', '0..1 (SUNAT: 1..1)', 'Total valor venta + IGV + ISC + otros tributos. Atributo @currencyID.', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO'),
    ('RF-01', 'Leyenda 1000 (Monto en Palabras)', "/Invoice/cbc:Note[@languageLocaleID='1000']", '0..* (SUNAT: 1..1)', 'Catálogo 52 SUNAT (Código 1000). Monto en letras oficial.', 'RS 097-2012; Catálogo 52', 'VERIFICADO'),
    ('RF-02 / RN-05', 'Documento Referenciado en Notas', '/CreditNote/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID', '1..1', 'Serie y número del comprobante que modifica (ej. F001-00001042).', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO'),
    ('RF-02 / RN-05', 'Motivo de Nota de Crédito / Débito', '/CreditNote/cac:DiscrepancyResponse/cbc:ResponseCode', '0..1 (SUNAT: 1..1)', 'Código según Catálogo 09 (NC) o Catálogo 10 (ND).', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO'),
    ('RF-02 / RN-05', 'Sustento del Motivo de Nota', '/CreditNote/cac:DiscrepancyResponse/cbc:Description', '0..* (SUNAT: 1..1)', 'Descripción detallada de la modificación o anulación.', 'Anexo 1, RS 097-2012/SUNAT', 'VERIFICADO')
]

for row_data in new_rows:
    max_r += 1
    for c, val in enumerate(row_data, 1):
        ws_matriz.cell(max_r, c, val)

# Create sheet Formato 14.1 - Ventas
if 'Formato 14.1 - Ventas' in wb.sheetnames:
    del wb['Formato 14.1 - Ventas']
ws_14 = wb.create_sheet(title='Formato 14.1 - Ventas')
ws_14.cell(1, 1, 'REGISTRO DE VENTAS E INGRESOS — FORMATO 14.1 (RS 234-2006 / RS 097-2012)')
ws_14.cell(1, 1).font = Font(bold=True, size=12)
headers_14 = ['Col. 14.1', 'Denominación SUNAT', 'Origen XPath UBL 2.1', 'Campo DTO LineaRegistroVentas', 'Tipo y Restricción']
for c, h in enumerate(headers_14, 1):
    cell = ws_14.cell(3, c, h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')

rows_14 = [
    (1, 'Número correlativo / CUO', 'N/A (Secuencia del generador)', 'correlative_number', 'Integer secuencial mensual'),
    (2, 'Fecha de emisión', '/Invoice/cbc:IssueDate', 'issue_date', 'YYYY-MM-DD'),
    (3, 'Fecha de vencimiento', '/Invoice/cbc:DueDate', 'due_date', 'YYYY-MM-DD (o null)'),
    (4, 'Tipo de comprobante', '/Invoice/cbc:InvoiceTypeCode', 'document_type', 'Catálogo 01 (01, 03, 07, 08)'),
    (5, 'Serie del comprobante', 'Extraído de /Invoice/cbc:ID', 'series', '^[FB][A-Z0-9]{3}$'),
    (6, 'Número del comprobante', 'Extraído de /Invoice/cbc:ID', 'document_number', 'Numérico hasta 8 dígitos'),
    (7, 'Tipo documento identidad cliente', '.../cac:AccountingCustomerParty/.../cbc:ID/@schemeID', 'customer_document_type', 'Catálogo 06 (1 DNI, 6 RUC)'),
    (8, 'Número documento identidad cliente', '.../cac:AccountingCustomerParty/.../cbc:ID', 'customer_document_number', '8 dígitos DNI o 11 dígitos RUC'),
    (9, 'Razón social / Nombres cliente', '.../cac:AccountingCustomerParty/.../cbc:RegistrationName', 'customer_name', 'Denominación legal adquirente'),
    (10, 'Base imponible gravada', '.../cac:TaxSubtotal[TaxScheme/ID="1000"]/cbc:TaxableAmount', 'taxable_base', 'Decimal string 2 decimales'),
    (11, 'Importe exonerado', '.../cac:TaxSubtotal[TaxScheme/ID="9997"]/cbc:TaxableAmount', 'exempt_amount', 'Decimal string 2 decimales'),
    (12, 'Importe inafecto', '.../cac:TaxSubtotal[TaxScheme/ID="9998"]/cbc:TaxableAmount', 'inafect_amount', 'Decimal string 2 decimales'),
    (13, 'ISC', '.../cac:TaxSubtotal[TaxScheme/ID="2000"]/cbc:TaxAmount', 'isc', 'Decimal string 2 decimales'),
    (14, 'IGV', '.../cac:TaxSubtotal[TaxScheme/ID="1000"]/cbc:TaxAmount', 'igv', 'Decimal string 2 decimales'),
    (15, 'Importe total', '/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount', 'total_amount', 'Decimal string 2 decimales')
]
for r_idx, r_data in enumerate(rows_14, 4):
    for c_idx, val in enumerate(r_data, 1):
        ws_14.cell(r_idx, c_idx, val)

# Create sheet Formato 12.1 - Kardex
if 'Formato 12.1 - Kardex' in wb.sheetnames:
    del wb['Formato 12.1 - Kardex']
ws_12 = wb.create_sheet(title='Formato 12.1 - Kardex')
ws_12.cell(1, 1, 'REGISTRO DE INVENTARIO PERMANENTE EN UNIDADES FÍSICAS — FORMATO 12.1 (RS 234-2006)')
ws_12.cell(1, 1).font = Font(bold=True, size=12)
headers_12 = ['Campo Formato 12.1', 'Norma SUNAT', 'Campo DTO PhysicalInventoryRecord', 'Mapeo Legado ABC', 'Estado Verificación']
for c, h in enumerate(headers_12, 1):
    cell = ws_12.cell(3, c, h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')

rows_12 = [
    ('Establecimiento', 'Código anexo RUC SUNAT', 'establishment_code', 'Fijo 0000 (Domicilio principal)', 'VERIFICADO (RS 234-2006)'),
    ('Tipo de existencia', 'Tabla 5 SUNAT (01 Mercaderías)', 'existence_type_table5', 'Mercadería de abarrotes por mayor/menor', 'VERIFICADO (Tabla 5)'),
    ('Código del producto', 'SKU interno homologado', 'product_sku', 'Derivado del campo producto legado', 'VERIFICADO'),
    ('Descripción del producto', 'Descripción comercial', 'product_description', 'Campo producto normalizado', 'VERIFICADO'),
    ('Unidad de medida', 'Tabla 6 SUNAT (equiv. Cat. 03)', 'unit_table6', 'Tabla 6 código 07 (Unid)=NIU; 01 (Kg)=KGM', 'VERIFICADO (Tabla 6)'),
    ('Fecha de transacción', 'Fecha calendario ISO 8601', 'transaction_date', 'Campo fecha normalizado', 'VERIFICADO'),
    ('Tipo documento sustentatorio', 'Tabla 10 SUNAT (01 Factura, 99 Interno)', 'document_type_table10', 'Campo nro_documento legado (tipo 99)', 'VERIFICADO (Tabla 10)'),
    ('Serie y correlativo documento', 'Numeración formal o referencia', 'document_series / document_number', 'Campo nro_documento legado', 'VERIFICADO'),
    ('Tipo de operación', 'Tabla 12 SUNAT (01 Venta, 02 Compra)', 'operation_type_table12', 'salida > 0: 01 (Venta); ingreso > 0: 02 (Compra)', 'VERIFICADO (Tabla 12)'),
    ('Cantidad entrada', 'Unidades físicas ingresadas', 'inbound_quantity', 'Campo ingreso legado (Decimal)', 'VERIFICADO'),
    ('Cantidad salida', 'Unidades físicas retiradas', 'outbound_quantity', 'Campo salida legado (Decimal)', 'VERIFICADO'),
    ('Saldo físico final', 'Balance acumulado unidades', 'balance_quantity', 'Saldo ant + entradas - salidas', 'VERIFICADO (RS 234-2006)')
]
for r_idx, r_data in enumerate(rows_12, 4):
    for c_idx, val in enumerate(r_data, 1):
        ws_12.cell(r_idx, c_idx, val)

# Create sheet Rangos CDR SUNAT
if 'Rangos CDR SUNAT' in wb.sheetnames:
    del wb['Rangos CDR SUNAT']
ws_cdr = wb.create_sheet(title='Rangos CDR SUNAT')
ws_cdr.cell(1, 1, 'CLASIFICACIÓN DE CÓDIGOS DE RESPUESTA CDR SUNAT / OSE')
ws_cdr.cell(1, 1).font = Font(bold=True, size=12)
headers_cdr = ['Rango de Códigos', 'Calificación SUNAT / OSE', 'Acción y Comportamiento del Sistema ABC Corp', 'Reutilización de Numeración']
for c, h in enumerate(headers_cdr, 1):
    cell = ws_cdr.cell(3, c, h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')

rows_cdr = [
    ('0000', 'ACEPTADO', 'Comprobante válido legalmente. Estado ISSUED_ACCEPTED. Almacenar XML y CDR.', 'Comprobante finalizado con éxito.'),
    ('0100 – 0999', 'EXCEPCIÓN TÉCNICA / TRANSITORIA', 'Error de comunicaciones SOAP o caída temporal de OSE/SUNAT. Reintento automático seguro con backoff.', 'Mantiene la misma serie y correlativo para reintento.'),
    ('1000 – 1999', 'RECHAZO CORREGIBLE DE DATOS', 'Error en contenido tributario subsanable. Corregir datos y reenviar a SUNAT.', 'Autorizado a reenviar bajo el mismo número según norma SUNAT.'),
    ('2000 – 3999', 'RECHAZO DEFINITIVO TRIBUTARIO', 'Comprobante nulo sin validez fiscal (RUC no habido, firma adulterada). Estado REJECTED.', 'PROHIBIDO reutilizar serie y correlativo. La numeración queda inutilizada.'),
    ('≥ 4000', 'ACEPTADO CON OBSERVACIONES', 'Comprobante con validez legal emitido con código 0 y advertencias no bloqueantes.', 'Válido. Registrar observaciones para subsanar en emisiones futuras.')
]
for r_idx, r_data in enumerate(rows_cdr, 4):
    for c_idx, val in enumerate(r_data, 1):
        ws_cdr.cell(r_idx, c_idx, val)

# Update sheet Notas y alcance
ws_notas = wb['Notas y alcance']
ws_notas.cell(6, 1, 'CORRECCIÓN NORMATIVA CRÍTICA: En la RS N° 097-2012/SUNAT, el Anexo N° 8 corresponde a los Catálogos de Códigos del Sistema de Emisión Electrónica (no a comunicaciones de baja y resúmenes). No debe confundirse el Catálogo 08 (Sistemas de cálculo de ISC) con el Anexo 8 (Compendio normativo de catálogos).')
ws_notas.cell(6, 1).font = Font(bold=True, color='C00000')

wb.save('specs/Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx')
print('Successfully updated specs/Matriz_Trazabilidad_SUNAT_UBL_ABC.xlsx!')

