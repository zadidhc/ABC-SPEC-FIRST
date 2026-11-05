"""Puertos de salida (interfaces desacopladas SPI) de la capa de aplicación."""

from abc import ABC, abstractmethod
from typing import Any
from abc_cpe.dominio.modelos import Comprobante, CalculoComprobante


class GeneradorUblPort(ABC):
    """Puerto para la construcción y serialización del XML OASIS UBL 2.1."""

    @abstractmethod
    def generar_invoice(
        self, comprobante: Comprobante, calculo: CalculoComprobante
    ) -> tuple[Any, bytes]:
        """
        Instancia las clases generadas por xsdata y produce los bytes XML del comprobante.
        Retorna (objeto_invoice_generado, xml_bytes).
        """
        pass


class ValidadorXmlPort(ABC):
    """Puerto para la validación estricta de esquemas XSD contra XML generado."""

    @abstractmethod
    def validar(self, xml_bytes: bytes, ruta_xsd: str) -> None:
        """
        Valida el documento XML frente al esquema XSD especificado.
        Lanza XmlInvalidoError si el XML no satisface la gramática o cardinalidad XSD.
        """
        pass

