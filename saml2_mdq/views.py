import base64
import datetime
import hashlib
import logging
import os
import time
import urllib

from django.conf import settings
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render

from . utils import sign_xml, add_valid_until


logger = logging.getLogger(__name__)


@cache_control(max_age=getattr(settings, 'METADATA_CACHE_CONTROL', 3600))
def saml2_entities(request):
    md_path_file = settings.PYFF_METADATA_LOADED
    if not os.path.exists(md_path_file):
        msg = '{} Path does not exist'.format(md_path)
        logger.error(msg)
        return HttpResponse('', status=404)

    md_xml = open(md_path_file, 'rb').read()
    #dt_file_mod = os.path.getmtime(md_path_file)
    dt_file_mod = datetime.datetime.now().timestamp()

    # if there validUntil configuration
    if getattr(settings, 'METADATA_VALID_UNTIL', None):
        md_xml = add_valid_until(md_xml, dt_file_mod)

    # test the existence of rsa keys for signing
    key_fname = getattr(settings, 'METADATA_SIGNER_KEY', None)
    cert_fname = getattr(settings, 'METADATA_SIGNER_CERT', None)
    if key_fname and cert_fname:
        md_xml = sign_xml(md_xml, key_fname, cert_fname)

    # response
    # Shibboleth have: java.lang.IllegalArgumentException: Could not parse 'application/samlmetadata+xml, application/xml, text/xml'
    #content_type='application/samlmetadata+xml, application/xml, text/xml'
    content_type='application/samlmetadata+xml'
    response =  HttpResponse(md_xml,
                             content_type=content_type,
                             charset='utf-8')
    return response

@cache_control(max_age=getattr(settings, 'METADATA_CACHE_CONTROL', 3600))
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
        return HttpResponse('Some digits in the entityID are not permitted',
                            status=403)

    entity = urllib.parse.unquote_plus(entity)
    if entity[:8] == '{base64}':
        entity_name = base64.b64decode(entity[8:]).decode()
        sha_entity = hashlib.sha1(entity_name.encode()).hexdigest()
        entity = '{sha1}'+'{}'.format(sha_entity)

    # if requested in sha1 format
    if entity[:6] == '{sha1}':
        md_try = os.path.sep.join((md_path, entity[6:]))
    else:
        sha_entity = hashlib.sha1(entity.encode()).hexdigest()
        md_try = os.path.sep.join((md_path, sha_entity))

    md_try += '.xml'
    if os.path.exists(md_try):
        #dt_file_mod = os.path.getmtime(md_try)
        dt_file_mod = datetime.datetime.now().timestamp()
        md_xml = open(md_try, 'rb').read()

        # if there validUntil configuration
        if getattr(settings, 'METADATA_VALID_UNTIL', None):
            md_xml = add_valid_until(md_xml, dt_file_mod)

        # test the existence of rsa keys for signing
        key_fname = getattr(settings, 'METADATA_SIGNER_KEY', None)
        cert_fname = getattr(settings, 'METADATA_SIGNER_CERT', None)
        if key_fname and cert_fname:
            md_xml = sign_xml(md_xml, key_fname, cert_fname)

        # response
        # Shibboleth have: java.lang.IllegalArgumentException: Could not parse 'application/samlmetadata+xml, application/xml, text/xml'
        #content_type='application/samlmetadata+xml, application/xml, text/xml'
        content_type='application/samlmetadata+xml'
        response =  HttpResponse(md_xml,
                                 content_type=content_type,
                                 charset='utf-8')
        response["Last-Modified"] = time.ctime(dt_file_mod)
        return response
    else:
        raise Http404()
