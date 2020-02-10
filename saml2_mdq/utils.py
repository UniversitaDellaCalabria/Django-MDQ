import datetime
import xmlsec

from django.conf import settings
from lxml import etree


def add_valid_until(xml_stream, dt_start):
    #template = etree.parse(xml_fname).getroot()
    #template = etree.fromstring(xml_stream).getroot()
    template = etree.XML(xml_stream)
    if template.get('validUntil'):
        return etree.tostring(template)

    offset = datetime.timedelta(minutes=settings.METADATA_VALID_UNTIL)
    dt = datetime.datetime.fromtimestamp(dt_start) + offset
    template.set('validUntil', dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return etree.tostring(template)


def sign_xml(xml_stream, key_fname, cert_fname):
    template = etree.XML(xml_stream)

    opts = dict()
    if hasattr(template, 'getroot') and \
       hasattr(template.getroot, '__call__'):
        root = template.getroot()
    else:
        root = template
    idattr = root.get('ID') or root.get('id')
    if idattr:
        opts['reference_uri'] = "#{}".format(idattr)

    signed_xml = xmlsec.sign(root, key_fname, cert_fname, **opts)
    return etree.tostring(signed_xml)
