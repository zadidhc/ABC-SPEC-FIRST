# ABC-SPEC-FIRST

### Arquitectura de software y generación de comprobantes XML UBL 2.1

**Proyecto académico · Universidad Nacional Agraria de la Selva (UNAS) · FIIS · Arquitectura de Software**

**Fase 1:** especificación *Spec-First* de requisitos, dominio, arquitectura y contratos.  
**Fase 2:** implementación en **Python** de la generación de XML `Invoice` a partir de **OASIS UBL 2.1**, con validación XSD y pruebas automatizadas.

[![Python](https://img.shields.io/badge/Implementaci%C3%B3n-Python-3776AB)](#implementación-de-la-fase-2) [![UBL](https://img.shields.io/badge/OASIS%20UBL-2.1-005B9A)](https://docs.oasis-open.org/ubl/os-UBL-2.1/) [![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-6BA539)](specs/05-endpoints-openapi.yaml) [![Pruebas](https://img.shields.io/badge/Pruebas%20locales-225%20aprobadas-brightgreen)](#pruebas-automatizadas)

> **Estado del segundo parcial (05/11/2026):** generación y validación de XML UBL 2.1 implementadas. La última ejecución local de la suite publicada registró **225 pruebas aprobadas**, de las cuales **49** corresponden a generación XML e integración XSD.

## Índice

1. [Objetivo y contexto](#objetivo-y-contexto)
2. [Implementación de la Fase 2](#implementación-de-la-fase-2)
3. [Estructura del repositorio](#estructura-del-repositorio)
4. [Instalación](#instalación)
5. [Pruebas automatizadas](#pruebas-automatizadas)
6. [Fase 1: especificaciones](#fase-1-especificaciones)
7. [Alcance y limitaciones](#alcance-y-limitaciones)
8. [Documentación y referencias](#documentación-y-referencias)

## Objetivo y contexto

ABC Software Corp es una empresa comercializadora de abarrotes y mercadería. Su sistema anterior de almacén registraba operaciones mediante cinco campos: `fecha`, `ingreso`, `salida`, `producto` y `nro_documento`, sin una estructura de facturación electrónica.

El proyecto aborda la especificación de una solución de facturación electrónica y migración de datos legados. En el **segundo parcial**, el objetivo concreto fue **implementar la generación de documentos XML desde el esquema `UBL-Invoice-2.1.xsd`, en el lenguaje elegido para el dominio, y comprobarla mediante pruebas unitarias**.

La implementación utiliza Python, modelos propios del dominio y clases generadas a partir de los esquemas XSD. **No es solo una especificación teórica**: existe código ejecutable y una suite automatizada de comprobación.

## Implementación de la Fase 2

### Arquitectura y componentes

| Capa | Responsabilidad | Archivo principal |
|---|---|---|
| **Dominio** | Representar emisores, clientes, comprobantes, líneas y catálogos; aplicar validaciones y cálculos. | [`implementacion/abc_cpe/dominio/`](implementacion/abc_cpe/dominio/) |
| **Aplicación** | Orquestar la validación, el cálculo, la generación y la comprobación del XML. | [`servicio.py`](implementacion/abc_cpe/aplicacion/servicio.py) |
| **Puertos** | Desacoplar el caso de uso de sus adaptadores de infraestructura. | [`puertos.py`](implementacion/abc_cpe/aplicacion/puertos.py) |
| **Generación UBL** | Construir y serializar los objetos XML usando las clases derivadas del XSD. | [`generador_ubl.py`](implementacion/abc_cpe/infraestructura/generador_ubl.py) |
| **Validación XSD** | Validar el XML contra `UBL-Invoice-2.1.xsd`. | [`validador_xsd.py`](implementacion/abc_cpe/infraestructura/validador_xsd.py) |
| **Modelos del XSD** | Contener clases Python generadas con `xsdata`. | [`ubl_generado/`](implementacion/abc_cpe/ubl_generado/) |

### Flujo funcional

```text
Datos de factura o boleta
          |
          v
Modelos del dominio (Comprobante, Emisor, Cliente, LineaDetalle)
          |
          v
Validaciones de negocio y cálculo de importes
          |
          v
Generador UBL 2.1 (clases Python derivadas del XSD)
          |
          v
Serialización a XML
          |
          v
Validación con lxml contra UBL-Invoice-2.1.xsd
          |
          v
Resultado: nombre de archivo, bytes XML y totales calculados
```

El caso de uso central es `GenerarXmlComprobanteService`. La generación produce un documento XML en memoria; las pruebas verifican sus elementos, importes y conformidad estructural. **No se requiere un servidor web ni una base de datos para ejecutar estas pruebas.**

### Esquemas XSD incluidos

Se incluyen los XSD OASIS UBL 2.1 utilizados por la implementación:

| Carpeta | Contenido |
|---|---|
| [`implementacion/xsd/maindoc/`](implementacion/xsd/maindoc/) | `UBL-Invoice-2.1.xsd`, `UBL-CreditNote-2.1.xsd` y `UBL-DebitNote-2.1.xsd` (**3 archivos**) |
| [`implementacion/xsd/common/`](implementacion/xsd/common/) | Componentes básicos, agregados, extensiones, firma y tipos compartidos (**14 archivos**) |

**Importante:** disponer de esquemas de notas de crédito y débito no implica que esta Fase 2 implemente su emisión. El alcance probado se centra en el documento **`Invoice`**, usado para facturas y boletas.

## Estructura del repositorio

```text
ABC-SPEC-FIRST/
├── .github/
│   └── workflows/
│       └── validate-specs.yml       # Validación automatizada configurada
├── docs/                         # Documentación complementaria
├── implementacion/               # CÓDIGO EJECUTABLE DE LA FASE 2
│   ├── abc_cpe/
│   │   ├── dominio/
│   │   │   ├── modelos.py
│   │   │   ├── catalogos.py
│   │   │   ├── validaciones.py
│   │   │   ├── calculo.py
│   │   │   ├── monto_en_letras.py
│   │   │   └── errores.py
│   │   ├── aplicacion/
│   │   │   ├── servicio.py
│   │   │   └── puertos.py
│   │   ├── infraestructura/
│   │   │   ├── generador_ubl.py
│   │   │   └── validador_xsd.py
│   │   └── ubl_generado/         # Clases generadas desde XSD con xsdata
│   ├── xsd/
│   │   ├── common/               # 14 XSD compartidos de UBL 2.1
│   │   └── maindoc/              # Invoice, CreditNote y DebitNote (XSD)
│   ├── generar_clases.sh
│   └── requirements.txt
├── references/                    # Material del caso y referencias de Fase 1
├── scripts/                       # Herramientas auxiliares
├── specs/                         # ESPECIFICACIONES DE LA FASE 1
│   ├── 01-requisitos-casos-uso.md
│   ├── 02-modelo-dominio.md
│   ├── 03-dtos-schemas.yaml
│   ├── 04-arquitectura.md
│   ├── 05-endpoints-openapi.yaml
│   ├── 06-matriz-sunat-ubl.md
│   └── diagramas/                # Diagramas de arquitectura
├── tests_specs/                   # PRUEBAS AUTOMATIZADAS
│   ├── conftest.py
│   ├── test_generacion_xml.py
│   ├── test_xsd_integration.py
│   ├── test_domain_validation.py
│   ├── test_financial_correctness.py
│   ├── test_adversarial.py
│   └── test_specs_validation.py
├── xsd/                          # Recursos adicionales del repositorio
├── INFORME_TECNICO_FINAL.md       # Informe de arquitectura y avances
├── README.md                      # Este documento
├── requirements.txt               # Dependencias Python
├── package.json                   # Scripts de validación de OpenAPI
└── pyrefly.toml                   # Configuración del analizador Python
```

> La estructura muestra los componentes principales; se omiten paquetes `__init__.py`, archivos generados internos y otros recursos para facilitar la lectura. La carpeta `tests_specs/scratch_check.py`, si aparece en tu equipo, es un archivo temporal local y no forma parte de la entrega publicada.

## Instalación

### Requisitos

- **Python 3.11 o posterior** (las pruebas locales se ejecutaron con Python 3.13).
- **PowerShell** para seguir los ejemplos de Windows.
- **Node.js y npm**, solo si se desea ejecutar también el comando completo de validación de OpenAPI.

Abre PowerShell en la **raíz del repositorio** (`ABC-SPEC-FIRST`):

```powershell
# 1. Crear el entorno virtual
py -m venv .venv

# 2. Instalar dependencias Python
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Hacer accesible el paquete abc_cpe
$env:PYTHONPATH = (Resolve-Path .\implementacion).Path
```

Estos comandos se ejecutan desde la carpeta que contiene `README.md` y `requirements.txt`.

## Pruebas automatizadas

### Pruebas del segundo parcial: generación XML y validación XSD

```powershell
.\.venv\Scripts\python.exe -m pytest -v tests_specs/test_generacion_xml.py tests_specs/test_xsd_integration.py
```

**Último resultado local registrado: `49 passed`.** Incluye generación de facturas y boletas, estructura XML, categorías tributarias, caracteres especiales, errores y conformidad XSD.

### Suite completa del proyecto

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests_specs
```

**Último resultado local registrado en la versión principal: `225 passed`.** Incluye validaciones de dominio, corrección financiera, pruebas adversariales, contrato OpenAPI y generación XML.

### Validación de OpenAPI 3.1 con npm (opcional)

```powershell
npm ci
$env:PYTHONPATH = (Resolve-Path .\implementacion).Path
$env:Path = "$((Resolve-Path .\.venv\Scripts).Path);$env:Path"
npm run validate:specs
```

Este comando ejecuta el análisis y empaquetado de OpenAPI con Redocly y lanza las pruebas del proyecto. La validación se comprobó localmente; el resultado de GitHub Actions debe consultarse por separado en la pestaña **Actions** del repositorio.

## Fase 1: especificaciones

La Fase 1 definió la propuesta de arquitectura y los contratos antes de la implementación. Se conservan como trazabilidad del diseño:

| Documento | Contenido |
|---|---|
| [`01-requisitos-casos-uso.md`](specs/01-requisitos-casos-uso.md) | Requisitos funcionales y no funcionales, reglas y casos de uso. |
| [`02-modelo-dominio.md`](specs/02-modelo-dominio.md) | Modelo del dominio, entidades y migración de datos legados. |
| [`03-dtos-schemas.yaml`](specs/03-dtos-schemas.yaml) | DTO y restricciones de esquemas reutilizables. |
| [`04-arquitectura.md`](specs/04-arquitectura.md) | Arquitectura modular MVC y evolución hacia puertos y adaptadores. |
| [`05-endpoints-openapi.yaml`](specs/05-endpoints-openapi.yaml) | Contrato REST formal OpenAPI 3.1. |
| [`06-matriz-sunat-ubl.md`](specs/06-matriz-sunat-ubl.md) | Trazabilidad entre requisitos, campos UBL y referencias normativas. |

La migración de almacén, la API REST y la firma/envío tributario se encuentran especificadas para fases posteriores, pero no deben confundirse con funcionalidades ya desplegadas.

## Alcance y limitaciones

| **Comprobado en esta implementación** | **No incluido en el alcance publicado de Fase 2** |
|---|---|
| Modelos y validaciones de datos del comprobante | Integración operativa con SUNAT u OSE |
| Cálculo y serialización de facturas/boletas XML UBL 2.1 | Recepción de CDR y autorización tributaria |
| Validación estructural contra el esquema XSD | Firma electrónica tributaria XAdES-BES con certificado autorizado |
| Pruebas automatizadas y rechazo de XML incorrectos | Emisión completa de notas, ICBPER y pagos a crédito |

**Aclaración:** que un XML pase el XSD de OASIS **no significa** que SUNAT lo haya aceptado. Algunas reglas tributarias adicionales —incluido el ISC al precio de venta al público— requieren verificación normativa antes de utilizar el generador en producción.

Si se incorporan posteriormente ejemplos de firma **XMLDSig con certificado de prueba**, deben documentarse como demostración académica separada, no como firma fiscal oficial.

## Documentación y referencias

- [Informe técnico del proyecto](INFORME_TECNICO_FINAL.md).
- [Documentación complementaria](docs/).
- [Estándar OASIS UBL 2.1](https://docs.oasis-open.org/ubl/os-UBL-2.1/).
- [Contrato OpenAPI](specs/05-endpoints-openapi.yaml).

---

**Uso académico — Arquitectura de Software, UNAS.** La documentación y el código de este repositorio representan un trabajo de aprendizaje y validación técnica, no un sistema de emisión tributaria autorizado para producción.
