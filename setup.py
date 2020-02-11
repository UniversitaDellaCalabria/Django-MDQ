from setuptools import setup

_name = 'saml2_mdq'

def readme():
    with open('README.md') as f:
        return f.read()

setup(name=_name,
      version='0.6.0',
      zip_safe = False,
      description="Django SAML MDQ",
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=['Development Status :: 5 - Production/Stable',
                  'License :: OSI Approved :: BSD License',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 3'],
      url='https://github.com/UniversitaDellaCalabria/Django-MDQ',
      author='Giuseppe De Marco',
      author_email='giuseppe.demarco@unical.it',
      license='BSD',
      packages=[_name],
      install_requires=['django', 'pyff'],
     )
