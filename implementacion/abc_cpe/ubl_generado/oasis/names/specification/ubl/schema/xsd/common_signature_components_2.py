from __future__ import annotations

from dataclasses import dataclass, field

from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.signature_aggregate_components_2 import (
    SignatureInformation,
)

__NAMESPACE__ = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2"
)


@dataclass(kw_only=True)
class UbldocumentSignaturesType:
    class Meta:
        name = "UBLDocumentSignaturesType"

    signature_information: list[SignatureInformation] = field(
        default_factory=list,
        metadata={
            "name": "SignatureInformation",
            "type": "Element",
            "namespace": "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class UbldocumentSignatures(UbldocumentSignaturesType):
    class Meta:
        name = "UBLDocumentSignatures"
        namespace = "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2"
