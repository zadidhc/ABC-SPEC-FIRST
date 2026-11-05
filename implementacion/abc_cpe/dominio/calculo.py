"""Motor de cálculo tributario aritmético exacto con Decimal y ROUND_HALF_UP."""

from decimal import Decimal, ROUND_HALF_UP
from abc_cpe.dominio.catalogos import SistemaIsc, AfectacionIgv
from abc_cpe.dominio.errores import ReglaNegocioError
from abc_cpe.dominio.monto_en_letras import monto_en_letras
from abc_cpe.dominio.modelos import (
    Comprobante,
    LineaDetalle,
    CalculoLinea,
    CalculoComprobante,
)

TASA_IGV = Decimal("0.18")
DOS_DECIMALES = Decimal("0.01")


def redondear_2(val: Decimal) -> Decimal:
    """Aplica redondeo aritmético a 2 decimales usando ROUND_HALF_UP."""
    return val.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def calcular_linea(linea: LineaDetalle) -> CalculoLinea:
    """Calcula los impuestos y totales para una línea individual."""
    valor_venta = redondear_2(linea.cantidad * linea.valor_unitario)

    monto_isc = Decimal("0.00")
    if linea.aplica_isc:
        if not linea.afectacion_igv.es_gravada:
            raise ReglaNegocioError("VAL-010", "El ISC solo puede liquidarse en líneas gravadas con IGV.")
        
        if linea.sistema_isc == SistemaIsc.AL_VALOR:
            if linea.tasa_isc is None or linea.tasa_isc <= Decimal("0"):
                raise ReglaNegocioError("VAL-011", "El Sistema 01 de ISC requiere declarar una tasa porcentual positiva.")
            monto_isc = redondear_2(valor_venta * linea.tasa_isc)
        elif linea.sistema_isc == SistemaIsc.ESPECIFICO:
            if linea.monto_fijo_isc is None or linea.monto_fijo_isc <= Decimal("0"):
                raise ReglaNegocioError("VAL-012", "El Sistema 02 de ISC requiere declarar un monto fijo positivo por unidad.")
            monto_isc = redondear_2(linea.cantidad * linea.monto_fijo_isc)
        elif linea.sistema_isc == SistemaIsc.AL_PVP:
            # Fórmula de cálculo sujeta a confirmación en referencias (PENDIENTE DE VERIFICACIÓN)
            if linea.pvp_isc is None or linea.tasa_isc is None:
                raise ReglaNegocioError("VAL-013", "El Sistema 03 de ISC requiere declarar PVP y tasa porcentual.")
            monto_isc = redondear_2(linea.cantidad * linea.pvp_isc * linea.tasa_isc)
        else:
            raise ReglaNegocioError("VAL-014", "Línea con ISC activo sin sistema de cálculo especificado.")

    # El ISC forma parte de la base imponible del IGV
    if linea.afectacion_igv.es_gravada:
        base_igv = valor_venta + monto_isc
        monto_igv = redondear_2(base_igv * TASA_IGV)
    else:
        base_igv = Decimal("0.00")
        monto_igv = Decimal("0.00")

    total_linea = valor_venta + monto_isc + monto_igv
    # Precio unitario con impuestos (puede tener hasta 10 decimales, mínimo 2)
    precio_unitario_con_impuestos = total_linea / linea.cantidad

    return CalculoLinea(
        linea=linea,
        valor_venta=valor_venta,
        monto_isc=monto_isc,
        base_igv=base_igv,
        monto_igv=monto_igv,
        total_linea=total_linea,
        precio_unitario_con_impuestos=precio_unitario_con_impuestos,
    )


def calcular_comprobante(comprobante: Comprobante) -> CalculoComprobante:
    """Calcula y totaliza todos los impuestos e importes del comprobante."""
    if not comprobante.lineas:
        raise ReglaNegocioError("VAL-006", "El comprobante debe contener al menos una línea de detalle.")

    lineas_calculadas = [calcular_linea(l) for l in comprobante.lineas]

    total_gravadas = Decimal("0.00")
    total_exoneradas = Decimal("0.00")
    total_inafectas = Decimal("0.00")
    base_isc = Decimal("0.00")
    total_isc = Decimal("0.00")
    total_igv = Decimal("0.00")

    for cl in lineas_calculadas:
        if cl.linea.afectacion_igv.es_gravada:
            total_gravadas += cl.valor_venta
        elif cl.linea.afectacion_igv.es_exonerada:
            total_exoneradas += cl.valor_venta
        elif cl.linea.afectacion_igv.es_inafecta:
            total_inafectas += cl.valor_venta

        # REGLA OBLIGATORIA: base_isc = suma del valor_venta exclusivamente de las líneas que tienen ISC
        if cl.linea.aplica_isc:
            base_isc += cl.valor_venta
            total_isc += cl.monto_isc

        total_igv += cl.monto_igv

    base_igv = total_gravadas + total_isc
    total_valor_venta = total_gravadas + total_exoneradas + total_inafectas
    total_con_impuestos = total_valor_venta + total_isc + total_igv
    importe_total = total_con_impuestos

    # Invariante tributario: el importe total debe igualar la suma exacta de las líneas
    suma_lineas = sum((cl.total_linea for cl in lineas_calculadas), Decimal("0.00"))
    if importe_total != suma_lineas:
        raise ReglaNegocioError(
            "VAL-002",
            f"El importe total ({importe_total}) no coincide con la suma de líneas ({suma_lineas})."
        )

    texto_letras = monto_en_letras(importe_total, comprobante.moneda)

    return CalculoComprobante(
        lineas_calculadas=lineas_calculadas,
        total_gravadas=redondear_2(total_gravadas),
        total_exoneradas=redondear_2(total_exoneradas),
        total_inafectas=redondear_2(total_inafectas),
        base_isc=redondear_2(base_isc),
        total_isc=redondear_2(total_isc),
        base_igv=redondear_2(base_igv),
        total_igv=redondear_2(total_igv),
        total_valor_venta=redondear_2(total_valor_venta),
        total_con_impuestos=redondear_2(total_con_impuestos),
        importe_total=redondear_2(importe_total),
        monto_en_letras=texto_letras,
    )

