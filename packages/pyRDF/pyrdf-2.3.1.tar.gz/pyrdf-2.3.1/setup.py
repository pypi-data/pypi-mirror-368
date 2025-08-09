#!/usr/bin/env python

from setuptools import setup


version = '2.3.1'

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='pyRDF',
    version=version,
    author='Xander Wilcke',
    author_email='w.x.wilcke@vu.nl',
    url='https://wxwilcke.gitlab.io/pyRDF',
    download_url = 'https://gitlab.com/wxwilcke/pyRDF/-/archive/' + version + '/pyRDF-' + version + '.tar.gz',
    description='Lightweight RDF Stream Parser',
    long_description = open('README.md').read(),
    long_description_content_type="text/markdown",
    license='GLP3',
    include_package_data=True,
    zip_safe=True,
    keywords=['rdf', 'ntriples', 'nquads', 'rdf-star', 'parser', 'streamer'],
    python_requires='>=3.8',
    test_suite="tests",
)
