# SPEC — Requisitos del Sistema y Casos de Uso (ABC Software Corp)

**Versión:** 1.0.0  
**Fecha:** 22 de octubre de 2026  
**Fase:** Fase 1 — Especificación Técnica Spec-First  
**Autor:** Senior Software Architect  
**Estado:** BORRADOR — PENDIENTE DE REVISIÓN

---

## 1. Introducción y Propósito

El presente documento define los requisitos funcionales, requisitos no funcionales, reglas de negocio y casos de uso formalizados para la transformación del software básico de almacén de **ABC Software Corp** en un sistema robusto de facturación electrónica compatible con el estándar internacional **OASIS UBL 2.1** y las normativas de la **Superintendencia Nacional de Aduanas y de Administración Tributaria (SUNAT)** de Perú.

Este documento sirve como base técnica autoritativa para el modelo de dominio, contratos de API (OpenAPI 3.1), matriz de trazabilidad y arquitectura de software sin requerir implementación de código ejecutable en esta fase.

---

## 2. Requisitos Funcionales (RF)

| ID | Requisito Funcional | Descripción | Casos de Uso Asociados |
| :--- | :--- | :--- | :--- |
| **RF-01** | Emisión de Factura Electrónica | Permitir el registro y estructuración de comprobantes de pago tipo Factura (código '01') conforme al estándar UBL 2.1 e instrucciones de SUNAT. | CU-01, CU-02 |
| **RF-02** | Validación Tributaria Previa | Validar de forma síncrona el RUC emisor/receptor, formato de serie/correlativo, coherencia de afectación al IGV, tasas y cálculos aritméticos antes de persistir o emitir. | CU-01, CU-02 |
| **RF-03** | Generación de XML UBL 2.1 | Construir la estructura XML bajo el namespace OASIS UBL Invoice 2.1 y la extensión `ext:UBLExtensions` requerida para la firma digital. | CU-02 |
| **RF-04** | Firma Digital XAdES-BES | Integrar el componente de firma digital con certificado digital tributario (PKCS#12) generando el resumen `ds:DigestValue` y la firma `ds:SignatureValue`. | CU-02 |
| **RF-05** | Comunicación con OSE / SUNAT | Gestionar el empaquetado ZIP, invocación SOAP a la OSE/SUNAT, recepción del CDR (Constancia de Recepción) y parseo de códigos de respuesta. | CU-02, CU-03 |
| **RF-06** | Consulta y Estado de Comprobantes | Consultar el estado operativo y tributario del comprobante (Borrador, Validado, Firmado, Aceptado por SUNAT, Rechazado, Observado). | CU-03 |
| **RF-07** | Migración de Datos Legados | Ingerir lotes de información histórica del sistema anterior (`fecha`, `ingreso`, `salida`, `producto`, `nro_documento`) asignándolos a movimientos de almacén y referencias comerciales. | CU-04 |
| **RF-08** | Trazabilidad y Bitácora de Migración | Registrar el resultado de migración por fila, indicando estado (Procesado, Error, Advertencia), mensaje de validación y vínculo con la entidad generada. | CU-04, CU-05 |
| **RF-09** | Gestión de Catálogos Tributarios | Proveer acceso a catálogos SUNAT requeridos: Catálogo 01 (Tipo de Documento), Catálogo 02 (Moneda), Catálogo 06 (Tipo Doc. Identidad), Catálogo 07 (Afectación al IGV), Catálogo 08 (Sistema de Cálculo ISC). | CU-01, CU-02 |

---

## 3. Requisitos No Funcionales (RNF)

| ID | Requisito No Funcional | Criterio de Aceptación / Restricción Técnica |
| :--- | :--- | :--- |
| **RNF-01** | Desacoplamiento Arquitectónico | El núcleo de dominio no debe depender de librerías de infraestructura, frameworks web, SOAP de SUNAT ni drivers de base de datos. Se proyecta de MVC a Arquitectura Hexagonal. |
| **RNF-02** | Multiplataforma y Empaquetado | La solución debe ejecutarse en sistemas Windows y dispositivos móviles Android, considerando distribución futura vía instalador Windows (MSI) y paquete Android (APK). |
| **RNF-03** | Idempotencia y Consistencia Transaccional | La generación de comprobantes y la migración de lotes deben soportar claves de idempotencia para prevenir duplicidades tributarias o de inventario. |
| **RNF-04** | Seguridad y Resguardo Criptográfico | Las llaves privadas del certificado digital tributario deben resguardarse en almacén seguro; las contraseñas no se expondrán en texto plano. |
| **RNF-05** | Conformidad con Estándares Abiertos | El esquema de comunicación API debe cumplir formalmente con la especificación OpenAPI 3.1.0 y las estructuras de documentos con OASIS UBL 2.1. |

---

## 4. Reglas de Negocio (RN)

- **RN-01 (Identificación del Receptor):** En comprobantes tipo Factura (código '01'), el adquirente debe identificarse obligatoriamente con RUC de 11 dígitos numéricos válido (Tipo Documento Identidad '6', Catálogo 06 SUNAT) y estado activo/habido.
- **RN-02 (Serie y Correlativo):** La serie para Facturas electrónicas emitidas desde el sistema del contribuyente (SEE-Del Contribuyente / OSE) debe iniciar con la letra 'F' seguida de 3 caracteres alfanuméricos (ej. `F001`). El correlativo es un número entero entre 1 y 99999999, completado con ceros a la izquierda en la representación impresa y formateado como entero en UBL.
- **RN-03 (Afectación al IGV - Catálogo 07):** Toda línea de detalle debe contener un código de tipo de afectación al IGV. Si es Gravada (código '10'), se debe calcular el 18% sobre el valor unitario. Si es Exonerada ('20') o Inafecta ('30'), el impuesto IGV es 0.00 pero debe especificarse la base imponible y el código tributario correspondiente (`VAT` / `9997` / `9998`).
- **RN-04 (Impuesto Selectivo al Consumo - ISC y Catálogo 08):** Cuando aplique ISC a productos gravados (ej. licores, bebidas azucaradas, combustibles comercializados por mayoristas), se debe aplicar uno de los sistemas previstos en el Catálogo 08:
  - Sistema al Valor (al porcentaje).
  - Sistema Específico (monto fijo por unidad física).
  - Sistema al Precio de Venta al Público.
  El ISC forma parte de la base imponible del IGV.
- **RN-05 (Impuesto al Consumo de Bolsas de Plástico - ICBPER):** Si la transacción incluye bolsas plásticas de un solo uso, se liquida el monto unitario fijo vigente por bolsa. El ICBPER no forma parte de la base imponible del IGV ni del ISC y se suma directamente al total a pagar.
- **RN-06 (Totalización Monetaria):**
  $$\text{Importe Total} = \text{Total Valor Venta} - \text{Total Descuentos} + \text{Total IGV} + \text{Total ISC} + \text{Total ICBPER} + \text{Total Otros Cargos}$$
  Los cálculos deben respetar un redondeo monetario a 2 decimales para totales y hasta 10 decimales para valores unitarios.
- **RN-07 (Inmutabilidad de Documentos Emitidos):** Un comprobante que cuente con firma digital y constancia CDR de SUNAT/OSE no puede modificarse ni eliminarse en base de datos. Cualquier ajuste contable debe realizarse mediante Nota de Crédito ('07') o Comunicación de Baja según corresponda.
- **RN-08 (No Equivalencia Automática de Documentos Legados):** Un `nro_documento` registrado en el sistema anterior de almacén es un identificador interno de control operativo; bajo ninguna circunstancia se convierte automáticamente en una Factura electrónica ni sustituye la serie y correlativo formal de SUNAT.

---

## 5. Especificación Formal de Casos de Uso

```mermaid
usecaseDiagram
    actor "Operador Comercial" as Operador
    actor "Administrador / Auditor" as Admin
    actor "Servicio OSE / SUNAT" as SUNAT

    package "Sistema de Facturación ABC" {
        usecase "CU-01: Registrar y Validar Factura" as CU01
        usecase "CU-02: Emitir Factura Electrónica (UBL/Firma/Envío)" as CU02
        usecase "CU-03: Consultar Comprobante y Estado CDR" as CU03
        usecase "CU-04: Iniciar Migración de Datos Legados" as CU04
        usecase "CU-05: Inspeccionar Trazabilidad de Migración" as CU05
    }

    Operador --> CU01
    Operador --> CU02
    Operador --> CU03
    Admin --> CU04
    Admin --> CU05
    CU02 ..> SUNAT : Envío SOAP / CDR
```

### CU-01: Registrar y Validar Factura (Borrador)
- **Actor Principal:** Operador Comercial / Facturador.
- **Precondiciones:** El cliente debe estar registrado con RUC válido en el sistema o proporcionarse en la solicitud; los productos deben contar con precio base, unidad de medida y régimen de afectación.
- **Flujo Principal:**
  1. El operador ingresa los datos de cabecera (cliente, moneda, fecha de emisión, fecha de vencimiento opcional).
  2. El operador añade ítems de detalle (producto, cantidad, valor unitario, afectación IGV, ISC/ICBPER si aplica).
  3. El sistema valida reglas de negocio RN-01, RN-02, RN-03, RN-04, RN-05 y RN-06.
  4. El sistema almacena la factura con estado `BORRADOR` y retorna el identificador interno, los totales calculados y el reporte de validación conforme.
- **Flujos Alternativos / Excepciones:**
  - *3a. RUC inválido o longitud distinta de 11 dígitos:* El sistema rechaza el registro con código de error `VAL-001` y lista los campos infractores.
  - *3b. Discrepancia aritmética en sumatorias:* El sistema retorna error `VAL-002` indicando diferencia entre suma de ítems y totales declarados.

### CU-02: Solicitar Emisión Electrónica
- **Actor Principal:** Operador Comercial / Proceso Desatendido.
- **Precondiciones:** La factura debe existir en estado `BORRADOR` o `VALIDADO`.
- **Flujo Principal:**
  1. El operador solicita la emisión electrónica indicando el ID de la factura.
  2. El sistema reserva el número correlativo oficial según la serie configurada (ej. `F001-00000124`).
  3. El sistema construye el árbol XML cumpliendo la gramática OASIS UBL Invoice 2.1.
  4. El servicio criptográfico firma el XML usando el certificado digital de ABC Software Corp, obteniendo el `ds:DigestValue` (código hash) y `ds:SignatureValue`.
  5. El sistema empaqueta el XML firmado en formato ZIP (`{RUC}-01-{SERIE}-{NUMERO}.zip`).
  6. El sistema envía el ZIP al webservice de la OSE o SUNAT mediante protocolo SOAP.
  7. El sistema recibe la respuesta con el CDR (Constancia de Recepción), extrae el código de respuesta (código `0` = Aceptado) y almacena el XML firmado y CDR.
  8. El estado del comprobante pasa a `EMITIDO_ACEPTADO`.
- **Flujos Alternativos / Excepciones:**
  - *6a. Falla de conexión con OSE/SUNAT:* La factura queda en estado `FIRMADO_PENDIENTE_ENVIO`. Se programa reintento y se notifica al usuario que el documento tiene valor temporal contingente según normativa.
  - *7a. Rechazo por parte de OSE/SUNAT:* Si el CDR retorna código de error (ej. error 2014, 2118), el comprobante pasa a `RECHAZADO`, registrando la observación técnica de SUNAT sin reusar el correlativo.

### CU-03: Consultar Comprobante y Estado Tributario
- **Actor Principal:** Operador Comercial / Cliente / Auditor.
- **Precondiciones:** Identificador único o serie-correlativo del comprobante.
- **Flujo Principal:**
  1. El usuario solicita el estado y detalle del comprobante.
  2. El sistema recupera los datos de dominio, el estado del ciclo de vida, el resumen hash (`ds:DigestValue`), el estado de aceptación en SUNAT y los enlaces de descarga (XML firmado, CDR, PDF).
  3. El usuario visualiza la información consolidada.

### CU-04: Iniciar Migración de Datos Legados de Almacén
- **Actor Principal:** Administrador de TI / Encargado de Almacén.
- **Precondiciones:** Archivo o carga de datos estructurada con las columnas históricas: `fecha`, `ingreso`, `salida`, `producto`, `nro_documento`.
- **Flujo Principal:**
  1. El administrador envía un lote de registros legados indicando una descripción y fuente de origen.
  2. El sistema genera un `LoteMigracion` en estado `EN_PROCESO`.
  3. Para cada fila del lote:
     a. Valida el formato de fecha ISO 8601.
     b. Normaliza cantidades: `ingreso` (entrada a inventario) y `salida` (egreso de inventario).
     c. Homologa el identificador o descripción de `producto` con el catálogo maestro de productos.
     d. Registra `nro_documento` como `referencia_documento_origen` de tipo documento interno (código '00' o interno).
     e. Genera un movimiento de almacén histórico vinculado.
     f. Registra un registro de trazabilidad con estado `EXITOSO`.
  4. Al finalizar la totalidad de filas, calcula totales de procesados, advertencias y fallidos, y marca el lote como `FINALIZADO`.
- **Flujos Alternativos / Excepciones:**
  - *3a. Fila con datos corruptos o valores negativos simultáneos:* La fila se registra con estado `FALLIDO`, se almacena el mensaje de error y el lote continúa procesando las demás filas.

### CU-05: Inspeccionar Trazabilidad de Migración
- **Actor Principal:** Administrador de TI / Auditor.
- **Precondiciones:** Identificador del lote de migración o referencia de documento legado.
- **Flujo Principal:**
  1. El usuario consulta el avance de un lote específico o busca el destino de un `nro_documento` antiguo.
  2. El sistema devuelve el estado consolidado del lote, la tasa de éxito y el listado detallado de filas con sus errores o entidades creadas.
