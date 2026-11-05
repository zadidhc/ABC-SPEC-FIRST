"""Definición de errores y excepciones del dominio de facturación electrónica."""

class DominioError(Exception):
    """Excepción base para errores de negocio y dominio."""
    pass


class ReglaNegocioError(DominioError):
    """Infracción de una regla de negocio tributaria o validación funcional (VAL-*)."""
    def __init__(self, codigo: str, mensaje: str):
        super().__init__(f"[{codigo}] {mensaje}")
        self.codigo = codigo
        self.mensaje = mensaje


class XmlInvalidoError(DominioError):
    """Error al validar la estructura XML generada contra los esquemas XSD oficiales."""
    def __init__(self, mensaje: str, errores: list[str] | None = None):
        super().__init__(mensaje)
        self.errores = errores or []

