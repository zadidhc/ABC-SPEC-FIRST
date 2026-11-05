import sys
from dataclasses import replace
from datetime import date, time
from decimal import Decimal
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementacion"))

from abc_cpe.dominio.catalogos import (
    TipoComprobante, TipoDocumentoIdentidad,
    AfectacionIgv, Moneda, UnidadMedida
)
from abc_cpe.dominio.modelos import (
    Emisor, Cliente, LineaDetalle, Comprobante
)
from abc_cpe.dominio.errores import ReglaNegocioError, XmlInvalidoError
from abc_cpe.aplicacion.servicio import GenerarXmlComprobanteService
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter
from abc_cpe.infraestructura.validador_xsd import ValidadorXsdLxml


@pytest.fixture
def factura():
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie="F001",
        correlativo=1,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=Emisor(
            ruc="20123456786",
            razon_social="ABC Software Corp - Prueba",
            nombre_comercial=None,
            ubigeo="150101",
            direccion="Av. Ejemplo 123",
            departamento="LIMA",
            provincia="LIMA",
            distrito="LIMA"
        ),
        cliente=Cliente(
            tipo_documento=TipoDocumentoIdentidad.RUC,
            numero_documento="20601234565",
            razon_social="Cliente de Prueba"
        ),
        lineas=[
            LineaDetalle(
                numero_orden=1,
                cantidad=Decimal("2"),
                unidad_medida=UnidadMedida.NIU,
                descripcion="Producto de prueba",
                valor_unitario=Decimal("100.00"),
                afectacion_igv=AfectacionIgv.GRAVADO_OPERACION_ONEROSA
            )
        ]
    )


@pytest.fixture
def servicio():
    return GenerarXmlComprobanteService(
        GeneradorUblAdapter(),
        ValidadorXsdLxml()
    )


def test_generacion_factura_xml_valida(factura, servicio):
    nombre, xml, calculo = servicio.ejecutar(factura)

    ns = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }
    root = etree.fromstring(xml)

    assert nombre == "20123456786-01-F001-1.xml"
    assert root.tag == "{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}Invoice"
    assert root.findtext("cbc:ID", namespaces=ns) == "F001-1"
    assert len(root.findall("cac:InvoiceLine", namespaces=ns)) == 1
    assert calculo.importe_total == Decimal("236.00")

    total_xml = root.findtext(
        "cac:LegalMonetaryTotal/cbc:PayableAmount",
        namespaces=ns
    )
    assert Decimal(total_xml) == Decimal("236.00")


def test_rechaza_cantidad_cero(factura, servicio):
    linea_invalida = replace(
        factura.lineas[0],
        cantidad=Decimal("0")
    )
    factura.lineas = [linea_invalida]

    with pytest.raises(ReglaNegocioError):
        servicio.ejecutar(factura)


def test_rechaza_ruc_emisor_invalido(factura, servicio):
    factura.emisor = replace(
        factura.emisor,
        ruc="00000000000"
    )

    with pytest.raises(ReglaNegocioError):
        servicio.ejecutar(factura)


def test_xsd_rechaza_xml_sin_id(factura, servicio):
    _, xml, _ = servicio.ejecutar(factura)

    root = etree.fromstring(xml)
    ns_cbc = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    id_factura = root.find(f"{{{ns_cbc}}}ID")

    assert id_factura is not None
    root.remove(id_factura)

    xml_invalido = etree.tostring(root, encoding="UTF-8")
    ruta_xsd = ROOT / "implementacion/xsd/maindoc/UBL-Invoice-2.1.xsd"

    with pytest.raises(XmlInvalidoError):
        ValidadorXsdLxml().validar(xml_invalido, str(ruta_xsd))
