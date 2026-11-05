from __future__ import annotations

from dataclasses import dataclass

from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.unqualified_data_types_2 import (
    IdentifierType,
)

__NAMESPACE__ = (
    "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2"
)


@dataclass(kw_only=True)
class ReferencedSignatureIdtype(IdentifierType):
    class Meta:
        name = "ReferencedSignatureIDType"


@dataclass(kw_only=True)
class ReferencedSignatureId(ReferencedSignatureIdtype):
    class Meta:
        name = "ReferencedSignatureID"
        namespace = "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2"
