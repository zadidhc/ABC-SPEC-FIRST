"""
PRIORIDAD 2 — Corrección financiera exacta con Decimal.

Cubre:
  - Factura de una línea (gravada, exonerada, inafecta).
  - Factura multi-línea con tipos mixtos.
  - ISC al valor (sistema 01).
  - ISC específico (sistema 02).
  - ISC al PVP (sistema 03) — MARCADO como pendiente de verificación normativa.
  - ISC como parte de la base del IGV.
  - Redondeo en medio centavo (ROUND_HALF_UP).
  - Cantidades y precios fraccionarios.
  - Acumulación de redondeos en muchas líneas.
  - Consistencia entre totales de líneas y totales del comprobante.
  - Cruce de totales del dominio vs valores serializados en XML.
  - monto_en_letras para importes extremos y moneda USD.
"""

import sys
from datetime import date, time
from decimal import Decimal
from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementacion"))

from abc_cpe.dominio.calculo import calcular_comprobante, calcular_linea, redondear_2, TASA_IGV
from abc_cpe.dominio.catalogos import (
    AfectacionIgv,
    Moneda,
    SistemaIsc,
    TipoComprobante,
    TipoDocumentoIdentidad,
    UnidadMedida,
)
from abc_cpe.dominio.errores import ReglaNegocioError
from abc_cpe.dominio.modelos import (
    CalculoComprobante,
    Cliente,
    Comprobante,
    Emisor,
    LineaDetalle,
)
from abc_cpe.dominio.monto_en_letras import monto_en_letras, numero_a_palabras
from abc_cpe.infraestructura.generador_ubl import GeneradorUblAdapter

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

NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
}


def _comp(lineas, corr=1, moneda=Moneda.PEN):
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie="F001",
        correlativo=corr,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=moneda,
        emisor=EMISOR,
        cliente=CLIENTE,
        lineas=lineas,
    )


def _grav(cantidad, precio, num=1):
    return LineaDetalle(num, Decimal(str(cantidad)), UnidadMedida.NIU, f"Prod {num}",
                        Decimal(str(precio)), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)


def _exo(cantidad, precio, num=1):
    return LineaDetalle(num, Decimal(str(cantidad)), UnidadMedida.NIU, f"Exo {num}",
                        Decimal(str(precio)), AfectacionIgv.EXONERADO_OPERACION_ONEROSA)


def _ina(cantidad, precio, num=1):
    return LineaDetalle(num, Decimal(str(cantidad)), UnidadMedida.NIU, f"Ina {num}",
                        Decimal(str(precio)), AfectacionIgv.INAFECTO_OPERACION_ONEROSA)


# ===========================================================================
# Sección 1: Cálculo de una línea individual
# ===========================================================================


class TestCalcularLineaUnica:
    def test_gravada_calculo_exacto(self):
        """2 unidades × S/100.00 = S/200.00 gravado; IGV = S/36.00; total = S/236.00."""
        l = _grav(2, "100.00")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("200.00")
        assert cl.base_igv == Decimal("200.00")
        assert cl.monto_igv == Decimal("36.00")
        assert cl.total_linea == Decimal("236.00")

    def test_exonerada_sin_igv(self):
        l = _exo(5, "50.00")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("250.00")
        assert cl.base_igv == Decimal("0.00")
        assert cl.monto_igv == Decimal("0.00")
        assert cl.monto_isc == Decimal("0.00")
        assert cl.total_linea == Decimal("250.00")

    def test_inafecta_sin_igv(self):
        l = _ina(3, "30.00")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("90.00")
        assert cl.base_igv == Decimal("0.00")
        assert cl.monto_igv == Decimal("0.00")
        assert cl.total_linea == Decimal("90.00")

    def test_precio_unitario_con_impuestos_gravada(self):
        """El precio unitario con impuestos es total_linea / cantidad."""
        l = _grav(2, "100.00")
        cl = calcular_linea(l)
        expected = Decimal("236.00") / Decimal("2")
        assert cl.precio_unitario_con_impuestos == expected

    def test_cantidad_fraccionaria(self):
        """3 × 0.333 = 0.999, redondeado a 1.00; IGV = 0.18; total = 1.18."""
        l = _grav("3", "0.333")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("1.00")
        assert cl.monto_igv == Decimal("0.18")
        assert cl.total_linea == Decimal("1.18")

    def test_redondeo_medio_centavo_up(self):
        """1 × 1.005 debe redondear a 1.01 (ROUND_HALF_UP)."""
        l = _grav(1, "1.005")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("1.01")

    def test_redondeo_medio_centavo_down(self):
        """1 × 1.004 debe redondear a 1.00 (truncar hacia abajo)."""
        l = _grav(1, "1.004")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("1.00")

    def test_precio_cero_gravada(self):
        """Precio cero: sin impuestos ni nada."""
        l = _grav(1, "0.00")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("0.00")
        assert cl.monto_igv == Decimal("0.00")
        assert cl.total_linea == Decimal("0.00")

    def test_cantidad_muy_pequena(self):
        """0.001 unidades × 1000.00 = 1.00."""
        l = _grav("0.001", "1000.00")
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("1.00")


