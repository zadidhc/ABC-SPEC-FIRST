"""Pruebas adicionales de firma XMLDSig demostrativa; no son certificación SUNAT."""

from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from pathlib import Path

import pytest

from abc_cpe.aplicacion.servicio import GenerarXmlComprobanteService
from abc_cpe.dominio.catalogos import (
    AfectacionIgv, Moneda, TipoComprobante, TipoDocumentoIdentidad, UnidadMedida,
)
from abc_cpe.dominio.modelos import Cliente, Comprobante, Emisor, LineaDetalle
from abc_cpe.infraestructura.firmador_xml_demo import firmar_xml_prueba, verificar_firma_prueba
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter
from abc_cpe.infraestructura.validador_xsd import ValidadorXsdLxml

RUTA_XSD = Path(__file__).resolve().parents[1] / 'implementacion' / 'xsd' / 'maindoc' / 'UBL-Invoice-2.1.xsd'


@pytest.fixture
def xml_original():
    factura = Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie='F001', correlativo=1,
        fecha_emision=date(2026, 11, 5), hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=Emisor(
            ruc='20123456786', razon_social='ABC Software Corp - Prueba',
            nombre_comercial=None, ubigeo='150101', direccion='Av. Ejemplo 123',
            departamento='LIMA', provincia='LIMA', distrito='LIMA',
        ),
        cliente=Cliente(
            tipo_documento=TipoDocumentoIdentidad.RUC,
            numero_documento='20601234565', razon_social='Cliente de Prueba',
        ),
        lineas=[LineaDetalle(
            numero_orden=1, cantidad=Decimal('2'), unidad_medida=UnidadMedida.NIU,
            descripcion='Producto de prueba', valor_unitario=Decimal('100.00'),
            afectacion_igv=AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
        )],
    )
    _, xml, total = GenerarXmlComprobanteService(
        GeneradorUblAdapter(), ValidadorXsdLxml()
    ).ejecutar(factura)
    assert total.importe_total == Decimal('236.00')
    return xml


def test_xml_firmado_demo_pasa_xsd(xml_original):
    firmado = firmar_xml_prueba(xml_original)
    ValidadorXsdLxml().validar(firmado, str(RUTA_XSD))


def test_firma_demostrativa_se_verifica(xml_original):
    firmado = firmar_xml_prueba(xml_original)
    verificar_firma_prueba(firmado)


def test_firma_detecta_alteraciones(xml_original):
    firmado = firmar_xml_prueba(xml_original)
    alterado = firmado.replace(b'Producto de prueba', b'Producto modificado')
    assert alterado != firmado
    with pytest.raises(ValueError, match='alterado'):
        verificar_firma_prueba(alterado)
