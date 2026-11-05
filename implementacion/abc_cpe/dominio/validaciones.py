"""Validaciones de reglas de negocio tributarias del dominio (VAL-*)."""

import re
from datetime import date
from decimal import Decimal
from abc_cpe.dominio.catalogos import TipoComprobante, TipoDocumentoIdentidad, SistemaIsc
from abc_cpe.dominio.errores import ReglaNegocioError
from abc_cpe.dominio.modelos import Comprobante, LineaDetalle

PESOS_RUC = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
PREFIJOS_RUC_VALIDOS = ("10", "15", "16", "17", "20")


def validar_ruc(ruc: str) -> bool:
    """
    Valida un RUC peruano según las reglas oficiales de SUNAT:
    1. Exactamente 11 dígitos numéricos.
    2. Comienza con los prefijos autorizados: 10, 15, 16, 17 o 20.
    3. Dígito verificador coincide con el algoritmo Módulo 11 ponderado.
    """
    if not isinstance(ruc, str) or len(ruc) != 11 or not ruc.isdigit():
        return False

    if not ruc.startswith(PREFIJOS_RUC_VALIDOS):
        return False

    suma = sum(int(digito) * peso for digito, peso in zip(ruc[:10], PESOS_RUC))
    resto = suma % 11
    digito_verificador = 11 - resto

    if digito_verificador == 10:
        digito_verificador = 0
    elif digito_verificador == 11:
        digito_verificador = 1

    return digito_verificador == int(ruc[10])


def validar_dni(dni: str) -> bool:
    """Valida que el DNI contenga exactamente 8 dígitos numéricos."""
    return isinstance(dni, str) and len(dni) == 8 and dni.isdigit()


def validar_serie_comprobante(tipo: TipoComprobante, serie: str) -> bool:
    """Valida la serie: ^F[A-Z0-9]{3}$ para Facturas y ^B[A-Z0-9]{3}$ para Boletas."""
    if not isinstance(serie, str) or len(serie) != 4:
        return False
    
    if tipo == TipoComprobante.FACTURA:
        return bool(re.match(r"^F[A-Z0-9]{3}$", serie))
    elif tipo == TipoComprobante.BOLETA:
        return bool(re.match(r"^B[A-Z0-9]{3}$", serie))
    return False


