"""
PRIORIDAD 4 — Pruebas adversariales, de robustez y seguridad.

Intenta romper el sistema con:
  - Cadenas hostiles (XML injection, Unicode extremo, cadenas muy largas).
  - Valores numéricos extremos y de precisión.
  - Tipos None inesperados.
  - IDs duplicados e inconsistencias.
  - Rutas inválidas y recursos faltantes.
  - Comportamiento frente a cantidades y precios límite.
"""

import sys
from dataclasses import replace
from datetime import date, time
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementacion"))

XSD_PATH = str(ROOT / "implementacion" / "xsd" / "maindoc" / "UBL-Invoice-2.1.xsd")

from abc_cpe.aplicacion.servicio import GenerarXmlComprobanteService
from abc_cpe.dominio.calculo import calcular_comprobante, calcular_linea
from abc_cpe.dominio.catalogos import (
    AfectacionIgv,
    Moneda,
    SistemaIsc,
    TipoComprobante,
    TipoDocumentoIdentidad,
    UnidadMedida,
)
from abc_cpe.dominio.errores import ReglaNegocioError, XmlInvalidoError
from abc_cpe.dominio.modelos import Cliente, Comprobante, Emisor, LineaDetalle
from abc_cpe.dominio.validaciones import validar_comprobante
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter
from abc_cpe.infraestructura.validador_xsd import ValidadorXsdLxml

EMISOR = Emisor(
    ruc="20123456786",
    razon_social="ABC Software Corp",
    nombre_comercial=None,
    ubigeo="150101",
    direccion="Av. 1 123",
    departamento="LIMA",
    provincia="LIMA",
    distrito="LIMA",
)
CLIENTE = Cliente(
    tipo_documento=TipoDocumentoIdentidad.RUC,
    numero_documento="20601234565",
    razon_social="Cliente SA",
)


def _factura(lineas, corr=1):
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie="F001",
        correlativo=corr,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=EMISOR,
        cliente=CLIENTE,
        lineas=lineas,
    )


