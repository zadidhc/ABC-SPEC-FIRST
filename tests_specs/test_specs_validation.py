import os
import re
import yaml
import pytest
from jsonschema import validate, ValidationError, Draft202012Validator
from openapi_spec_validator import validate as validate_openapi
from openapi_spec_validator.readers import read_from_filename

OPENAPI_PATH = "specs/05-endpoints-openapi.yaml"
DTOS_PATH = "specs/03-dtos-schemas.yaml"

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="module")
def openapi_spec():
    return load_yaml(OPENAPI_PATH)

@pytest.fixture(scope="module")
def dtos_spec():
    return load_yaml(DTOS_PATH)

# ==========================================================
# 1. VALIDACIÓN ESTRUCTURAL Y LINT DE OPENAPI 3.1
# ==========================================================
def test_openapi_version_is_3_1(openapi_spec):
    assert openapi_spec.get("openapi") == "3.1.0"

def test_openapi_spec_validity():
    spec_dict, _ = read_from_filename(OPENAPI_PATH)
    validate_openapi(spec_dict)

def test_no_nullable_true_in_openapi():
    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "nullable: true" not in content, "Se encontraron ocurrencias de 'nullable: true'. Debe usarse OpenAPI 3.1 type: [string, 'null']."

def test_no_nullable_true_in_dtos():
    with open(DTOS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "nullable: true" not in content, "Se encontraron ocurrencias de 'nullable: true' en 03-dtos-schemas.yaml."

# ==========================================================
# 2. AUDITORÍA DE SEGURIDAD Y OPERACIONES
# ==========================================================
def test_security_schemes_bearer_auth(openapi_spec):
    schemes = openapi_spec.get("components", {}).get("securitySchemes", {})
    assert "bearerAuth" in schemes, "Falta securitySchemes.bearerAuth"
    assert schemes["bearerAuth"]["type"] == "http"
    assert schemes["bearerAuth"]["scheme"] == "bearer"
    assert schemes["bearerAuth"]["bearerFormat"] == "JWT"

def test_root_security_declaration(openapi_spec):
    sec = openapi_spec.get("security", [])
    assert any("bearerAuth" in s for s in sec), "Debe declararse bearerAuth a nivel global en security"

def test_every_operation_has_unique_operation_id_and_security_responses(openapi_spec):
    operation_ids = set()
    paths = openapi_spec.get("paths", {})
    
    for path, methods in paths.items():
        for method, op in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue
            op_id = op.get("operationId")
            assert op_id is not None, f"Operación sin operationId en {method.upper()} {path}"
            assert op_id not in operation_ids, f"operationId duplicado '{op_id}' en {method.upper()} {path}"
            operation_ids.add(op_id)
            
            # Verificar 401 y 403
            responses = op.get("responses", {})
            assert "401" in responses, f"Falta respuesta 401 en {op_id} ({method.upper()} {path})"
            assert "403" in responses, f"Falta respuesta 403 en {op_id} ({method.upper()} {path})"

def test_issuance_and_migration_status_codes(openapi_spec):
    paths = openapi_spec.get("paths", {})
    
    # Emisión de facturas
    issue_op = paths.get("/invoices/{id}/issue", {}).get("post", {})
    issue_responses = issue_op.get("responses", {})
    assert "200" in issue_responses
    assert "202" in issue_responses
    assert "409" in issue_responses
    assert "502" in issue_responses
    assert "503" in issue_responses
    
    # Migración
    migration_op = paths.get("/migration/batches", {}).get("post", {})
    migration_responses = migration_op.get("responses", {})
    assert "202" in migration_responses, "POST /migration/batches debe retornar HTTP 202"

# ==========================================================
# 3. CONSISTENCIA DE ESQUEMAS DTO VS OPENAPI
# ==========================================================
def test_dtos_schema_parity(openapi_spec, dtos_spec):
    dtos_schemas = dtos_spec.get("components", {}).get("schemas", {})
    openapi_schemas = openapi_spec.get("components", {}).get("schemas", {})
    
    for schema_name in dtos_schemas.keys():
        assert schema_name in openapi_schemas, f"El esquema {schema_name} de 03-dtos-schemas.yaml no está en openapi.yaml"

# ==========================================================
# 4. PRUEBAS DE CONTRATO POSITIVAS (JSON SCHEMA VALIDATION)
# ==========================================================
def test_positive_contract_create_invoice(openapi_spec):
    schema = openapi_spec["components"]["schemas"]["CreateInvoiceRequest"]
    # Resolver refs locales integrando el documento completo
    resolver_spec = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **schema,
        "components": openapi_spec["components"]
    }
    
    valid_invoice = {
        "invoice_type_code": "01",
        "series": "F001",
        "issue_date": "2026-10-22",
        "due_date": "2026-11-22",
        "currency": "PEN",
        "operation_type": "0101",
        "payment_terms": {
            "payment_means_id": "Contado"
        },
        "customer": {
            "identity_document_type": "6",
            "identity_document_number": "20481234567",
            "legal_name": "DISTRIBUIDORA SAN MARTIN S.A.C.",
            "address": "Jr. Progreso 124",
            "email": "contacto@distribuidorasanmartin.pe"
        },
        "lines": [
            {
                "sku": "ARR-COST-50K",
                "description": "Saco de Arroz Costeño Extra 50 Kg",
                "quantity": "10.0000",
                "unit_code": "BX",
                "unit_value": "150.0000",
                "tax_exemption_reason_code": "10",
                "igv_rate": "18.00"
            }
        ]
    }
    
    validator = Draft202012Validator(resolver_spec)
    errors = list(validator.iter_errors(valid_invoice))
    assert len(errors) == 0, f"Error validando factura válida: {errors}"

