Django SAML MDQ
---------------

A lightweight SAML2 MDQ server that:

1) Runs on top of the metadata downloaded and validated by pyFF (batch pipeline)
2) Is much more performant than a pyFFd MDQ service
3) Have signing features (on top of xmlsec)
4) Have ValidUntil definitions feature
5) Have a lightweight [draft-young-md-query implementation](https://tools.ietf.org/html/draft-young-md-query-12)
6) Supports the following Entities Identifiers: urlencoded, {sha1} and {base64}

Remember that pyFF is needed for metadata downloading, it can run as daemon or as a scheduled process (batch)

Table of contents
-----------------

<!--ts-->
   * #### Installation
       * [Requirements](#requirements)
       * [Configure pyFF](#configure-pyff)
       * [Test the pipeline](#test-the-pipeline)
       * [Configure Django MDQ](#configure-django-mdq)
   * #### Client configurations
      * [Shibboleth IdP Configuration](#shibboleth-idp-configuration)
      * [PySAML2](#A-test-with-pysaml2)
   * #### Performances
      * [Performances](#performances)
   * [Authors](#authors)
   * [Credits](#credits)
<!--te-->

Requirements
------------

````
apt install build-essential python3-dev libxml2-dev libxslt1-dev libyaml-dev python3-pip
pip3 install --upgrade pip
pip3 install virtualenv django lxml xmlsec
````

Install [pyFF](https://pyff.io/)
````
virtualenv -p python3 python-pyff
source python-pyff/bin/activate
pip3 install git+https://github.com/IdentityPython/pyFF.git
````

Configure pyFF
--------------

````
# Create a folder for the configuration
mkdir pyff-configuration
cd pyff-configuration

# create folder for the certificates
mkdir certificates

# create certificates
openssl req -nodes -new -x509 -days 3650 -keyout certificates/private.key -out certificates/public.cert -subj '/CN=your.own.fqdn.com'

# create a pipeline directory
mkdir pipelines
````

Create a pipelines to fetch and handle all the Idem + eduGAIN metadata, this would be similar to the following.
Name it `pipelines/garr_batch.fd`:
````
# Metadata download and validation
- load xrd garr-loaded.xrd:
  - ./pipelines/garr.xrd
# select can even filter entity by IDPSSO or SPSSO Description and things ...
# - select: "!//md:EntityDescriptor[md:SPSSODescriptor]"
- select
- store:
     directory: ./garr
- publish:
     output: ./garr/garr-loaded.xml
- stats
````

Now create the XRD file where to configure the URLs where the Metadata can be downloaded.
Name it `pipelines/garr.xrd`
````
<?xml version="1.0" encoding="UTF-8"?>
<XRDS xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
  <XRD>
    <Link rel="urn:oasis:names:tc:SAML:2.0:metadata" href="http://md.idem.garr.it/metadata/idem-test-metadata-sha256.xml"/>
  </XRD>
  <XRD>
    <Subject>http://md.idem.garr.it/metadata/edugain2idem-metadata-sha256.xml</Subject>
    <Link rel="urn:oasis:names:tc:SAML:2.0:metadata" href="http://md.idem.garr.it/metadata/edugain2idem-metadata-sha256.xml">
        <Title>IDEM+eduGAIN</Title>
        <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <ds:X509Data>
                <ds:X509Certificate>
                MIIDWzCCAkOgAwIBAgIJALo/EGIq8rgNMA0GCSqGSIb3DQEBCwUAMEQxCzAJBgNV
                BAYTAklUMRYwFAYDVQQKDA1JREVNIEdBUlIgQUFJMR0wGwYDVQQDDBRJREVNIE1l
                dGFkYXRhIFNpZ25lcjAeFw0xOTAxMjIxNjA5MjBaFw0yMjAxMjExNjA5MjBaMEQx
                CzAJBgNVBAYTAklUMRYwFAYDVQQKDA1JREVNIEdBUlIgQUFJMR0wGwYDVQQDDBRJ
                REVNIE1ldGFkYXRhIFNpZ25lcjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
                ggEBAMay3N21fswu3AE6hqCPUVjvCyol5OKTHs9CXDIFyAoigP+YSdloLSGwx6n6
                ks9aBbJqlzRBIEd3CpByvX7GmBuITl3ElhxMY40Cv/ULok1GbDmQMhPScU6J1f9b
                526R9Ks+BbYZYmBRX9gqmpX1R867IES4z+JhXnXr5K8HTPjfaDGh2xORL6msXjww
                DJgaJCOpBCctLvCWcmUp0ucpl8VHGjFAAI5Eb6pwQEEPj1yqW52ggM+AHNFY6bAC
                9RX7Qv8MonQZwXpNNBNL+UcnGLVBXtBftd4zq7XxPNN9F/Ele3YJGaOVk8cCEJt5
                SfTeguzUaAyh8f/BfEs6CwucCSsCAwEAAaNQME4wHQYDVR0OBBYEFCZQVW7g6mc9
                3zaJP/p0lGbVQ4O6MB8GA1UdIwQYMBaAFCZQVW7g6mc93zaJP/p0lGbVQ4O6MAwG
                A1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAF6OKKdWyeI385ZS5i29mSMA
                4BoPCVAhyXDMLMdqTQqvZp3PAL/zjLYRYKgGH53d4uN/EztWM8YBdyzBzdbpFWpd
                wRGzwyfXzt6l2luElWb59PacNqHbBkyFO2YZmgqLzgrVX1gA3/3ij9zrLqd1lHVH
                MHPUpqv98KYXnttyzhacdYaRGDO/2A28U9QeRq2/HgVScklhJvoySeNyXNspYfte
                ePRxeHBj21DgiQb+X1+ovKASM+RULa6cA1TJBCop+VqZMZiRJ3Rj6RML63ckEO8H
                Md/XFvxlr+P2JcVKzHaZEEUGGINUCCuDABqKBZOqykGWXDastVw6/I0OIdLmWNI=
                </ds:X509Certificate>
            </ds:X509Data>
      </ds:KeyInfo>
    </Link>
  </XRD>
</XRDS>
````

#### Test the pipeline
````

pyff pipelines/garr.fd
````

You should have an output of this kind
````
total size:     6003
selected:       6003
          idps: 3257
           sps: 2744
````

Configure Django MDQ
--------------------
If you need to integrate `saml2_mdq` in a preexisting django project you can install it as an app:
````
pip install saml2_mdq
````
Then add `saml2_mdq` into your `settings.INSTALLED_APPS`, it doesn't need migrations.
Add also `django.middleware.http.ConditionalGetMiddleware` in `settings.MIDDLEWARE` to enable `ETag` in the HttpResponse headers.

If you instead just need a fully working MDQ server you can copy the entire project this way
````
git clone https://github.com/UniversitaDellaCalabria/Django-MDQ.git
cd Django-MDQ
pip install -r requirements
````

Then

1. Copy `django_mdq/settingslocal.py.example` to `django_mdq/settingslocal.py` and edit it
2. in `django_mdq/settingslocal.py` configure:
   - `PYFF_METADATA_FOLDER` must point to the folder where the pyFF downloads periodically the metadata xml files
   - `PYFF_METADATA_LOADED` must point to the full metadata xml published by pyff, containing all the entities
   - `METADATA_SIGNER_KEY` and `METADATA_SIGNER_CERT` to enable Metadata signing features (optional, not required)
   - `METADATA_CACHE_CONTROL` to set the Http-Header Cache control max-age
   - `METADATA_VALID_UNTIL` to set the freshness of the metadata
2. This projects doesn't need of any database configuration
3. Run it in development mode `./manage.py runserver 0.0.0.0:8001` or in production one (see gunicorn or uwsgi examples to do that)

To create your Metadata RSA keys you can even use this example command:
````
openssl req -nodes -new -x509 -days 3650 -keyout certificates/private.key -out certificates/public.cert -subj '/CN=your.own.fqdn.com'
````

Shibboleth IdP Configuration
----------------------------

This is a metadata-provider definition file that can be included in`/opt/shibboleth-idp/conf/services.xml`.
In the MetadataProviders resources, called `<util:list id="shibboleth.MetadataResolverResources">` we can put it as the child element `<value>%{idp.home}/conf/metadata-providers-mdq.xml</value>`.
Just change `django_mdq.url` in your production url.
````
<?xml version="1.0" encoding="UTF-8"?>
<!-- This file is an EXAMPLE metadata configuration file. -->
<MetadataProvider id="ShibbolethMetadataMdq" xsi:type="ChainingMetadataProvider"
    xmlns="urn:mace:shibboleth:2.0:metadata"
    xmlns:resource="urn:mace:shibboleth:2.0:resource"
    xmlns:security="urn:mace:shibboleth:2.0:security"
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="urn:mace:shibboleth:2.0:metadata http://shibboleth.net/schema/idp/shibboleth-metadata.xsd
                        urn:mace:shibboleth:2.0:resource http://shibboleth.net/schema/idp/shibboleth-resource.xsd
                        urn:mace:shibboleth:2.0:security http://shibboleth.net/schema/idp/shibboleth-security.xsd
                        urn:oasis:names:tc:SAML:2.0:metadata http://docs.oasis-open.org/security/saml/v2.0/saml-schema-metadata-2.0.xsd">

    <MetadataProvider id="DynamicEntityMetadata" xsi:type="DynamicHTTPMetadataProvider"
                  connectionRequestTimeout="PT5S"
                  connectionTimeout="PT5S"
                  socketTimeout="PT3S">

    <!-- Enable this if have configured METADATA_SIGNER_KEY and METADATA_SIGNER_CERT in Django-MDQ settingslocal.py
    <MetadataFilter xsi:type="SignatureValidation" requireSignedRoot="true"
                    certificateFile="%{idp.home}/credentials/mdq-cert.pem"/>
    -->

    <!-- Enable this if have configured METADATA_VALID_UNTIL in Django-MDQ settingslocal.py
    <MetadataFilter xsi:type="RequiredValidUntil" maxValidityInterval="P14D"/>
    -->

    <MetadataQueryProtocol>https://django_mdq.url/</MetadataQueryProtocol>
    </MetadataProvider>

</MetadataProvider>
````

#### Test the configuration
````
# reload ShibbolethIdP or Metadata Service
touch /opt/jetty/webapps/idp.xml

# do a mdquery
/opt/shibboleth-idp/bin/mdquery.sh -e https://coco.release-check.edugain.org/shibboleth --saml2 -u http://localhost:8080/idp
````

A test with PySAML2
-------------------

````
import io
import json
import urllib.request

from saml2.mdstore import MetaDataMDX

def b64(entity_name):
    return '{base64}'+base64.b64encode(entity_name.encode()).decode()

# when available
mdq_url = "http://localhost:8001"
mdq_cert = "certificates/public.cert"

entity2check = 'https://idp.unical.it/idp/shibboleth'

cert = open(mdq_cert)

# omit cert if unavailable
mdx = MetaDataMDX(mdq_url, cert=cert)
# base64 entity name trasformation
# mdx = MetaDataMDX(mdq_url, cert=cert, entity_transform=b64)

# certificati
mdx.certs(entity2check, "idpsso", use="encryption")

# get certs from idp
mdx.service(entity2check, 'idpsso_descriptor', 'single_sign_on_service')
mdx.certs(entity2check, "idpsso", use="signing")
````

Performances
-----------

The first query of a Shibboleth IdP (uncached) on a pure pyFF MDX Server takes roughly 8 seconds.
The first query of a Shibboleth IdP (uncached) on Django-MDQ takes less then 1.5 seconds.

Run pyFFd with RedisWhoosStore:
````
PYFF_STORE_CLASS=pyff.store:RedisWhooshStore pyffd -p pyff.pid -f -a --dir=`pwd` -H 0.0.0.0 -P 8001  pipelines/garr.fd
````

or Run pyFF using gunicorn instead:
````
gunicorn --reload --reload-extra-file pipelines/garr.fd --preload --bind 0.0.0.0:8001 -t 600 -e PYFF_PIPELINE=pipelines/garr.fd -e PYFF_STORE_CLASS=pyff.store:RedisWhooshStore -e PYFF_UPDATE_FREQUENCY=600 -e PYFF_PORT=8001 --threads 4 --worker-tmp-dir=/dev/shm --worker-class=gthread pyff.wsgi:app
````

Test pyFFd performance with a real Shibboleth IdP 3.4.6:
````
time /opt/shibboleth-idp/bin/aacli.sh -n luigi -r https://coco.release-check.edugain.org/shibboleth  -u http://localhost:8080/idp

{
"requester": "https://coco.release-check.edugain.org/shibboleth",
"principal": "luigi",
"attributes": [ ... ]


real    0m7.917s
user    0m0.316s
sys 0m0.040s
````

Test django_mdq server with the same but restarted Shibboleth 3.4.6:
````
time /opt/shibboleth-idp/bin/aacli.sh -n luigi -r https://coco.release-check.edugain.org/shibboleth  -u http://localhost:8080/idp

{
"requester": "https://coco.release-check.edugain.org/shibboleth",
"principal": "luigi",
"attributes": [ ... ]


real    0m1.354s
user    0m0.348s
sys 0m0.028s
````

Authors
-------

Giuseppe De Marco <giuseppe.demarco@unical.it>


Credits
-------
[IdentityPython](https://idpy.org/)
