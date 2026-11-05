"""Adaptador de infraestructura que genera documentos XML OASIS UBL 2.1 usando clases xsdata."""

from decimal import Decimal, ROUND_HALF_UP
from xsdata.models.datatype import XmlDate, XmlTime
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from abc_cpe.aplicacion.puertos import GeneradorUblPort
from abc_cpe.dominio.modelos import Comprobante, CalculoComprobante, CalculoLinea
from abc_cpe.dominio.catalogos import Moneda, SistemaIsc

# Clases generadas desde los esquemas normativos oficiales OASIS UBL 2.1 XSD
from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.invoice_2 import Invoice
from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.common_basic_components_2 import (
    UblversionId,
    CustomizationId,
    Id,
    IssueDate,
    IssueTime,
    DueDate,
    InvoiceTypeCode,
    Note,
    DocumentCurrencyCode,
    LineCountNumeric,
    PriceAmount,
    PriceTypeCode,
    TaxAmount,
    TaxableAmount,
    Percent,
    PerUnitAmount,
    TierRange,
    TaxExemptionReasonCode,
    LineExtensionAmount,
    TaxInclusiveAmount,
    PayableAmount,
    InvoicedQuantity,
    Description,
    Name,
    RegistrationName,
    AddressTypeCode,
    CityName,
    CountrySubentity,
    District,
    Line,
    IdentificationCode,
    TaxTypeCode,
    PaymentMeansId,
    Uri,
)
from abc_cpe.ubl_generado.oasis.names.specification.ubl.schema.xsd.common_aggregate_components_2 import (
    Address,
    Signature,
    SignatoryParty,
    DigitalSignatureAttachment,
    ExternalReference,
    AccountingSupplierParty,
    AccountingCustomerParty,
    Party,
    PartyIdentification,
    PartyName,
    PartyLegalEntity,
    RegistrationAddress,
    AddressLine,
    Country,
    PaymentTerms,
    TaxTotal,
    TaxSubtotal,
    TaxCategory,
    TaxScheme,
    LegalMonetaryTotal,
    InvoiceLine,
    Item,
    Price,
    PricingReference,
    AlternativeConditionPrice,
    SellersItemIdentification,
)


