import hashlib
import logging
import os

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render


logger = logging.getLogger(__name__)


def saml2_entity(request, entity):
    md_path = settings.PYFF_METADATA_FOLDER
    if not os.path.exists(md_path):
        msg = '{} Path does not exist'.format(md_path)
        logger.error(msg)
        return HttpResponse('', status=404)

    # path traversal prevention
    entity = entity.replace('..', '')

    # if requested in sha1 format
    if entity[0:6] == '{sha1}':
        md_try = os.path.sep.join((md_path, entity[6:]))+'.xml'
    else:
        sha_entity = hashlib.sha1(entity.encode())
        md_try = os.path.sep.join((md_path, sha_entity.hexdigest()))+'.xml'

    if os.path.exists(md_try):
        md_xml = open(md_try).read()
        return HttpResponse(md_xml, content_type='application/samlmetadata+xml')
    else:
        raise Http404()