# ===========================================================================
# Sección 2: ISC en línea individual
# ===========================================================================


class TestCalcularLineaConIsc:
    def test_isc_al_valor_10_pct(self):
        """10 unidades × S/5.00 = S/50.00; ISC 10% = S/5.00; base IGV = S/55.00; IGV = S/9.90; total = S/64.90."""
        l = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Cigarro",
            Decimal("5.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("50.00")
        assert cl.monto_isc == Decimal("5.00")
        assert cl.base_igv == Decimal("55.00")
        assert cl.monto_igv == Decimal("9.90")
        assert cl.total_linea == Decimal("64.90")

    def test_isc_especifico_1_50_por_unidad(self):
        """10 unidades × S/5.00; ISC S/1.50/u = S/15.00; base IGV = S/65.00; IGV = S/11.70; total = S/76.70."""
        l = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Cerveza",
            Decimal("5.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.ESPECIFICO, monto_fijo_isc=Decimal("1.50"),
        )
        cl = calcular_linea(l)
        assert cl.valor_venta == Decimal("50.00")
        assert cl.monto_isc == Decimal("15.00")
        assert cl.base_igv == Decimal("65.00")
        assert cl.monto_igv == redondear_2(Decimal("65.00") * TASA_IGV)
        assert cl.total_linea == cl.valor_venta + cl.monto_isc + cl.monto_igv

    def test_isc_pvp_formula_pendiente_verificacion(self):
        """
        Sistema 03 (Al PVP): ISC = round2(cantidad × PVP × tasa).
        NOTA: La fórmula está marcada como PENDIENTE DE VERIFICACIÓN NORMATIVA.
        Este test documenta el comportamiento implementado actual, no valida
        que sea fiscalmente correcto según SUNAT.
        """
        l = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Prod PVP",
            Decimal("5.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_PVP,
            pvp_isc=Decimal("8.00"), tasa_isc=Decimal("0.10"),
        )
        cl = calcular_linea(l)
        # Fórmula implementada: ISC = round2(10 × 8.00 × 0.10) = 8.00
        isc_implementado = redondear_2(Decimal("10") * Decimal("8.00") * Decimal("0.10"))
        assert cl.monto_isc == isc_implementado, (
            "ISC PVP: fórmula implementada difiere. Verificar contra RS 097-2012."
        )

    def test_isc_es_parte_de_base_igv(self):
        """El ISC SIEMPRE se suma al valor_venta para formar la base del IGV (Ley del IGV)."""
        l = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod",
            Decimal("100.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.20"),
        )
        cl = calcular_linea(l)
        assert cl.base_igv == cl.valor_venta + cl.monto_isc


# ===========================================================================
# Sección 3: Totales del comprobante
# ===========================================================================