def validar_comprobante(comprobante: Comprobante) -> None:
    """
    Ejecuta todas las validaciones previas de reglas de negocio tributarias.
    Lanza ReglaNegocioError con código VAL-* si alguna regla es vulnerada.
    """
    # VAL-001: RUC del emisor válido
    if not validar_ruc(comprobante.emisor.ruc):
        raise ReglaNegocioError(
            "VAL-001",
            f"El RUC del emisor '{comprobante.emisor.ruc}' es inválido (falla Módulo 11 o prefijo no autorizado)."
        )

    # VAL-002: Serie según tipo de comprobante
    if not validar_serie_comprobante(comprobante.tipo_comprobante, comprobante.serie):
        esperado = "iniciar con 'F'" if comprobante.tipo_comprobante == TipoComprobante.FACTURA else "iniciar con 'B'"
        raise ReglaNegocioError(
            "VAL-002",
            f"Serie '{comprobante.serie}' inválida para {comprobante.tipo_comprobante.name}. Debe tener 4 caracteres y {esperado}."
        )

    # VAL-003: Correlativo numérico entre 1 y 99,999,999
    if not isinstance(comprobante.correlativo, int) or comprobante.correlativo < 1 or comprobante.correlativo > 99_999_999:
        raise ReglaNegocioError(
            "VAL-003",
            f"Correlativo '{comprobante.correlativo}' fuera de rango. Debe ser un entero entre 1 y 99,999,999."
        )

    # VAL-004: Coherencia de identificación del cliente
    if comprobante.tipo_comprobante == TipoComprobante.FACTURA:
        if comprobante.cliente.tipo_documento != TipoDocumentoIdentidad.RUC:
            raise ReglaNegocioError(
                "VAL-004",
                "Las facturas ('01') requieren obligatoriamente adquirente con RUC (Catálogo 06 código 6)."
            )
        if not validar_ruc(comprobante.cliente.numero_documento):
            raise ReglaNegocioError(
                "VAL-004",
                f"El RUC del cliente '{comprobante.cliente.numero_documento}' no satisface el algoritmo Módulo 11."
            )
    elif comprobante.tipo_comprobante == TipoComprobante.BOLETA:
        if comprobante.cliente.tipo_documento == TipoDocumentoIdentidad.DNI:
            if not validar_dni(comprobante.cliente.numero_documento):
                raise ReglaNegocioError(
                    "VAL-004",
                    f"El DNI del cliente '{comprobante.cliente.numero_documento}' debe contener exactamente 8 dígitos."
                )
        elif comprobante.cliente.tipo_documento == TipoDocumentoIdentidad.RUC:
            if not validar_ruc(comprobante.cliente.numero_documento):
                raise ReglaNegocioError(
                    "VAL-004",
                    f"El RUC del cliente '{comprobante.cliente.numero_documento}' en la boleta es inválido."
                )

    # VAL-005: Fecha de vencimiento mayor o igual a fecha de emisión
    if comprobante.fecha_vencimiento is not None:
        if comprobante.fecha_vencimiento < comprobante.fecha_emision:
            raise ReglaNegocioError(
                "VAL-005",
                f"La fecha de vencimiento ({comprobante.fecha_vencimiento}) no puede ser anterior a la de emisión ({comprobante.fecha_emision})."
            )

    # VAL-006: Al menos una línea de detalle
    if not comprobante.lineas:
        raise ReglaNegocioError(
            "VAL-006",
            "El comprobante debe incluir al menos una línea de detalle."
        )

    # Validaciones a nivel de cada línea
    numeros_orden = set()
    for idx, linea in enumerate(comprobante.lineas, start=1):
         # VAL-015: Identificador de línea válido y único
        if (
            type(linea.numero_orden) is not int
            or linea.numero_orden <= 0
            or linea.numero_orden in numeros_orden
        ):
            raise ReglaNegocioError(
                "VAL-015",
                f"Línea #{idx}: el número de orden debe ser "
                "un entero positivo y no repetido."
            )

        numeros_orden.add(linea.numero_orden)
        # VAL-007: Cantidad mayor a cero
        if (
                not isinstance(linea.cantidad, Decimal)
                or not linea.cantidad.is_finite()
                or linea.cantidad <= Decimal("0")
            ):
            raise ReglaNegocioError(
                "VAL-007",
                f"Línea #{idx}: La cantidad ({linea.cantidad}) debe ser estrictamente mayor a 0."
            )

        # VAL-008: Valor unitario no negativo
        if (
                not isinstance(linea.valor_unitario, Decimal)
                or not linea.valor_unitario.is_finite()
                or linea.valor_unitario < Decimal("0")
            ):
            raise ReglaNegocioError(
                "VAL-008",
                f"Línea #{idx}: El valor unitario ({linea.valor_unitario}) no puede ser negativo."
            )

        # VAL-009: Descripción no vacía
        if not linea.descripcion or not linea.descripcion.strip():
            raise ReglaNegocioError(
                "VAL-009",
                f"Línea #{idx}: La descripción del ítem no puede estar vacía."
            )

        # VAL-010..014: Reglas de ISC
        if linea.aplica_isc:
            if not linea.afectacion_igv.es_gravada:
                raise ReglaNegocioError(
                    "VAL-010",
                    f"Línea #{idx}: El ISC solo puede asociarse a operaciones gravadas con IGV."
                )
            if linea.sistema_isc == SistemaIsc.AL_VALOR:
                if linea.tasa_isc is None or linea.tasa_isc <= Decimal("0"):
                    raise ReglaNegocioError(
                        "VAL-011",
                        f"Línea #{idx}: El Sistema 01 de ISC requiere una tasa porcentual positiva."
                    )
            elif linea.sistema_isc == SistemaIsc.ESPECIFICO:
                if linea.monto_fijo_isc is None or linea.monto_fijo_isc <= Decimal("0"):
                    raise ReglaNegocioError(
                        "VAL-012",
                        f"Línea #{idx}: El Sistema 02 de ISC requiere un monto fijo unitario positivo."
                    )
            elif linea.sistema_isc == SistemaIsc.AL_PVP:
                if linea.pvp_isc is None or linea.pvp_isc <= Decimal("0") or linea.tasa_isc is None or linea.tasa_isc <= Decimal("0"):
                    raise ReglaNegocioError(
                        "VAL-013",
                        f"Línea #{idx}: El Sistema 03 de ISC requiere PVP y tasa porcentual positivos."
                    )
            elif linea.sistema_isc is None:
                raise ReglaNegocioError(
                    "VAL-014",
                    f"Línea #{idx}: Línea con ISC activo pero sin sistema de cálculo tipificado."
                )

