"""Demo académica: datos de dominio -> XML Invoice 2.1 -> XSD -> XMLDSig de prueba.

Desde la raíz del proyecto:
    .\.venv\Scripts\python.exe ejemplos/generar_factura_firmada_demo.py

No equivale a firma tributaria válida, ni envío/aceptación SUNAT.
"""

from __future__ import annotations

import sys
from datetime import date, time
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'implementacion'))

from abc_cpe.aplicacion.servicio import GenerarXmlComprobanteService
from abc_cpe.dominio.catalogos import (
    AfectacionIgv, Moneda, TipoComprobante, TipoDocumentoIdentidad, UnidadMedida,
)
from abc_cpe.dominio.modelos import Cliente, Comprobante, Emisor, LineaDetalle
from abc_cpe.infraestructura.firmador_xml_demo import firmar_xml_prueba, verificar_firma_prueba
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter
from abc_cpe.infraestructura.validador_xsd import ValidadorXsdLxml

RUTA_XSD = RAIZ / 'implementacion' / 'xsd' / 'maindoc' / 'UBL-Invoice-2.1.xsd'
SALIDA = RAIZ / 'ejemplos' / 'salida'


def crear_factura_ejemplo() -> Comprobante:
    """Datos didácticos, no corresponden a una transacción tributaria real."""
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie='F001',
        correlativo=1,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=Emisor(
            ruc='20123456786',
            razon_social='ABC Software Corp - Prueba',
            nombre_comercial=None,
            ubigeo='150101',
            direccion='Av. Ejemplo 123',
            departamento='LIMA',
            provincia='LIMA',
            distrito='LIMA',
        ),
        cliente=Cliente(
            tipo_documento=TipoDocumentoIdentidad.RUC,
            numero_documento='20601234565',
            razon_social='Cliente de Prueba',
        ),
        lineas=[
            LineaDetalle(
                numero_orden=1,
                cantidad=Decimal('2'),
                unidad_medida=UnidadMedida.NIU,
                descripcion='Producto de prueba',
                valor_unitario=Decimal('100.00'),
                afectacion_igv=AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            )
        ],
    )


def generar_archivos():
    validador = ValidadorXsdLxml()
    servicio = GenerarXmlComprobanteService(GeneradorUblAdapter(), validador)
    nombre, xml_original, calculo = servicio.ejecutar(crear_factura_ejemplo())
    assert calculo.importe_total == Decimal('236.00'), calculo.importe_total
    xml_firmado = firmar_xml_prueba(xml_original)
    validador.validar(xml_firmado, str(RUTA_XSD))
    verificar_firma_prueba(xml_firmado)

    SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_original = SALIDA / nombre
    ruta_firmado = SALIDA / nombre.replace('.xml', '-FIRMADO-DEMO.xml')
    ruta_original.write_bytes(xml_original)
    ruta_firmado.write_bytes(xml_firmado)
    print('FACTURA XML GENERADA Y VALIDADA CONTRA INVOICE XSD 2.1')
    print('XML SIN FIRMA:', ruta_original)
    print('XML CON FIRMA DE PRUEBA:', ruta_firmado)
    print('TOTAL:', calculo.importe_total, 'PEN (base 200.00 + IGV 36.00)')
    print('XSD: APROBADO')
    print('FIRMA XMLDSig RSA-SHA256: VERIFICADA CRIPTOGRAFICAMENTE')
    print('ADVERTENCIA: CERTIFICADO AUTOFIRMADO DE PRUEBA. NO VALIDO ANTE SUNAT.')
    return ruta_original, ruta_firmado


if __name__ == '__main__':
    generar_archivos()
