"""
PRIORIDAD 1 — Validaciones de dominio y casos de frontera.

Cubre VAL-001 … VAL-014:
  - RUC checksum, longitud, prefijos.
  - DNI.
  - Serie / tipo de comprobante.
  - Correlativo rango.
  - Coherencia cliente/tipo-comprobante.
  - Fechas de vencimiento.
  - Ausencia de líneas, IDs duplicados, secuencia incorrecta.
  - Cantidades / precios / descripciones límite.
  - Tipos Decimal inválidos (NaN, Infinity).
  - Configuración ISC incompleta.
"""

import sys
from datetime import date, time
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementacion"))

from abc_cpe.dominio.catalogos import (
    AfectacionIgv,
    Moneda,
    SistemaIsc,
    TipoComprobante,
    TipoDocumentoIdentidad,
    UnidadMedida,
)
from abc_cpe.dominio.calculo import calcular_linea
from abc_cpe.dominio.errores import ReglaNegocioError
from abc_cpe.dominio.modelos import Cliente, Comprobante, Emisor, LineaDetalle
from abc_cpe.dominio.validaciones import (
    validar_comprobante,
    validar_dni,
    validar_ruc,
    validar_serie_comprobante,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EMISOR_VALIDO = Emisor(
    ruc="20123456786",
    razon_social="ABC Software Corp",
    nombre_comercial=None,
    ubigeo="150101",
    direccion="Av. 1 123",
    departamento="LIMA",
    provincia="LIMA",
    distrito="LIMA",
)
CLIENTE_RUC = Cliente(
    tipo_documento=TipoDocumentoIdentidad.RUC,
    numero_documento="20601234565",
    razon_social="Cliente SA",
)
LINEA_OK = LineaDetalle(
    numero_orden=1,
    cantidad=Decimal("1"),
    unidad_medida=UnidadMedida.NIU,
    descripcion="Producto OK",
    valor_unitario=Decimal("100.00"),
    afectacion_igv=AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
)


def _factura(lineas=None, serie="F001", corr=1, cliente=None, emisor=None, fvenc=None):
    return Comprobante(
        tipo_comprobante=TipoComprobante.FACTURA,
        serie=serie,
        correlativo=corr,
        fecha_emision=date(2026, 11, 5),
        hora_emision=time(10, 0),
        moneda=Moneda.PEN,
        emisor=emisor or EMISOR_VALIDO,
        cliente=cliente or CLIENTE_RUC,
        lineas=lineas if lineas is not None else [LINEA_OK],
        fecha_vencimiento=fvenc,
    )


# ===========================================================================
# Sección 1: validar_ruc
# ===========================================================================


class TestValidarRuc:
    """VAL-001: RUC algoritmo Módulo 11, longitud y prefijos."""

    # Casos válidos
    @pytest.mark.parametrize("ruc", [
        "20123456786",  # fixture principal (empresa)
        "20601234565",  # cliente de prueba
        "10123456781",  # persona natural (prefijo 10, dv=1 correcto)
    ])
    def test_ruc_validos(self, ruc):
        assert validar_ruc(ruc) is True

    # Longitud incorrecta
    @pytest.mark.parametrize("ruc", ["2012345678", "201234567890", "", "0"])
    def test_ruc_longitud_incorrecta(self, ruc):
        assert validar_ruc(ruc) is False

    # Prefijo no autorizado
    @pytest.mark.parametrize("ruc", [
        "30123456789",  # prefijo 30 no válido
        "00000000000",  # prefijo 00
        "11000000000",  # prefijo 11
        "50000000000",  # prefijo 50
    ])
    def test_ruc_prefijo_invalido(self, ruc):
        assert validar_ruc(ruc) is False

    # Dígito verificador incorrecto
    @pytest.mark.parametrize("ruc", [
        "20123456780",  # último dígito alterado
        "20123456781",
        "20601234560",
    ])
    def test_ruc_digito_verificador_incorrecto(self, ruc):
        assert validar_ruc(ruc) is False

    # Contiene no-dígitos
    @pytest.mark.parametrize("ruc", ["2012345678X", "20-12345678", "20 12345678"])
    def test_ruc_no_numerico(self, ruc):
        assert validar_ruc(ruc) is False

    # Tipos no string
    @pytest.mark.parametrize("ruc", [None, 20123456786, 20123456786.0, [], {}])
    def test_ruc_tipo_incorrecto(self, ruc):
        assert validar_ruc(ruc) is False


# ===========================================================================
# Sección 2: validar_dni
# ===========================================================================


class TestValidarDni:
    @pytest.mark.parametrize("dni", ["45678901", "00000000", "99999999"])
    def test_dni_validos(self, dni):
        assert validar_dni(dni) is True

    @pytest.mark.parametrize("dni", [
        "4567890",   # 7 dígitos
        "456789012", # 9 dígitos
        "",
        "4567890X",
        "4567-901",
    ])
    def test_dni_invalidos(self, dni):
        assert validar_dni(dni) is False

    @pytest.mark.parametrize("dni", [None, 45678901, []])
    def test_dni_tipo_incorrecto(self, dni):
        assert validar_dni(dni) is False


# ===========================================================================
# Sección 3: validar_serie_comprobante
# ===========================================================================


class TestValidarSerie:
    @pytest.mark.parametrize("serie", ["F001", "F999", "FABC", "F0A1"])
    def test_facturas_validas(self, serie):
        assert validar_serie_comprobante(TipoComprobante.FACTURA, serie) is True

    @pytest.mark.parametrize("serie", ["B001", "BABC"])
    def test_boletas_validas(self, serie):
        assert validar_serie_comprobante(TipoComprobante.BOLETA, serie) is True

    @pytest.mark.parametrize("serie", [
        "B001",  # boleta para factura
        "f001",  # minúscula
        "F 01",  # espacio
        "F01",   # 3 chars
        "F00001",# 6 chars
        "",
        "0001",
    ])
    def test_factura_serie_invalida(self, serie):
        assert validar_serie_comprobante(TipoComprobante.FACTURA, serie) is False

    @pytest.mark.parametrize("serie", ["F001", "b001", "B 01", "B01"])
    def test_boleta_serie_invalida(self, serie):
        assert validar_serie_comprobante(TipoComprobante.BOLETA, serie) is False


# ===========================================================================
# Sección 4: validar_comprobante — correlativo
# ===========================================================================


class TestValidarCorrelativo:
    def test_correlativo_minimo_valido(self):
        validar_comprobante(_factura(corr=1))  # no debe lanzar

    def test_correlativo_maximo_valido(self):
        validar_comprobante(_factura(corr=99_999_999))

    def test_correlativo_cero_rechazado(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(corr=0))
        assert exc.value.codigo == "VAL-003"

    def test_correlativo_negativo_rechazado(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(corr=-1))
        assert exc.value.codigo == "VAL-003"

    def test_correlativo_sobre_maximo_rechazado(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(corr=100_000_000))
        assert exc.value.codigo == "VAL-003"

    def test_correlativo_tipo_float_rechazado(self):
        """Un float no es int — debe fallar VAL-003."""
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(corr=1.0))  # type: ignore[arg-type]
        assert exc.value.codigo == "VAL-003"


