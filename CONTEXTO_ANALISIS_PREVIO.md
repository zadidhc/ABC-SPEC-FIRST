# Contexto previo de análisis — ABC Software Corp

> **IMPORTANTE:** Este archivo contiene un resumen de trabajo PRELIMINAR, NO es un entregable final ni sustituye el enunciado o la normativa oficial. Antigravity debe corregir cualquier propuesta que no sea compatible con las fuentes.

## Objetivo del examen
Primera fase **Spec-First** de un sistema de facturación electrónica y migración de registros de mercadería para ABC Software Corp. El profesor solicita exclusivamente cuatro entregables: (1) modelo de dominio y contratos DTO/Schemas, (2) diagramas de arquitectura MVC con evolución hacia hexagonal, (3) especificación de endpoints/servicios (contrato API), (4) matriz de trazabilidad SUNAT–UBL.

## Restricciones explícitas del caso
- Registros históricos del software anterior: `fecha`, `ingreso`, `salida`, `producto`, `nro_documento`; migración conservando trazabilidad.
- Considerar requerimientos SUNAT, tipos de documentos, afectación IGV, monedas, series/correlativos, reglas de emisión y **Catálogo 08**.
- Arquitectura inicial: **monolito MVC**; especificar separación para futura evolución a hexagonal/Clean Architecture y potencial escalamiento posterior.
- Diseñar estrategia de ejecución y empaquetado Windows/Android con MSI o APK como restricción futura; NO construir instaladores en esta fase.
- OASIS UBL Invoice 2.1, examinar el XSD adjunto y sus importaciones.
- Nubefact se usa **solo como referencia para descubrimiento de casos de uso**. No integrar ni copiar su API.

## Casos de uso CANDIDATOS (sujetos a priorización)
- Registrar venta / preparar factura.
- Registrar o emitir factura electrónica, validar datos tributarios, consultar comprobantes y sus estados.
- Mantener datos esenciales de clientes y productos.
- Migrar y consultar trazabilidad histórica.
- Anulación/corrección: solo como caso complementario si la justificación normativa y alcance lo permiten.

## Dominio CANDIDATO (no es un modelo definitivo)
Emisor; Cliente; Producto; Factura; DetalleFactura; ImpuestoDetalle; MovimientoAlmacen; LoteMigracion; RegistroMigracion. Identificar cardinalidades/identificadores, snapshots de datos del documento y excepciones de migración. El número de documento interno heredado **no se transforma automáticamente en una factura tributaria**.

## DTOs CANDIDATOS
FacturaCrear, DetalleFactura, FacturaRespuesta, ResultadoValidacion, MigracionSolicitud y MigracionResultado. Definir el contrato definitivo en función de los casos de uso, no copiar respuestas Nubefact.

## UBL Invoice 2.1 — elementos principales observados en el XSD
El archivo `referencias/UBL-Invoice-2.1.xml` contiene un esquema `<xsd:schema>` aunque su extensión sea XML. En `InvoiceType`:
- `cbc:ID`: 1..1.
- `cbc:IssueDate`: 1..1.
- `cac:AccountingSupplierParty`: 1..1.
- `cac:AccountingCustomerParty`: 1..1.
- `cac:LegalMonetaryTotal`: 1..1.
- `cac:InvoiceLine`: 1..n.
- `cbc:InvoiceTypeCode`, `cbc:DocumentCurrencyCode`, `cac:TaxTotal`: opcionales **según XSD base**; las reglas SUNAT pueden exigirlos.
Los componentes `cac`, `cbc` y `ext` se definen en esquemas comunes importados, que deben consultarse antes de afirmar sus campos internos. NO interpretar XSD como un XML de factura válida.

## Arquitectura CANDIDATA
Monolito MVC con servicios de negocio y puntos de desacoplamiento para repositorio, serialización UBL, firma y envío SUNAT/OSE. No programar aplicación ni microservicios: solo diagramas/decisiones.

## Límites y criterios de rigor
- La foto del examen es la fuente prioritaria; todo lo anterior se ajusta a ella.
- Las normas deben verificarse por fuente, artículo y versión aplicable. Distinguir exigencias SUNAT de estructura XSD OASIS.
- Marcar `PENDIENTE DE VERIFICACIÓN` los campos/catálogos que no se puedan confirmar.
- Aclarar el mapeo de referencias oficiales y que Catálogo 08 no equivale al Anexo 8.
- Las capturas de Nubefact mostraron emisión, consulta/listado de comprobantes, productos y menú administrativo. Los listados vacíos en DEMO no prueban errores.