class GeneradorUblAdapter(GeneradorUblPort):
    """
    Construye e instancia clases Python autogeneradas a partir del esquema oficial
    OASIS UBL-Invoice-2.1.xsd y las serializa a XML estándar sin usar plantillas de texto.
    """

    def __init__(self):
        self.config = SerializerConfig(
            indent="  ",
            xml_declaration=True,
            encoding="UTF-8",
        )
        self.ns_map = {
            None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        }
        self.serializer = XmlSerializer(config=self.config)

    def generar_invoice(
        self, comprobante: Comprobante, calculo: CalculoComprobante
    ) -> tuple[Invoice, bytes]:
        """Construye la entidad Invoice fuertemente tipada y la serializa a XML en bytes."""
        moneda_cod = comprobante.moneda.value

        # 1. Cabecera del comprobante
        # Importante: cbc:ID es serie-correlativo sin ceros a la izquierda
        id_comprobante = comprobante.numero_comprobante

        fecha_emision = XmlDate.from_date(comprobante.fecha_emision)
        hora_emision = XmlTime.from_time(comprobante.hora_emision)
        fecha_vencimiento = (
            XmlDate.from_date(comprobante.fecha_vencimiento)
            if comprobante.fecha_vencimiento
            else None
        )

        tipo_comprobante_elem = InvoiceTypeCode(
            value=comprobante.tipo_comprobante.value,
            list_id=comprobante.tipo_operacion,
            name="Tipo de Operacion",
            list_agency_name="PE:SUNAT",
            list_name="Tipo de Documento",
            list_uri="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01",
        )

        # 2. Firma del comprobante
        sig_id = f"SIGN-{comprobante.emisor.ruc}"
        firma_elem = Signature(
            id=Id(value=sig_id),
            signatory_party=SignatoryParty(
                party_identification=[
                    PartyIdentification(id=Id(value=comprobante.emisor.ruc))
                ],
                party_name=[PartyName(name=Name(value=comprobante.emisor.razon_social))],
            ),
            digital_signature_attachment=DigitalSignatureAttachment(
                external_reference=ExternalReference(uri=Uri(value=f"#{sig_id}"))
            ),
        )

        # 3. Emisor (Supplier)
        direccion_emisor = RegistrationAddress(
            id=Id(value=comprobante.emisor.ubigeo),
            address_type_code=AddressTypeCode(value="0000"),
            city_name=CityName(value=comprobante.emisor.departamento),
            country_subentity=CountrySubentity(value=comprobante.emisor.provincia),
            district=District(value=comprobante.emisor.distrito),
            address_line=[AddressLine(line=Line(value=comprobante.emisor.direccion))],
            country=Country(
                identification_code=IdentificationCode(value=comprobante.emisor.codigo_pais)
            ),
        )

        nombre_comercial = comprobante.emisor.nombre_comercial or comprobante.emisor.razon_social
        supplier_party = AccountingSupplierParty(
            party=Party(
                party_identification=[
                    PartyIdentification(
                        id=Id(value=comprobante.emisor.ruc, scheme_id="6")
                    )
                ],
                party_name=[PartyName(name=Name(value=nombre_comercial))],
                party_legal_entity=[
                    PartyLegalEntity(
                        registration_name=RegistrationName(
                            value=comprobante.emisor.razon_social
                        ),
                        registration_address=direccion_emisor,
                    )
                ],
            )
        )

        # 4. Adquirente / Cliente (Customer)
        customer_party = AccountingCustomerParty(
            party=Party(
                party_identification=[
                    PartyIdentification(
                        id=Id(
                            value=comprobante.cliente.numero_documento,
                            scheme_id=comprobante.cliente.tipo_documento.value,
                        )
                    )
                ],
                party_legal_entity=[
                    PartyLegalEntity(
                        registration_name=RegistrationName(
                            value=comprobante.cliente.razon_social
                        )
                    )
                ],
            )
        )

        # 5. Condiciones de pago
        payment_terms = [
            PaymentTerms(
                id=Id(value="FormaPago"),
                payment_means_id=[PaymentMeansId(value=comprobante.forma_pago)],
            )
        ]

        # 6. Desglose de impuestos globales del documento (TaxTotal)
        total_tributos = calculo.total_isc + calculo.total_igv
        subtotales_doc: list[TaxSubtotal] = []

        # Subtotal IGV (Gravado 1000)
        if calculo.total_igv > Decimal("0.00") or calculo.total_gravadas > Decimal("0.00"):
            subtotales_doc.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=calculo.base_igv, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=calculo.total_igv, currency_id=moneda_cod
                    ),
                    tax_category=TaxCategory(
                        id=Id(value="S"),
                        percent=Percent(value=Decimal("18.00")),
                        tax_scheme=TaxScheme(
                            id=Id(value="1000"),
                            name=Name(value="IGV"),
                            tax_type_code=TaxTypeCode(value="VAT"),
                        ),
                    ),
                )
            )

        # Subtotal ISC (2000) - Base imponible = base_isc exclusivamente
        if calculo.total_isc > Decimal("0.00") or calculo.base_isc > Decimal("0.00"):
            subtotales_doc.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=calculo.base_isc, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=calculo.total_isc, currency_id=moneda_cod
                    ),
                    tax_category=TaxCategory(
                        id=Id(value="S"),
                        tax_scheme=TaxScheme(
                            id=Id(value="2000"),
                            name=Name(value="ISC"),
                            tax_type_code=TaxTypeCode(value="EXC"),
                        ),
                    ),
                )
            )

        # Subtotal Exonerado (9997)
        if calculo.total_exoneradas > Decimal("0.00"):
            subtotales_doc.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=calculo.total_exoneradas, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=Decimal("0.00"), currency_id=moneda_cod
                    ),
                    tax_category=TaxCategory(
                        id=Id(value="E"),
                        percent=Percent(value=Decimal("0.00")),
                        tax_scheme=TaxScheme(
                            id=Id(value="9997"),
                            name=Name(value="EXO"),
                            tax_type_code=TaxTypeCode(value="VAT"),
                        ),
                    ),
                )
            )

        # Subtotal Inafecto (9998)
        if calculo.total_inafectas > Decimal("0.00"):
            subtotales_doc.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=calculo.total_inafectas, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=Decimal("0.00"), currency_id=moneda_cod
                    ),
                    tax_category=TaxCategory(
                        id=Id(value="O"),
                        percent=Percent(value=Decimal("0.00")),
                        tax_scheme=TaxScheme(
                            id=Id(value="9998"),
                            name=Name(value="INA"),
                            tax_type_code=TaxTypeCode(value="FRE"),
                        ),
                    ),
                )
            )

        doc_tax_total = TaxTotal(
            tax_amount=TaxAmount(value=total_tributos, currency_id=moneda_cod),
            tax_subtotal=subtotales_doc,
        )

        # 7. Totales monetarios del documento (LegalMonetaryTotal)
        legal_monetary_total = LegalMonetaryTotal(
            line_extension_amount=LineExtensionAmount(
                value=calculo.total_valor_venta, currency_id=moneda_cod
            ),
            tax_inclusive_amount=TaxInclusiveAmount(
                value=calculo.total_con_impuestos, currency_id=moneda_cod
            ),
            payable_amount=PayableAmount(
                value=calculo.importe_total, currency_id=moneda_cod
            ),
        )

        # 8. Líneas de detalle del comprobante (InvoiceLine)
        invoice_lines: list[InvoiceLine] = []
        for cl in calculo.lineas_calculadas:
            inv_line = self._construir_linea(cl, moneda_cod)
            invoice_lines.append(inv_line)

        # Construcción de la instancia Invoice UBL 2.1
        # NOTA MANDATORIA B4: ublextensions NO debe emitirse vacío porque XSD rechaza ExtensionContent vacío
        invoice_obj = Invoice(
            ublextensions=None,
            ublversion_id=UblversionId(value="2.1"),
            customization_id=CustomizationId(value="2.0"),
            id=Id(value=id_comprobante),
            issue_date=IssueDate(value=fecha_emision),
            issue_time=IssueTime(value=hora_emision),
            due_date=DueDate(value=fecha_vencimiento) if fecha_vencimiento else None,
            invoice_type_code=tipo_comprobante_elem,
            note=[Note(value=calculo.monto_en_letras, language_locale_id="1000")],
            document_currency_code=DocumentCurrencyCode(value=moneda_cod),
            line_count_numeric=LineCountNumeric(value=Decimal(len(comprobante.lineas))),
            signature=[firma_elem],
            accounting_supplier_party=supplier_party,
            accounting_customer_party=customer_party,
            payment_terms=payment_terms,
            tax_total=[doc_tax_total],
            legal_monetary_total=legal_monetary_total,
            invoice_line=invoice_lines,
        )

        xml_string = self.serializer.render(invoice_obj, ns_map=self.ns_map)
        xml_bytes = xml_string.encode("utf-8")
        return invoice_obj, xml_bytes

    def _construir_linea(self, cl: CalculoLinea, moneda_cod: str) -> InvoiceLine:
        """Construye una instancia de InvoiceLine apegada a la secuencia XSD."""
        linea = cl.linea

        # Precio unitario con impuestos (Catálogo 16 código 01)
        # Formateo con hasta 10 decimales si tiene fracción extensa
        pu_val = cl.precio_unitario_con_impuestos
        if pu_val == pu_val.quantize(Decimal("0.01")):
            pu_val = pu_val.quantize(Decimal("0.01"))
        else:
            pu_val = pu_val.quantize(Decimal("0.0000000001")).normalize()

        pricing_ref = PricingReference(
            alternative_condition_price=[
                AlternativeConditionPrice(
                    price_amount=PriceAmount(value=pu_val, currency_id=moneda_cod),
                    price_type_code=PriceTypeCode(value="01"),
                )
            ]
        )

        subtotales_linea: list[TaxSubtotal] = []

        # Si la línea tiene ISC: subtotal ISC primero con TierRange
        if linea.aplica_isc and linea.sistema_isc:
            tier_range_elem = TierRange(value=linea.sistema_isc.value)
            percent_elem = (
                Percent(value=linea.tasa_isc * Decimal("100"))
                if linea.tasa_isc is not None
                else None
            )
            per_unit_elem = (
                PerUnitAmount(value=linea.monto_fijo_isc, currency_id=moneda_cod)
                if linea.monto_fijo_isc is not None
                else None
            )

            cat_isc = TaxCategory(
                id=Id(value="S"),
                percent=percent_elem,
                per_unit_amount=per_unit_elem,
                tier_range=tier_range_elem,
                tax_scheme=TaxScheme(
                    id=Id(value="2000"),
                    name=Name(value="ISC"),
                    tax_type_code=TaxTypeCode(value="EXC"),
                ),
            )
            subtotales_linea.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=cl.valor_venta, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=cl.monto_isc, currency_id=moneda_cod
                    ),
                    tax_category=cat_isc,
                )
            )

        # Subtotal IGV / EXO / INA de la línea
        if linea.afectacion_igv.es_gravada:
            cat_igv = TaxCategory(
                id=Id(value="S"),
                percent=Percent(value=Decimal("18.00")),
                tax_exemption_reason_code=TaxExemptionReasonCode(
                    value=linea.afectacion_igv.value
                ),
                tax_scheme=TaxScheme(
                    id=Id(value="1000"),
                    name=Name(value="IGV"),
                    tax_type_code=TaxTypeCode(value="VAT"),
                ),
            )
            subtotales_linea.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=cl.base_igv, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=cl.monto_igv, currency_id=moneda_cod
                    ),
                    tax_category=cat_igv,
                )
            )
        elif linea.afectacion_igv.es_exonerada:
            cat_exo = TaxCategory(
                id=Id(value="E"),
                percent=Percent(value=Decimal("0.00")),
                tax_exemption_reason_code=TaxExemptionReasonCode(
                    value=linea.afectacion_igv.value
                ),
                tax_scheme=TaxScheme(
                    id=Id(value="9997"),
                    name=Name(value="EXO"),
                    tax_type_code=TaxTypeCode(value="VAT"),
                ),
            )
            subtotales_linea.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=cl.valor_venta, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=Decimal("0.00"), currency_id=moneda_cod
                    ),
                    tax_category=cat_exo,
                )
            )
        elif linea.afectacion_igv.es_inafecta:
            cat_ina = TaxCategory(
                id=Id(value="O"),
                percent=Percent(value=Decimal("0.00")),
                tax_exemption_reason_code=TaxExemptionReasonCode(
                    value=linea.afectacion_igv.value
                ),
                tax_scheme=TaxScheme(
                    id=Id(value="9998"),
                    name=Name(value="INA"),
                    tax_type_code=TaxTypeCode(value="FRE"),
                ),
            )
            subtotales_linea.append(
                TaxSubtotal(
                    taxable_amount=TaxableAmount(
                        value=cl.valor_venta, currency_id=moneda_cod
                    ),
                    tax_amount=TaxAmount(
                        value=Decimal("0.00"), currency_id=moneda_cod
                    ),
                    tax_category=cat_ina,
                )
            )

        line_tax_total = TaxTotal(
            tax_amount=TaxAmount(
                value=cl.monto_isc + cl.monto_igv, currency_id=moneda_cod
            ),
            tax_subtotal=subtotales_linea,
        )

        item_sellers_id = (
            SellersItemIdentification(id=Id(value=linea.codigo_producto))
            if linea.codigo_producto
            else None
        )
        item_elem = Item(
            description=[Description(value=linea.descripcion)],
            sellers_item_identification=item_sellers_id,
        )

        price_elem = Price(
            price_amount=PriceAmount(value=linea.valor_unitario, currency_id=moneda_cod)
        )

        return InvoiceLine(
            id=Id(value=str(linea.numero_orden)),
            invoiced_quantity=InvoicedQuantity(
                value=linea.cantidad, unit_code=linea.unidad_medida.value
            ),
            line_extension_amount=LineExtensionAmount(
                value=cl.valor_venta, currency_id=moneda_cod
            ),
            pricing_reference=pricing_ref,
            tax_total=[line_tax_total],
            item=item_elem,
            price=price_elem,
        )
