from __future__ import annotations

from dataclasses import dataclass, field

from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.common_basic_components_2 import (
    Id,
)
from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.signature_basic_components_2 import (
    ReferencedSignatureId,
)
from abc_cpe.ubl_generado.org.w3.pkg_2000.pkg_09.xmldsig import Signature

__NAMESPACE__ = "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2"


@dataclass(kw_only=True)
class SignatureInformationType:
    """
    :ivar id:
    :ivar referenced_signature_id:
    :ivar signature: This is a single digital signature as defined by
        the W3C specification.
    """

    id: None | Id = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Element",
            "namespace": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        },
    )
    referenced_signature_id: None | ReferencedSignatureId = field(
        default=None,
        metadata={
            "name": "ReferencedSignatureID",
            "type": "Element",
            "namespace": "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2",
        },
    )
    signature: None | Signature = field(
        default=None,
        metadata={
            "name": "Signature",
            "type": "Element",
            "namespace": "http://www.w3.org/2000/09/xmldsig#",
        },
    )


@dataclass(kw_only=True)
class SignatureInformation(SignatureInformationType):
    class Meta:
        namespace = "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2"
