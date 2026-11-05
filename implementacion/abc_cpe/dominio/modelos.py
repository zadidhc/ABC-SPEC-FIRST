"""Modelos de datos del dominio puro de comprobantes de pago electrónicos."""

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal
from abc_cpe.dominio.catalogos import (
    TipoComprobante,
    TipoDocumentoIdentidad,
    AfectacionIgv,
    SistemaIsc,
    Moneda,
    UnidadMedida,
)


@dataclass(frozen=True)
class Emisor:
    """Información fiscal de la empresa emisora (ABC Software Corp)."""
    ruc: str
    razon_social: str
    nombre_comercial: str | None
    ubigeo: str
    direccion: str
    departamento: str
    provincia: str
    distrito: str
    codigo_pais: str = "PE"


@dataclass(frozen=True)
class Cliente:
    """Información del adquirente / cliente."""
    tipo_documento: TipoDocumentoIdentidad
    numero_documento: str
    razon_social: str
    direccion: str | None = None
    email: str | None = None


@dataclass(frozen=True)
class LineaDetalle:
    """Línea de ítem de venta del comprobante."""
    numero_orden: int
    cantidad: Decimal
    unidad_medida: UnidadMedida
    descripcion: str
    valor_unitario: Decimal  # Valor de venta unitario sin tributos
    afectacion_igv: AfectacionIgv
    aplica_isc: bool = False
    sistema_isc: SistemaIsc | None = None
    tasa_isc: Decimal | None = None        # Tasa porcentual para sistemas 01 y 03 (ej. Decimal('0.10'))
    monto_fijo_isc: Decimal | None = None  # Monto fijo unitario para sistema 02 (ej. Decimal('1.50'))
    pvp_isc: Decimal | None = None         # Precio de venta al público para sistema 03
    codigo_producto: str | None = None


@dataclass(frozen=True)
class CalculoLinea:
    """Valores tributarios calculados de una línea individual."""
    linea: LineaDetalle
    valor_venta: Decimal
    monto_isc: Decimal
    base_igv: Decimal
    monto_igv: Decimal
    total_linea: Decimal
    precio_unitario_con_impuestos: Decimal


@dataclass(frozen=True)
class CalculoComprobante:
    """Consolidación de totales tributarios de todo el comprobante."""
    lineas_calculadas: list[CalculoLinea]
    total_gravadas: Decimal
    total_exoneradas: Decimal
    total_inafectas: Decimal
    base_isc: Decimal          # Suma de valor_venta de líneas con ISC exclusivamente
    total_isc: Decimal
    base_igv: Decimal          # total_gravadas + total_isc
    total_igv: Decimal
    total_valor_venta: Decimal # total_gravadas + total_exoneradas + total_inafectas
    total_con_impuestos: Decimal
    importe_total: Decimal
    monto_en_letras: str


@dataclass
class Comprobante:
    """Entidad principal que representa un comprobante electrónico (Factura o Boleta)."""
    tipo_comprobante: TipoComprobante
    serie: str
    correlativo: int
    fecha_emision: date
    hora_emision: time
    moneda: Moneda
    emisor: Emisor
    cliente: Cliente
    lineas: list[LineaDetalle] = field(default_factory=list)
    fecha_vencimiento: date | None = None
    tipo_operacion: str = "0101"
    forma_pago: str = "Contado"

    @property
    def numero_comprobante(self) -> str:
        """Identificador cbc:ID = serie-correlativo sin ceros a la izquierda."""
        return f"{self.serie}-{self.correlativo}"

    @property
    def nombre_archivo_xml(self) -> str:
        """Nombre normativo del archivo XML: {RUC}-{tipo}-{serie}-{correlativo}.xml"""
        return f"{self.emisor.ruc}-{self.tipo_comprobante.value}-{self.serie}-{self.correlativo}.xml"