# ===========================================================================
# Sección 5: validar_comprobante — cliente/tipo
# ===========================================================================


class TestValidarClienteTipo:
    def test_factura_requiere_ruc(self):
        cliente_dni = Cliente(TipoDocumentoIdentidad.DNI, "45678901", "Juan")
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(cliente=cliente_dni))
        assert exc.value.codigo == "VAL-004"

    def test_factura_ruc_cliente_invalido_rechazado(self):
        cliente_ruc_malo = Cliente(TipoDocumentoIdentidad.RUC, "20000000000", "Bad Corp")
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(cliente=cliente_ruc_malo))
        assert exc.value.codigo == "VAL-004"

    def test_boleta_con_dni_valido(self):
        cliente_dni = Cliente(TipoDocumentoIdentidad.DNI, "45678901", "Juan")
        boleta = Comprobante(
            tipo_comprobante=TipoComprobante.BOLETA,
            serie="B001",
            correlativo=1,
            fecha_emision=date(2026, 11, 5),
            hora_emision=time(10, 0),
            moneda=Moneda.PEN,
            emisor=EMISOR_VALIDO,
            cliente=cliente_dni,
            lineas=[LINEA_OK],
        )
        validar_comprobante(boleta)  # no debe lanzar

    def test_boleta_con_dni_mal_formato_rechazado(self):
        cliente_dni_malo = Cliente(TipoDocumentoIdentidad.DNI, "123", "Juan")
        boleta = Comprobante(
            tipo_comprobante=TipoComprobante.BOLETA,
            serie="B001",
            correlativo=1,
            fecha_emision=date(2026, 11, 5),
            hora_emision=time(10, 0),
            moneda=Moneda.PEN,
            emisor=EMISOR_VALIDO,
            cliente=cliente_dni_malo,
            lineas=[LINEA_OK],
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(boleta)
        assert exc.value.codigo == "VAL-004"

    def test_serie_boleta_con_tipo_factura_rechazada(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(serie="B001"))
        assert exc.value.codigo == "VAL-002"

    def test_emisor_ruc_invalido_rechazado(self):
        emisor_malo = Emisor("11111111111", "Bad Emisor", None, "150101", "Av 1", "LIMA", "LIMA", "LIMA")
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(emisor=emisor_malo))
        assert exc.value.codigo == "VAL-001"


# ===========================================================================
# Sección 6: validar_comprobante — fechas
# ===========================================================================


class TestValidarFechas:
    def test_fecha_vencimiento_igual_emision_ok(self):
        validar_comprobante(_factura(fvenc=date(2026, 11, 5)))  # no lanza

    def test_fecha_vencimiento_posterior_ok(self):
        validar_comprobante(_factura(fvenc=date(2026, 12, 31)))  # no lanza

    def test_fecha_vencimiento_anterior_rechazada(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(fvenc=date(2026, 11, 4)))
        assert exc.value.codigo == "VAL-005"

    def test_sin_fecha_vencimiento_ok(self):
        validar_comprobante(_factura())  # no lanza


