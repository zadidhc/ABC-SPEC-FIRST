"""Adaptador de validación de esquemas XSD basado en lxml."""

import os
from lxml import etree
from abc_cpe.aplicacion.puertos import ValidadorXmlPort
from abc_cpe.dominio.errores import XmlInvalidoError


class ValidadorXsdLxml(ValidadorXmlPort):
    """Adaptador que valida documentos XML contra esquemas normativos XSD oficiales."""

    def __init__(self, ruta_xsd_defecto: str | None = None):
        self._cache_esquemas: dict[str, etree.XMLSchema] = {}
        if ruta_xsd_defecto:
            self._obtener_esquema(ruta_xsd_defecto)

    def _obtener_esquema(self, ruta_xsd: str) -> etree.XMLSchema:
        if ruta_xsd not in self._cache_esquemas:
            if not os.path.exists(ruta_xsd):
                raise FileNotFoundError(f"Archivo de esquema XSD no encontrado en: {ruta_xsd}")
            doc_xsd = etree.parse(ruta_xsd)
            self._cache_esquemas[ruta_xsd] = etree.XMLSchema(doc_xsd)
        return self._cache_esquemas[ruta_xsd]

    def validar(self, xml_bytes: bytes, ruta_xsd: str) -> None:
        """
        Parsea y valida el documento XML en memoria contra el esquema XSD.
        Si la sintaxis o la estructura no cumplen, lanza XmlInvalidoError con el detalle de errores.
        """
        try:
            doc_xml = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as exc:
            raise XmlInvalidoError(f"Error de sintaxis XML (mal formado): {exc}", [str(exc)])

        esquema = self._obtener_esquema(ruta_xsd)
        if not esquema.validate(doc_xml):
            errores = [
                f"Línea {err.line}, col {err.column}: {err.message}"
                for err in esquema.error_log
            ]
            detalle = "\n".join(errores)
            raise XmlInvalidoError(
                f"El documento XML no cumple con el esquema XSD oficial OASIS UBL 2.1:\n{detalle}",
                errores,
            )

