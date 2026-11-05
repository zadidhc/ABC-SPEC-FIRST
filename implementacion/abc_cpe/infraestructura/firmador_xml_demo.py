"""Firma XMLDSig RSA-SHA256 de demostración para UBL Invoice 2.1.

No es una firma tributaria SUNAT: genera certificado autofirmado temporal de prueba.
NO usar en producción ni para enviar comprobantes reales.
"""

from __future__ import annotations

import base64
import copy
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from lxml import etree
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

EXT_NS = 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
DS_NS = 'http://www.w3.org/2000/09/xmldsig#'
NS = {'ext': EXT_NS, 'ds': DS_NS}
C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'
SIGNATURE_ALG = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
DIGEST_ALG = 'http://www.w3.org/2001/04/xmlenc#sha256'
ENVELOPED = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'
SIG_ID = 'SIG-ABC-DEMO'


def _analizar(xml_bytes: bytes):
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_blank_text=True)
    return etree.fromstring(xml_bytes, parser=parser)


def _c14n(el):
    return etree.tostring(el, method='c14n', exclusive=True, with_comments=False)


def _eliminar_firma_del_clon(root):
    tmp = copy.deepcopy(root)
    firmas = tmp.xpath('.//ds:Signature', namespaces=NS)
    if len(firmas) != 1:
        raise ValueError('Se esperaba exactamente una firma XMLDSig')
    firmas[0].getparent().remove(firmas[0])
    return tmp


def crear_certificado_prueba():
    """Clave RSA efímera + certificado X.509 autofirmado solo en memoria."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    sujeto = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, 'ABC Software Corp - CERTIFICADO DE PRUEBA'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Proyecto academico UBL 2.1'),
    ])
    ahora = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(sujeto)
        .issuer_name(sujeto)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1))
        .not_valid_after(ahora + timedelta(days=30))
        .sign(private_key, hashes.SHA256())
    )
    return private_key, cert


def firmar_xml_prueba(xml_bytes: bytes) -> bytes:
    """Inserta ds:Signature en UBLExtensions y firma el documento completo."""
    root = _analizar(xml_bytes)
    if root.xpath('.//ds:Signature', namespaces=NS):
        raise ValueError('El XML ya contiene una firma criptografica')
    ext_ex = root.find(f'{{{EXT_NS}}}UBLExtensions')
    if ext_ex is None:
        ext_ex = etree.Element(f'{{{EXT_NS}}}UBLExtensions', nsmap={'ext': EXT_NS})
        root.insert(0, ext_ex)
    extension = etree.SubElement(ext_ex, f'{{{EXT_NS}}}UBLExtension')
    contenido = etree.SubElement(extension, f'{{{EXT_NS}}}ExtensionContent')
    firma = etree.SubElement(contenido, f'{{{DS_NS}}}Signature', nsmap={'ds': DS_NS})
    firma.set('Id', SIG_ID)

    si = etree.SubElement(firma, f'{{{DS_NS}}}SignedInfo')
    etree.SubElement(si, f'{{{DS_NS}}}CanonicalizationMethod', Algorithm=C14N)
    etree.SubElement(si, f'{{{DS_NS}}}SignatureMethod', Algorithm=SIGNATURE_ALG)
    referencia = etree.SubElement(si, f'{{{DS_NS}}}Reference', URI='')
    transformaciones = etree.SubElement(referencia, f'{{{DS_NS}}}Transforms')
    etree.SubElement(transformaciones, f'{{{DS_NS}}}Transform', Algorithm=ENVELOPED)
    etree.SubElement(transformaciones, f'{{{DS_NS}}}Transform', Algorithm=C14N)
    etree.SubElement(referencia, f'{{{DS_NS}}}DigestMethod', Algorithm=DIGEST_ALG)
    digest_value = etree.SubElement(referencia, f'{{{DS_NS}}}DigestValue')

    documento_sin_firma = _eliminar_firma_del_clon(root)
    digest = hashlib.sha256(_c14n(documento_sin_firma)).digest()
    digest_value.text = base64.b64encode(digest).decode('ascii')

    llave, certificado = crear_certificado_prueba()
    valor_firma = llave.sign(_c14n(si), padding.PKCS1v15(), hashes.SHA256())
    etree.SubElement(firma, f'{{{DS_NS}}}SignatureValue').text = base64.b64encode(valor_firma).decode('ascii')
    ki = etree.SubElement(firma, f'{{{DS_NS}}}KeyInfo')
    x509_data = etree.SubElement(ki, f'{{{DS_NS}}}X509Data')
    etree.SubElement(x509_data, f'{{{DS_NS}}}X509Certificate').text = base64.b64encode(
        certificado.public_bytes(serialization.Encoding.DER)
    ).decode('ascii')

    signed = etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=False)
    verificar_firma_prueba(signed)
    return signed


def verificar_firma_prueba(xml_firmado: bytes) -> None:
    """Verifica firma y digest. NO comprueba confianza tributaria del certificado."""
    root = _analizar(xml_firmado)
    firmas = root.xpath('.//ds:Signature', namespaces=NS)
    if len(firmas) != 1:
        raise ValueError('No hay exactamente una firma ds:Signature')
    firma = firmas[0]
    si = firma.find(f'{{{DS_NS}}}SignedInfo')
    if si is None:
        raise ValueError('Falta SignedInfo')
    c14n_method = si.find(f'{{{DS_NS}}}CanonicalizationMethod')
    signature_method = si.find(f'{{{DS_NS}}}SignatureMethod')
    refs = si.findall(f'{{{DS_NS}}}Reference')
    if c14n_method is None or c14n_method.get('Algorithm') != C14N:
        raise ValueError('Canonizacion no soportada')
    if signature_method is None or signature_method.get('Algorithm') != SIGNATURE_ALG:
        raise ValueError('Algoritmo de firma no soportado')
    if len(refs) != 1 or refs[0].get('URI') != '':
        raise ValueError('Referencia de documento no soportada')
    transformaciones = refs[0].find(f'{{{DS_NS}}}Transforms')
    algoritmos = ([x.get('Algorithm') for x in transformaciones] if transformaciones is not None else [])
    if algoritmos != [ENVELOPED, C14N]:
        raise ValueError('Transformaciones inesperadas')
    dm = refs[0].find(f'{{{DS_NS}}}DigestMethod')
    if dm is None or dm.get('Algorithm') != DIGEST_ALG:
        raise ValueError('DigestMethod no soportado')
    dv = refs[0].find(f'{{{DS_NS}}}DigestValue')
    if dv is None or not dv.text:
        raise ValueError('Falta DigestValue')
    esperado = base64.b64decode(dv.text)
    obtenido = hashlib.sha256(_c14n(_eliminar_firma_del_clon(root))).digest()
    if not hmac.compare_digest(esperado, obtenido):
        raise ValueError('El XML fue alterado después de firmarlo (digest diferente)')

    sv = firma.find(f'{{{DS_NS}}}SignatureValue')
    certs = firma.xpath('./ds:KeyInfo/ds:X509Data/ds:X509Certificate', namespaces=NS)
    if sv is None or not sv.text or len(certs) != 1 or not certs[0].text:
        raise ValueError('Falta firma o certificado X509')
    cert = x509.load_der_x509_certificate(base64.b64decode(certs[0].text))
    cert.public_key().verify(
        base64.b64decode(sv.text), _c14n(si), padding.PKCS1v15(), hashes.SHA256()
    )

