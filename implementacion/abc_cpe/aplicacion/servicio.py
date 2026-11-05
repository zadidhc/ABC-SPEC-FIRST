"""Servicio de aplicación para orquestar la generación y validación XSD de comprobantes."""

import os
from abc_cpe.dominio.modelos import Comprobante, CalculoComprobante
from abc_cpe.dominio.validaciones import validar_comprobante
from abc_cpe.dominio.calculo import calcular_comprobante
from abc_cpe.aplicacion.puertos import GeneradorUblPort, ValidadorXmlPort


class GenerarXmlComprobanteService:
    """Caso de uso de aplicación: Validar reglas -> Calcular -> Generar XML -> Validar XSD."""

    def __init__(
        self,
        generador: GeneradorUblPort,
        validador: ValidadorXmlPort,
        ruta_xsd_invoice: str | None = None,
    ):
        self.generador = generador
        self.validador = validador
        
        # Ruta por defecto al esquema oficial UBL-Invoice-2.1.xsd
        if ruta_xsd_invoice:
            self.ruta_xsd_invoice = ruta_xsd_invoice
        else:
            # Resolución relativa segura respecto al proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.ruta_xsd_invoice = os.path.join(base_dir, "xsd", "maindoc", "UBL-Invoice-2.1.xsd")

    def ejecutar(self, comprobante: Comprobante) -> tuple[str, bytes, CalculoComprobante]:
        """
        Orquesta el flujo integral de generación del comprobante:
        1. Valida reglas de negocio tributarias peruanas (VAL-*).
        2. Ejecuta el motor aritmético decimal para obtener todos los totales y la leyenda 1000.
        3. Invoca al generador UBL basado en clases xsdata.
        4. Valida el XML resultante contra el esquema oficial XSD.
        5. Retorna la tupla (nombre_archivo, xml_bytes, calculo).
        """
        # Paso 1: Validaciones de negocio (RUC, correlativo, coherencia adquirente, etc.)
        validar_comprobante(comprobante)

        # Paso 2: Cálculo aritmético tributario
        calculo = calcular_comprobante(comprobante)

        # Paso 3: Generación UBL a partir de clases de esquema
        _objeto_invoice, xml_bytes = self.generador.generar_invoice(comprobante, calculo)

        # Paso 4: Validación contra el esquema normativo OASIS UBL Invoice XSD
        self.validador.validar(xml_bytes, self.ruta_xsd_invoice)

        # Paso 5: Retorno de artefactos
        nombre_archivo = comprobante.nombre_archivo_xml
        return nombre_archivo, xml_bytes, calculo