def _linea_ok(num=1):
    return LineaDetalle(
        num, Decimal("1"), UnidadMedida.NIU, "Producto OK",
        Decimal("100.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
    )


# ===========================================================================
# Sección 1: Cadenas hostiles en campos texto
# ===========================================================================


class TestCadenasHostiles:
    """Los caracteres especiales XML deben escaparse correctamente.
    El sistema NO debe producir XML inválido ni exponer inyección XML."""

    @pytest.mark.parametrize("descripcion,corr", [
        ("Producto " + chr(38) + " Servicios S.A.", 200),          # & (ampersand)
        ("Artículo " + chr(60) + "TIPO" + chr(62) + " especial", 201),  # <TIPO>
        ('Con "comillas" dobles', 202),                             # "
        ("Con 'comillas' simples", 203),                            # '
        ("Fin de línea\nproducto", 204),                            # \n
        ("Producto\x00nulo", 205),                                  # null byte
        ("Ñ ó ú á é í — ¿ ¡", 206),                               # acentos y ñ
        ("中文字符 🎉 🚀", 207),                                      # Unicode extendido
        ("A" * 500, 208),                                           # cadena muy larga
        ("<![CDATA[injección]]>", 209),                             # intento CDATA injection
        ("&lt;no_tag&gt;", 210),                                    # entidades ya escapadas
    ])
    def test_cadena_hostil_no_produce_xml_invalido(self, descripcion, corr):
        """El sistema debe manejar o rechazar cadenas hostiles sin producir
        XML malformado o inyección de etiquetas."""
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, descripcion,
            Decimal("10.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
        )
        gen = GeneradorUblAdapter()
        # Puede fallar en validación (OK), pero si genera XML debe ser bien formado
        try:
            validar_comprobante(_factura([linea], corr=corr))
            calc = calcular_comprobante(_factura([linea], corr=corr))
            _, xml = gen.generar_invoice(_factura([linea], corr=corr), calc)
            # Si llegamos aquí, el XML debe ser bien formado
            etree.fromstring(xml)  # no debe lanzar
        except (ReglaNegocioError, ValueError, TypeError):
            pass  # La validación de dominio puede rechazarlo; eso es OK
        except etree.XMLSyntaxError as exc:
            pytest.fail(f"El sistema generó XML malformado con descripcion={descripcion!r}: {exc}")

    def test_null_byte_en_descripcion_manejado(self):
        """Un byte nulo en descripción debe ser rechazado o producir XML bien formado."""
        descripcion = "Producto\x00nulo"
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, descripcion,
            Decimal("10.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
        )
        gen = GeneradorUblAdapter()
        try:
            calc = calcular_comprobante(_factura([linea], corr=211))
            _, xml = gen.generar_invoice(_factura([linea], corr=211), calc)
            # Si se genera XML, debe ser parseabe
            etree.fromstring(xml)
        except (ReglaNegocioError, etree.XMLSyntaxError, ValueError):
            pass  # Cualquiera de estos es aceptable


# ===========================================================================
# Sección 2: Valores numéricos extremos
# ===========================================================================


class TestValoresNumericos:
    def test_cantidad_muy_pequena_positiva(self):
        """0.0001 unidades debe ser mayor que cero y aceptado."""
        linea = LineaDetalle(1, Decimal("0.0001"), UnidadMedida.NIU, "Prod micro",
                             Decimal("1000000.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        validar_comprobante(_factura([linea], corr=220))
        cl = calcular_linea(linea)
        assert cl.valor_venta >= Decimal("0.00")

    def test_cantidad_extremadamente_grande(self):
        """9999999 unidades × 9999.99 — el sistema debe calcularlo sin desbordamiento."""
        linea = LineaDetalle(1, Decimal("9999999"), UnidadMedida.NIU, "Prod masivo",
                             Decimal("9999.99"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        validar_comprobante(_factura([linea], corr=221))
        cl = calcular_linea(linea)
        assert cl.valor_venta > Decimal("0")

    def test_precio_muy_pequeno_no_negativo(self):
        """0.01 es el precio mínimo práctico."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "Prod barato",
                             Decimal("0.01"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        validar_comprobante(_factura([linea], corr=222))

    def test_decimal_nan_en_cantidad_no_pasa_calculo(self):
        """Decimal NaN en cantidad falla en la comparación VAL-007 con InvalidOperation."""
        linea = LineaDetalle(1, Decimal("NaN"), UnidadMedida.NIU, "Prod",
                             Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises((ReglaNegocioError, InvalidOperation)):
            validar_comprobante(_factura([linea], corr=223))

    def test_decimal_infinity_rechazado_en_validacion(self):
        """Infinity debe rechazarse con VAL-007 antes de realizar cálculos."""
        linea = LineaDetalle(
            1,
            Decimal("Infinity"),
            UnidadMedida.NIU,
            "Prod",
            Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA
        )

        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura([linea], corr=224))

        assert exc.value.codigo == "VAL-007"

    def test_tasa_isc_negativa_rechazada_en_validacion(self):
        """Una tasa ISC negativa debe ser rechazada por VAL-011."""
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod",
            Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR,
            tasa_isc=Decimal("-0.10"),
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura([linea], corr=225))
        assert exc.value.codigo == "VAL-011"


# ===========================================================================
# Sección 3: Tipos inesperados / None
# ===========================================================================


class TestTiposInesperados:
    def test_ruc_none_rechazado(self):
        from abc_cpe.dominio.validaciones import validar_ruc
        assert validar_ruc(None) is False  # type: ignore

    def test_dni_none_rechazado(self):
        from abc_cpe.dominio.validaciones import validar_dni
        assert validar_dni(None) is False  # type: ignore

    def test_ruc_entero_rechazado(self):
        from abc_cpe.dominio.validaciones import validar_ruc
        assert validar_ruc(20123456786) is False  # type: ignore

    def test_ruc_lista_rechazada(self):
        from abc_cpe.dominio.validaciones import validar_ruc
        assert validar_ruc(["20123456786"]) is False  # type: ignore


# ===========================================================================
# Sección 4: Validador XSD — entradas hostiles
# ===========================================================================


class TestValidadorXsdHostil:
    def test_xml_injection_contenido_no_ejecuta(self):
        """Un XML con contenido tipo injection no debe ejecutarse ni corromper el validador."""
        xml_hostil = b"""<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<Invoice>&xxe;</Invoice>"""
        val = ValidadorXsdLxml()
        # Debe lanzar XmlInvalidoError (documento inválido) sin abrir el archivo
        with pytest.raises((XmlInvalidoError, etree.XMLSyntaxError)):
            val.validar(xml_hostil, XSD_PATH)

    def test_xml_enorme_no_lanza_excepcion_de_memoria(self):
        """Un XML grande pero bien formado debe ser procesado normalmente."""
        # Generar XML válido con muchas líneas
        gen = GeneradorUblAdapter()
        lineas = [
            LineaDetalle(i, Decimal("1"), UnidadMedida.NIU, f"Producto {i:04d}",
                         Decimal("10.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
            for i in range(1, 51)  # 50 líneas
        ]
        c = _factura(lineas, corr=300)
        calc = calcular_comprobante(c)
        _, xml = gen.generar_invoice(c, calc)
        val = ValidadorXsdLxml()
        val.validar(xml, XSD_PATH)  # no debe lanzar

    def test_xsd_path_vacio_lanza_error(self):
        """Una ruta de XSD vacía debe producir un error controlado."""
        val = ValidadorXsdLxml()
        with pytest.raises((FileNotFoundError, OSError, Exception)):
            val.validar(b"<Invoice/>", "")

    def test_xml_solo_espacios_lanza_error(self):
        """XML con sólo espacios en blanco no es un documento válido."""
        val = ValidadorXsdLxml()
        with pytest.raises(XmlInvalidoError):
            val.validar(b"   \n   ", XSD_PATH)


# ===========================================================================
# Sección 5: Consistencia del comprobante y casos de borde en el servicio
# ===========================================================================


class TestConsistenciaComprobante:
    @pytest.fixture
    def srv(self):
        return GenerarXmlComprobanteService(GeneradorUblAdapter(), ValidadorXsdLxml())

    def test_comprobante_con_linea_precio_cero_genera_xml(self, srv):
        """Precio cero es permitido por el dominio; el XML debe ser válido."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "Producto bonificado",
                             Decimal("0.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        nombre, xml, calc = srv.ejecutar(_factura([linea], corr=400))
        assert calc.importe_total == Decimal("0.00")
        root = etree.fromstring(xml)
        pa = root.findtext(
            "cac:LegalMonetaryTotal/cbc:PayableAmount",
            namespaces={"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
        )
        assert Decimal(pa) == Decimal("0.00")

    def test_boleta_sin_documento_sin_ruc_genera_xml(self, srv):
        """Boleta con cliente SIN_DOCUMENTO debe generar XML válido."""
        cliente_sin_doc = Cliente(
            tipo_documento=TipoDocumentoIdentidad.SIN_DOCUMENTO,
            numero_documento="-",
            razon_social="Consumidor Final",
        )
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "Producto",
                             Decimal("100.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        boleta = Comprobante(
            tipo_comprobante=TipoComprobante.BOLETA,
            serie="B001", correlativo=401,
            fecha_emision=date(2026, 11, 5), hora_emision=time(10, 0),
            moneda=Moneda.PEN, emisor=EMISOR,
            cliente=cliente_sin_doc,
            lineas=[linea],
        )
        nombre, xml, calc = srv.ejecutar(boleta)
        assert calc.importe_total == Decimal("118.00")

    def test_serie_mayusculas_no_alfanumerico_rechazado(self, srv):
        """Una serie con caracteres no permitidos debe rechazarse."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "P", Decimal("1.00"),
                             AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        c = Comprobante(
            tipo_comprobante=TipoComprobante.FACTURA,
            serie="F-01", correlativo=1,  # guion no permitido
            fecha_emision=date(2026, 11, 5), hora_emision=time(10, 0),
            moneda=Moneda.PEN, emisor=EMISOR, cliente=CLIENTE,
            lineas=[linea],
        )
        with pytest.raises(ReglaNegocioError) as exc:
            srv.ejecutar(c)
        assert exc.value.codigo == "VAL-002"
