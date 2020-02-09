import hashlib
import logging
import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render

from . utils import sign_xml


logger = logging.getLogger(__name__)


def saml2_entity(request, entity):
    md_path = settings.PYFF_METADATA_FOLDER
    if not os.path.exists(md_path):
        msg = '{} Path does not exist'.format(md_path)
        logger.error(msg)
        return HttpResponse('', status=404)

    # path traversal prevention
    if entity != entity.replace('..', '').\
                        replace('%2e%2e', '').\
                        replace('\.', '').\
                        replace('%5C.', '').\
                        replace('%2e%2e%2f', '').\
                        replace('%252e%252e', ''):
        msg = 'Error Path traversal prevention on {}'.format(entity)
        logger.error(msg)
        return HttpResponse('Some digits in the entityID are not permitted', status=403)

    # if requested in sha1 format
    if entity[0:6] == '{sha1}':
        md_try = os.path.sep.join((md_path, entity[6:]))
    else:
        sha_entity = hashlib.sha1(entity.encode())
        md_try = os.path.sep.join((md_path, sha_entity.hexdigest()))

    md_try += '.xml'
    if os.path.exists(md_try):
        # test the existence of rsa keys for signing
        key_fname = getattr(settings, 'METADATA_SIGNER_KEY', None)
        cert_fname = getattr(settings, 'METADATA_SIGNER_CERT', None)
        if key_fname and cert_fname:
            md_xml = sign_xml(md_try, key_fname, cert_fname)
        # otherwise static serve without signing
        else:
            md_xml = open(md_try).read()
        return HttpResponse(md_xml,
                            content_type='application/samlmetadata+xml')
    else:
        raise Http404()