# ===========================================================================
# Sección 7: validar_comprobante — líneas
# ===========================================================================


class TestValidarLineas:
    def test_sin_lineas_rechazado(self):
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[]))
        assert exc.value.codigo == "VAL-006"

    def test_cantidad_cero_rechazada(self):
        linea = LineaDetalle(1, Decimal("0"), UnidadMedida.NIU, "P", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-007"

    def test_cantidad_negativa_rechazada(self):
        linea = LineaDetalle(1, Decimal("-1"), UnidadMedida.NIU, "P", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-007"

    def test_valor_unitario_negativo_rechazado(self):
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "P", Decimal("-1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-008"

    def test_valor_unitario_cero_permitido(self):
        """El precio cero no está prohibido en la especificación para descuentos totales."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "Producto bonificado", Decimal("0.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        validar_comprobante(_factura(lineas=[linea]))  # no debe lanzar

    def test_descripcion_vacia_rechazada(self):
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-009"

    def test_descripcion_solo_espacios_rechazada(self):
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "   ", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-009"

    def test_descripcion_unicode_valida(self):
        """Caracteres Unicode y acentos son válidos en descripciones."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "Ñoño ñoño — ¿Qué? αβγ 中文", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        validar_comprobante(_factura(lineas=[linea]))  # no debe lanzar

    def test_ids_duplicados_rechazados(self):
        """
        DEFECTO CONOCIDO: La validación actual no verifica IDs duplicados en líneas.
        Este test documenta el comportamiento actual para servir de regresión
        si se implementa la validación futura (VAL-015 pendiente).
        """
        lineas = [
            LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "P1", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA),
            LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "P2", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA),
        ]

        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=lineas))

        assert exc.value.codigo == "VAL-015"

    def test_multiples_lineas_validas(self):
        lineas = [
            LineaDetalle(i, Decimal("1"), UnidadMedida.NIU, f"Producto {i}", Decimal("10.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
            for i in range(1, 6)
        ]
        validar_comprobante(_factura(lineas=lineas))  # no debe lanzar


# ===========================================================================
# Sección 8: validar_comprobante — ISC
# ===========================================================================


class TestValidarIsc:
    def test_isc_sin_sistema_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Prod", Decimal("5.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True,
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-014"

    def test_isc_en_exonerada_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.EXONERADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-010"

    def test_isc_en_inafecta_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.INAFECTO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-010"

    def test_isc_al_valor_sin_tasa_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=None,
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-011"

    def test_isc_al_valor_tasa_cero_rechazada(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0"),
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-011"

    def test_isc_especifico_sin_monto_fijo_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.ESPECIFICO, monto_fijo_isc=None,
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-012"

    def test_isc_pvp_sin_pvp_rechazado(self):
        linea = LineaDetalle(
            1, Decimal("1"), UnidadMedida.NIU, "Prod", Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_PVP,
            tasa_isc=Decimal("0.10"), pvp_isc=None,
        )
        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))
        assert exc.value.codigo == "VAL-013"

    def test_isc_valido_al_valor(self):
        linea = LineaDetalle(
            1, Decimal("10"), UnidadMedida.NIU, "Cigarro ISC", Decimal("5.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA,
            aplica_isc=True, sistema_isc=SistemaIsc.AL_VALOR, tasa_isc=Decimal("0.10"),
        )
        validar_comprobante(_factura(lineas=[linea]))  # no debe lanzar


# ===========================================================================
# Sección 9: Tipos Decimal inválidos (NaN, Infinity)
# ===========================================================================


class TestDecimalInvalidos:
    def test_cantidad_nan_lanza_error(self):
        """Decimal NaN: la comparación con cero en validaciones falla en InvalidOperation."""
        linea = LineaDetalle(1, Decimal("NaN"), UnidadMedida.NIU, "P", Decimal("1.00"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises((ReglaNegocioError, InvalidOperation, ValueError)):
            validar_comprobante(_factura(lineas=[linea]))

    def test_cantidad_infinity_rechazada_en_validacion(self):
        """VAL-007: Infinity debe rechazarse antes de calcular importes."""
        linea = LineaDetalle(
            1,
            Decimal("Infinity"),
            UnidadMedida.NIU,
            "P",
            Decimal("1.00"),
            AfectacionIgv.GRAVADO_OPERACION_ONEROSA
        )

        with pytest.raises(ReglaNegocioError) as exc:
            validar_comprobante(_factura(lineas=[linea]))

        assert exc.value.codigo == "VAL-007"

    def test_precio_nan_lanza_error(self):
        """Decimal NaN en precio: falla en validación o cálculo."""
        linea = LineaDetalle(1, Decimal("1"), UnidadMedida.NIU, "P", Decimal("NaN"), AfectacionIgv.GRAVADO_OPERACION_ONEROSA)
        with pytest.raises((ReglaNegocioError, InvalidOperation, ValueError)):
            validar_comprobante(_factura(lineas=[linea]))
