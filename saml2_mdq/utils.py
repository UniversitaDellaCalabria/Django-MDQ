import xmlsec

from lxml import etree


def sign_xml(xml_fname, key_fname, cert_fname):
    template = etree.parse(xml_fname).getroot()

    opts = dict()
    if hasattr(template, 'getroot') and \
       hasattr(templace.getroot, '__call__'):
        root = template.getroot()
    else:
        root = template
    idattr = root.get('ID') or root.get('id')
    if idattr:
        opts['reference_uri'] = "#{}".format(idattr)

    signed_xml = xmlsec.sign(template, key_fname, cert_fname, **opts)
    return etree.tostring(signed_xml)
