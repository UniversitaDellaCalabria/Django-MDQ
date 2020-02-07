Django SAML MDQ
---------------

Let's suppose that we need a simple as possibile SAML2 MDQ server that:

1) Runs locally as a private service for multiple containers or VM
2) Should be decoupled from pyFF
3) Should be much more performant than pyFF MDQ service
4) Haven't any signing or ValidUntil definitions features (TODO, not today)
5) Must be used in a safe environment

This means that we do not need signatures and things, but just a Metadata accessible via web following Young MD Draft specification.
Remember that pyFF is needed for metadata downloading, it can run as daemon or as a scheduled process, this latter sucks less resources.

Installation of the necessary software
--------------------------------------

````
apt install build-essential python3-dev libxml2-dev libxslt1-dev libyaml-dev python3-pip
pip3 install --upgrade pip
pip3 install virtualenv django
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

Create a pipelines to fetch and handle all the Idem + eduGAIN metadata, this would be similar to this
````
# Metadata download and validation
- load xrd garr-loaded.xrd:
  - ./pipelines/garr.xrd
# select can even filter entity by IDPSSO or SPSSO Description and things ...
- select
- store:
     directory: ./garr
- publish:
     output: ./garr/garr-loaded.xml
- stats

# MDX server
- when request:
    - select
    - pipe:
        - when accept application/xml:
             - xslt:
                 stylesheet: tidy.xsl
             - first
             - finalize:
                cacheDuration: PT5H
                validUntil: P10D
             - sign:
                 key: certificates/private.key
                 cert: certificates/public.cert
             - emit application/xml
             - break
        - when accept application/json:
             - xslt:
                 stylesheet: discojson.xsl
             - emit application/json:
             - break
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

Test the pipelines
````

pyff pipelines/garr.fd
````

You should have aan output of this kind
````
total size:     6003
selected:       6003
          idps: 3257
           sps: 2744
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
    <MetadataQueryProtocol>https://django_mdq.url/</MetadataQueryProtocol>
    </MetadataProvider>

</MetadataProvider>
````

A test with PySAML2
-------------------

````
import io
import json
import urllib.request

from saml2.mdstore import MetaDataMDX

# when available
mdq_url = "http://192.168.27.27:8001"
entity2check = 'https://idp.unical.it/idp/shibboleth'

mdx = MetaDataMDX(mdq_url) #, cert=cert)

# certificati
mdx.certs(entity2check, "idpsso", use="encryption")

# get certs from idp
mdx.service(entity2check, 'idpsso_descriptor', 'single_sign_on_service')
mdx.certs(entity2check, "idpsso", use="signing")
````

Configure Django MDQ
--------------------

1. Copy `django_mdq/settingslocal.py.example` to `django_mdq/settingslocal.py` and edit it, `PYFF_METADATA_FOLDER` must point to the folder where the pyFF downloads periodically the metadata xml files.
2. This projects doesn't need of any database configuration
3. Run it in development mode `./manage.py runserver 0.0.0.0:8001` or in production one (see gunicorn or uwsgi examples to do that)

Performance
-----------

First query of a Shibboleth IdP on a pyFF MDX Server, takes roughly 8 seconds, example with RedisWhoosStore and this configuration:
````
PYFF_STORE_CLASS=pyff.store:RedisWhooshStore pyffd -p pyff.pid -f -a --dir=`pwd` -H 0.0.0.0 -P 8001  pipelines/garr.fd
````

Or using gunicorn
````
gunicorn --reload --reload-extra-file pipelines/garr.fd --preload --bind 0.0.0.0:8001 -t 600 -e PYFF_PIPELINE=pipelines/garr.fd -e PYFF_STORE_CLASS=pyff.store:RedisWhooshStore -e PYFF_UPDATE_FREQUENCY=600 -e PYFF_PORT=8001 --threads 4 --worker-tmp-dir=/dev/shm --worker-class=gthread pyff.wsgi:app
````

Test from a real Shibboleth IdP 3.4.6
````
time /opt/shibboleth-idp/bin/aacli.sh -n luigi -r https://coco.release-check.edugain.org/shibboleth  -u http://localhost:8080/idp

{
"requester": "https://coco.release-check.edugain.org/shibboleth",
"principal": "luigi",
"attributes": [


  {
    "name": "eduPersonScopedAffiliation",
    "values": [
              "staff@testunical.it"          ]
  },

  {
    "name": "eduPersonTargetedID",
    "values": [
              "T6KCZHRUIHM27ENJE5A2LVQVYS6VCMS7"          ]
  },

  {
    "name": "eduPersonPrincipalName",
    "values": [
              "luigi@testunical.it"          ]
  },

  {
    "name": "email",
    "values": [
              "luigi@testunical.it"          ]
  }

]
}


real    0m7.917s
user    0m0.316s
sys 0m0.040s
````

First query on django_mdq server, less than 1.5 seconds
````
time /opt/shibboleth-idp/bin/aacli.sh -n luigi -r https://coco.release-check.edugain.org/shibboleth  -u http://localhost:8080/idp

{
"requester": "https://coco.release-check.edugain.org/shibboleth",
"principal": "luigi",
"attributes": [


  {
    "name": "eduPersonScopedAffiliation",
    "values": [
              "staff@testunical.it"          ]
  },

  {
    "name": "eduPersonTargetedID",
    "values": [
              "T6KCZHRUIHM27ENJE5A2LVQVYS6VCMS7"          ]
  },

  {
    "name": "eduPersonPrincipalName",
    "values": [
              "luigi@testunical.it"          ]
  },

  {
    "name": "email",
    "values": [
              "luigi@testunical.it"          ]
  }

]
}


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
