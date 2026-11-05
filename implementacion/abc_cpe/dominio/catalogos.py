"""Catálogos normativos oficiales de SUNAT para comprobantes de pago electrónicos."""

from enum import Enum


class TipoComprobante(str, Enum):
    """Catálogo 01 - Tipo de documento electrónico."""
    FACTURA = "01"
    BOLETA = "03"


class TipoDocumentoIdentidad(str, Enum):
    """Catálogo 06 - Tipo de documento de identidad."""
    SIN_DOCUMENTO = "0"
    DNI = "1"
    CARNET_EXTRANJERIA = "4"
    RUC = "6"
    PASAPORTE = "7"


class AfectacionIgv(str, Enum):
    """Catálogo 07 - Afectación al IGV."""
    GRAVADO_OPERACION_ONEROSA = "10"
    EXONERADO_OPERACION_ONEROSA = "20"
    INAFECTO_OPERACION_ONEROSA = "30"

    @property
    def es_gravada(self) -> bool:
        return self == AfectacionIgv.GRAVADO_OPERACION_ONEROSA

    @property
    def es_exonerada(self) -> bool:
        return self == AfectacionIgv.EXONERADO_OPERACION_ONEROSA

    @property
    def es_inafecta(self) -> bool:
        return self == AfectacionIgv.INAFECTO_OPERACION_ONEROSA


class SistemaIsc(str, Enum):
    """Catálogo 08 - Sistema de cálculo del Impuesto Selectivo al Consumo."""
    AL_VALOR = "01"
    ESPECIFICO = "02"
    AL_PVP = "03"  # Sistema al Precio de Venta al Público (Fórmula: PENDIENTE DE VERIFICACIÓN)


class Moneda(str, Enum):
    """Catálogo 02 - Tipo de Moneda."""
    PEN = "PEN"
    USD = "USD"


class UnidadMedida(str, Enum):
    """Subconjunto de Catálogo 03 - Unidades de medida comerciales."""
    NIU = "NIU"  # Unidad (Bienes)
    ZZ = "ZZ"    # Servicio
    KGM = "KGM"  # Kilogramos
    GRM = "GRM"  # Gramos
    TNE = "TNE"  # Toneladas
    LTR = "LTR"  # Litros
    MLT = "MLT"  # Mililitros
    GLL = "GLL"  # Galones
    BX = "BX"    # Caja
    PK = "PK"    # Paquete
    BG = "BG"    # Bolsa
    BO = "BO"    # Botella
    DZN = "DZN"  # Docena
    MTR = "MTR"  # Metros


class Tributo(Enum):
    """Catálogo 05 - Tipos de Tributos."""
    IGV = ("1000", "IGV", "VAT", "S")
    ISC = ("2000", "ISC", "EXC", "S")
    EXO = ("9997", "EXO", "VAT", "E")
    INA = ("9998", "INA", "FRE", "O")

    def __init__(self, codigo: str, nombre: str, tipo_codigo: str, categoria: str):
        self.codigo = codigo
        self.nombre = nombre
        self.tipo_codigo = tipo_codigo
        self.categoria = categoria