class TestCalcularComprobante:
    def test_una_linea_gravada_totales(self):
        c = _comp([_grav(2, "100.00")])
        calc = calcular_comprobante(c)
        assert calc.total_gravadas == Decimal("200.00")
        assert calc.total_exoneradas == Decimal("0.00")
        assert calc.total_inafectas == Decimal("0.00")
        assert calc.total_igv == Decimal("36.00")
        assert calc.importe_total == Decimal("236.00")

    def test_una_linea_exonerada_totales(self):
        c = _comp([_exo(5, "50.00")])
        calc = calcular_comprobante(c)
        assert calc.total_exoneradas == Decimal("250.00")
        assert calc.total_igv == Decimal("0.00")
        assert calc.total_isc == Decimal("0.00")
        assert calc.importe_total == Decimal("250.00")

    def test_una_linea_inafecta_totales(self):
        c = _comp([_ina(3, "30.00")])
        calc = calcular_comprobante(c)
        assert calc.total_inafectas == Decimal("90.00")
        assert calc.total_igv == Decimal("0.00")
        assert calc.importe_total == Decimal("90.00")

    def test_mixta_gravada_exonerada_inafecta(self):
        """
        grav: 2×100 = 200; exo: 5×50 = 250; ina: 3×30 = 90.
        IGV sobre gravada: 200×0.18 = 36.
        total_vv = 200+250+90 = 540; importe = 540+36 = 576.
        """
        lineas = [_grav(2, "100.00", 1), _exo(5, "50.00", 2), _ina(3, "30.00", 3)]
        c = _comp(lineas)
        calc = calcular_comprobante(c)
        assert calc.total_gravadas == Decimal("200.00")
        assert calc.total_exoneradas == Decimal("250.00")
        assert calc.total_inafectas == Decimal("90.00")
        assert calc.base_igv == Decimal("200.00")
        assert calc.total_igv == Decimal("36.00")
        assert calc.total_valor_venta == Decimal("540.00")
        assert calc.importe_total == Decimal("576.00")

    def test_multilinea_gravada_totales(self):
        """5 líneas × 2 × 100 = 1000 gravado; IGV = 180."""
        lineas = [_grav(2, "100.00", i) for i in range(1, 6)]
        c = _comp(lineas)
        calc = calcular_comprobante(c)
        assert calc.total_gravadas == Decimal("1000.00")
        assert calc.total_igv == Decimal("180.00")
        assert calc.importe_total == Decimal("1180.00")

    def test_invariante_suma_lineas_igual_total(self):
        """La suma de total_linea de cada línea debe igualar importe_total."""
        lineas = [_grav(2, "100.00", i) for i in range(1, 4)]
        c = _comp(lineas)
        calc = calcular_comprobante(c)
        suma_lineas = sum(cl.total_linea for cl in calc.lineas_calculadas)
        assert suma_lineas == calc.importe_total

    def test_base_igv_incluye_isc(self):
        """base_igv = total_gravadas + total_isc (ISC integra la base del IGV)."""
        l = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Prod ISC",
            Decimal("5.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        c = _comp([l])
        calc = calcular_comprobante(c)
        assert calc.base_igv == calc.total_gravadas + calc.total_isc
        assert calc.base_igv == Decimal("55.00")

    def test_base_isc_es_valor_venta_lineas_con_isc(self):
        """base_isc = suma de valor_venta de las líneas que tienen ISC."""
        l1 = _grav(1, "100.00", 1)  # sin ISC
        l2 = LineaDetalle(
            2, Decimal("10"), UnidadMedida.NIU, "Con ISC",
            Decimal("5.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        c = _comp([l1, l2])
        calc = calcular_comprobante(c)
        # Solo l2 tiene ISC: base_isc = 50.00
        assert calc.base_isc == Decimal("50.00")

    def test_comprobante_sin_lineas_rechazado(self):
        c = _comp([])
        with pytest.raises(ReglaNegocioError) as exc:
            calcular_comprobante(c)
        assert exc.value.codigo == "VAL-006"


# ===========================================================================
# Sección 4: Redondeo acumulado
# ===========================================================================


class TestRedondeoAcumulado:
    def test_diez_lineas_de_1_005_no_rompe_invariante(self):
        """
        10 líneas × 1×1.005. Cada una: valor_venta=1.01, IGV=0.18, total=1.19.
        Invariante: sum(total_lineas) == importe_total.
        """
        lineas = [_grav(1, "1.005", i) for i in range(1, 11)]
        c = _comp(lineas)
        calc = calcular_comprobante(c)
        suma_lineas = sum(cl.total_linea for cl in calc.lineas_calculadas)
        assert suma_lineas == calc.importe_total
        assert calc.importe_total == Decimal("11.90")

    def test_tres_lineas_tercio_calculo_exacto(self):
        """3 líneas × 1×(1/3). Cada una: valor_venta=0.33; total≈0.39."""
        lineas = [_grav(1, "0.333333", i) for i in range(1, 4)]
        c = _comp(lineas)
        calc = calcular_comprobante(c)
        suma_lineas = sum(cl.total_linea for cl in calc.lineas_calculadas)
        assert suma_lineas == calc.importe_total


# ===========================================================================
# Sección 5: Cruce dominio → XML (corrección de serialización)
# ===========================================================================


class TestCruceCalculoXml:
    """Verifica que los valores calculados en el dominio coincidan exactamente
    con los valores serializados en el XML generado."""

    @pytest.fixture
    def gen(self):
        return GeneradorUblAdapter()

    def _xml_root(self, gen, c):
        calc = calcular_comprobante(c)
        _, xml = gen.generar_invoice(c, calc)
        return etree.fromstring(xml), calc

    def test_payable_amount_xml_igual_dominio(self, gen):
        c = _comp([_grav(2, "100.00")])
        root, calc = self._xml_root(gen, c)
        total_xml = root.findtext("cac:LegalMonetaryTotal/cbc:PayableAmount", namespaces=NS)
        assert Decimal(total_xml) == calc.importe_total

    def test_line_extension_amount_xml_igual_dominio(self, gen):
        c = _comp([_grav(2, "100.00")])
        root, calc = self._xml_root(gen, c)
        ext_xml = root.findtext("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", namespaces=NS)
        assert Decimal(ext_xml) == calc.total_valor_venta

    def test_tax_amount_xml_igual_dominio(self, gen):
        c = _comp([_grav(2, "100.00")])
        root, calc = self._xml_root(gen, c)
        tax_xml = root.findtext("cac:TaxTotal/cbc:TaxAmount", namespaces=NS)
        total_tributos = calc.total_isc + calc.total_igv
        assert Decimal(tax_xml) == total_tributos

    def test_invoice_lines_count_xml_igual_dominio(self, gen):
        lineas = [_grav(1, "10.00", i) for i in range(1, 4)]
        c = _comp(lineas, corr=2)
        root, calc = self._xml_root(gen, c)
        lines_xml = root.findall("cac:InvoiceLine", namespaces=NS)
        assert len(lines_xml) == len(c.lineas)

    def test_line_extension_amount_por_linea_xml(self, gen):
        """El LineExtensionAmount de cada InvoiceLine debe coincidir con valor_venta de dominio."""
        lineas = [_grav(2, "100.00", 1), _exo(5, "10.00", 2)]
        c = _comp(lineas, corr=3)
        root, calc = self._xml_root(gen, c)
        inv_lines = root.findall("cac:InvoiceLine", namespaces=NS)
        for i, (inv_line, cl) in enumerate(zip(inv_lines, calc.lineas_calculadas)):
            ext = inv_line.findtext("cbc:LineExtensionAmount", namespaces=NS)
            assert Decimal(ext) == cl.valor_venta, f"Línea {i+1}: LineExtensionAmount no coincide"


# ===========================================================================
# Sección 6: monto_en_letras
# ===========================================================================


class TestMontoEnLetras:
    def test_cero(self):
        assert monto_en_letras(Decimal("0.00")) == "SON: CERO CON 00/100 SOLES"

    def test_cien(self):
        assert monto_en_letras(Decimal("100.00")) == "SON: CIEN CON 00/100 SOLES"

    def test_cien_cincuenta(self):
        assert monto_en_letras(Decimal("100.50")) == "SON: CIEN CON 50/100 SOLES"

    def test_mil(self):
        assert monto_en_letras(Decimal("1000.00")) == "SON: MIL CON 00/100 SOLES"

    def test_un_millon(self):
        assert monto_en_letras(Decimal("1000000.00")) == "SON: UN MILLON CON 00/100 SOLES"

    def test_dos_millones(self):
        assert monto_en_letras(Decimal("2000000.00")) == "SON: DOS MILLONES CON 00/100 SOLES"

    def test_moneda_usd(self):
        assert monto_en_letras(Decimal("100.50"), Moneda.USD) == "SON: CIEN CON 50/100 DOLARES AMERICANOS"

    def test_centavos_01(self):
        assert monto_en_letras(Decimal("0.01")) == "SON: CERO CON 01/100 SOLES"

    def test_centavos_99(self):
        assert monto_en_letras(Decimal("0.99")) == "SON: CERO CON 99/100 SOLES"

    def test_236(self):
        """Valor de la factura canónica de prueba."""
        assert monto_en_letras(Decimal("236.00")) == "SON: DOSCIENTOS TREINTA Y SEIS CON 00/100 SOLES"

    def test_numero_palabras_1001(self):
        assert numero_a_palabras(1001) == "MIL UN"

    def test_numero_palabras_1000(self):
        assert numero_a_palabras(1000) == "MIL"

    def test_numero_palabras_21(self):
        assert numero_a_palabras(21) == "VEINTIUN"

    def test_numero_palabras_100(self):
        assert numero_a_palabras(100) == "CIEN"

    def test_numero_palabras_101(self):
        assert numero_a_palabras(101) == "CIENTO UN"

