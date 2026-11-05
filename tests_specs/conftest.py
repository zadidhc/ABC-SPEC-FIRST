"""
Configuración compartida de pytest para la suite de pruebas ABC-SPEC-FIRST.

Fixtures globales: emisor y cliente canónicos, comprobante base, servicio completo.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementacion"))

from dataclasses import replace
from datetime import date, time
from decimal import Decimal

import pytest

from abc_cpe.dominio.catalogos import (
    AfectacionIgv,
    Moneda,
    SistemaIsc,
    TipoComprobante,
    TipoDocumentoIdentidad,
    UnidadMedida,
)
from abc_cpe.dominio.modelos import Cliente, Comprobante, Emisor, LineaDetalle
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter
from abc_cpe.infraestructura.validador_xsd import ValidadorXsdLxml
from abc_cpe.aplicacion.servicio import GenerarXmlComprobanteService

XSD_PATH = str(ROOT / "implementacion" / "xsd" / "maindoc" / "UBL-Invoice-2.1.xsd")


# ---------------------------------------------------------------------------
# Fixtures básicas reutilizables
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def emisor_valido():
    return Emisor(
        ruc="20123456786",
        razon_social="ABC Software Corp",
        nombre_comercial="ABC Corp",
        ubigeo="150101",
        direccion="Av. República de Panamá 3030",
        departamento="LIMA",
        provincia="LIMA",
        distrito="MIRAFLORES",
    )


@pytest.fixture(scope="session")
def cliente_ruc_valido():
    return Cliente(
        tipo_documento=TipoDocumentoIdentidad.RUC,
        numero_documento="20601234565",
        razon_social="Distribuidora Los Andes S.A.C.",
    )


@pytest.fixture(scope="session")
def cliente_dni_valido():
    return Cliente(
        tipo_documento=TipoDocumentoIdentidad.DNI,
        numero_documento="45678901",
        razon_social="Juan Carlos Pérez López",
    )


@pytest.fixture(scope="session")
def linea_gravada_basica():
    return LineaDetalle(
        numero_orden=1,
        cantidad=Decimal("2"),
        unidad_medida=UnidadMedida.NIU,
        descripcion="Producto de prueba gravado",
        valor_unitario=Decimal("100.00"),
        afectacion_igv=AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
    )


@pytest.fixture
def factura_basica(emisor_valido, cliente_ruc_valido, linea_gravada_basica):
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie="F001",
        correlativo=1,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=emisor_valido,
        cliente=cliente_ruc_valido,
        lineas=[linea_gravada_basica],
    )


@pytest.fixture(scope="session")
def generador():
    return GeneradorUblAdapter()


@pytest.fixture(scope="session")
def validador():
    return ValidadorXsdLxml()


@pytest.fixture(scope="session")
def servicio():
    return GenerarXmlComprobanteService(
        GeneradorUblAdapter(),
        ValidadorXsdLxml(),
    )


@pytest.fixture(scope="session")
def xsd_path():
    return XSD_PATH

