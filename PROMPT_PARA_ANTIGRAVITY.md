# Instrucción para Google Antigravity — Primera fase Spec-First

Act as a senior software architect, requirements analyst and specialist in OASIS UBL 2.1 and Peruvian electronic invoicing. READ `referencias/caso-estudio-examen.png` first as the authoritative statement of scope and requested deliverables, then READ `CONTEXTO_ANALISIS_PREVIO.md` as **non-authoritative preliminary notes**. Read the supplied OASIS XSD, SUNAT PDF and Nubefact JSON guide. Write ALL deliverables in Spanish.

IMPORTANT CLARIFICATION: The professor requests MULTIPLE SPECIFICATION FILES, NOT JSON interchange files or a functioning API. Use YAML for the API contract, Markdown for written specifications, and PlantUML for diagrams. You MAY describe request/response schemas within OpenAPI YAML, but DO NOT generate independent JSON example files, send JSON payloads, or execute HTTP requests.

Your task is to PRODUCE ONLY FOUR FIRST-PHASE SPEC-FIRST DELIVERABLES inside `specs/`:

1. **Modelo de dominio y DTOs/Schemas:** entities, attributes, associations/cardinalities, contracts and validation; include mapping from five legacy fields and traceability of migration. Model UBL document representations separately from internal domain objects.
2. **Diagramas MVC con visión hexagonal:** an initial modular monolith MVC and an explicitly mapped future evolution to ports/adapters. Generate renderable `.puml` diagrams and explanation. Address Windows/Android and MSI/APK as deployment constraints/architecture choices, WITHOUT claiming the packages exist.
3. **Contratos de endpoints/servicios:** a VALID `specs/contracts/openapi.yaml` with coherent operations, DTOs, request/response, validation and HTTP statuses for essential invoice and migration workflows. This is ABC's own API, NOT Nubefact's interface.
4. **Matriz de trazabilidad SUNAT–UBL:** field/rule -> relevant UBL element -> verified OASIS XSD cardinality -> exact SUNAT norm/catalog/article -> source -> verification status. Pay particular attention to Catalog 08 and the referenced resolutions. Do not confuse XSD optionality with SUNAT optionality.

Put concise supporting requirements, discovered use cases and citations in the specs as needed, preferably files `01-requisitos-y-casos-de-uso.md`, `02-modelo-dominio-y-dtos.md`, `03-arquitectura.md`, diagrams under `diagramas/`, `contracts/openapi.yaml`, and `04-matriz-sunat-ubl.md`. Add a brief README.

Mandatory safeguards: The supplied `UBL-Invoice-2.1.xml` is actually XSD markup. Its `xsd:import` references common OASIS schemas not present locally; research official sources where possible and label unresolved dependencies. Nubefact documents are CONTEXT ONLY — do not connect to Nubefact. Do not copy its API or build its feature set. Distinguish source facts from assumptions and proposals; cite exact legal support or mark `PENDIENTE DE VERIFICACIÓN`. Do not infer SUNAT legal compliance merely from the UBL XSD.

DO NOT generate standalone `.json` files, Postman collections, executed API exchanges, application code, FastAPI endpoints, frontend, databases, tests of business implementation, live SUNAT integration, MSI or APK. Only specs and diagrams. Do not request API tokens or personal credentials.

Verify the four requested deliverables are present, their names are consistent, the OpenAPI YAML parses and diagrams are syntactically renderable when tooling exists. End with a concise Spanish status report, including verification limitations. Work directly in files and avoid unnecessary token use.