def test_positive_contract_create_note(openapi_spec):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **openapi_spec["components"]["schemas"]["CreateNoteRequest"],
        "components": openapi_spec["components"]
    }
    
    valid_note = {
        "note_type_code": "07",
        "series": "FC01",
        "issue_date": "2026-10-25",
        "currency": "PEN",
        "referenced_document_type": "01",
        "referenced_document_series_number": "F001-00001042",
        "discrepancy_code": "01",
        "discrepancy_description": "Anulación total de la operación",
        "customer": {
            "identity_document_type": "6",
            "identity_document_number": "20481234567",
            "legal_name": "DISTRIBUIDORA SAN MARTIN S.A.C."
        },
        "lines": [
            {
                "description": "Devolución de mercadería",
                "quantity": "1.0000",
                "unit_code": "NIU",
                "unit_value": "100.0000",
                "tax_exemption_reason_code": "10"
            }
        ]
    }
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(valid_note))
    assert len(errors) == 0

# ==========================================================
# 5. PRUEBAS DE CONTRATO NEGATIVAS (DEBEN SER RECHAZADAS)
# ==========================================================
def test_negative_contract_missing_required_fields(openapi_spec):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **openapi_spec["components"]["schemas"]["CreateInvoiceRequest"],
        "components": openapi_spec["components"]
    }
    validator = Draft202012Validator(schema)
    
    # Falta 'lines' y 'customer'
    invalid_invoice = {
        "invoice_type_code": "01",
        "series": "F001",
        "issue_date": "2026-10-22",
        "currency": "PEN"
    }
    assert not validator.is_valid(invalid_invoice)

def test_negative_contract_empty_lines_rejected(openapi_spec):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **openapi_spec["components"]["schemas"]["CreateInvoiceRequest"],
        "components": openapi_spec["components"]
    }
    validator = Draft202012Validator(schema)
    
    invoice_empty_lines = {
        "invoice_type_code": "01",
        "series": "F001",
        "issue_date": "2026-10-22",
        "currency": "PEN",
        "customer": {
            "identity_document_type": "6",
            "identity_document_number": "20481234567",
            "legal_name": "CLIENTE PRUEBA"
        },
        "lines": [] # minItems: 1
    }
    assert not validator.is_valid(invoice_empty_lines)

def test_negative_contract_invalid_unit_code(openapi_spec):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **openapi_spec["components"]["schemas"]["CreateInvoiceLineDTO"],
        "components": openapi_spec["components"]
    }
    validator = Draft202012Validator(schema)
    
    line_bad_unit = {
        "description": "Producto",
        "quantity": "5.0000",
        "unit_code": "INVALID_UNIT", # No en catálogo 03
        "unit_value": "20.0000",
        "tax_exemption_reason_code": "10"
    }
    assert not validator.is_valid(line_bad_unit)

def test_negative_contract_invalid_amount_decimal_format(openapi_spec):
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **openapi_spec["components"]["schemas"]["DecimalAmountString"]
    }
    validator = Draft202012Validator(schema)
    
    assert not validator.is_valid("118") # Sin 2 decimales
    assert not validator.is_valid("118.5") # Solo 1 decimal
    assert not validator.is_valid(118.00) # Es un número, no string
    assert not validator.is_valid("abc") # Letras
    assert validator.is_valid("118.00") # Correcto

def test_cross_validation_rules_factura_and_boleta():
    # Validación de reglas cruzadas de negocio que complementan a JSON Schema
    def validar_regla_cruzada(tipo_doc, serie, tipo_doc_identidad, num_doc):
        errores = []
        if tipo_doc == "01":
            if not serie.startswith("F"):
                errores.append("Factura debe tener serie que inicie con F")
            if tipo_doc_identidad != "6" or len(num_doc) != 11:
                errores.append("Factura exige cliente con RUC de 11 dígitos")
        elif tipo_doc == "03":
            if not serie.startswith("B"):
                errores.append("Boleta debe tener serie que inicie con B")
            if tipo_doc_identidad not in ["0", "1", "4", "6", "7"]:
                errores.append("Tipo de documento de identidad no admitido en Boleta")
        return errores

    # Caso inválido 1: Factura con serie B
    errs = validar_regla_cruzada("01", "B001", "6", "20481234567")
    assert "Factura debe tener serie que inicie con F" in errs

    # Caso inválido 2: Factura con cliente DNI
    errs = validar_regla_cruzada("01", "F001", "1", "45678901")
    assert "Factura exige cliente con RUC de 11 dígitos" in errs

    # Caso inválido 3: Boleta con serie F
    errs = validar_regla_cruzada("03", "F001", "1", "45678901")
    assert "Boleta debe tener serie que inicie con B" in errs

    # Caso válido: Factura F001 con RUC
    errs = validar_regla_cruzada("01", "F001", "6", "20481234567")
    assert len(errs) == 0

    # Caso válido: Boleta B001 con DNI
    errs = validar_regla_cruzada("03", "B001", "1", "45678901")
    assert len(errs) == 0

