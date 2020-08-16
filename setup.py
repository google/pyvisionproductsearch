# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pyvisionproductsearch',
    packages=['pyvisionproductsearch'],
    version='0.3',
    license='apache-2.0',
    description='Python Wrapper around the Google Vision Product Search API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dale Markowitz',
    author_email='dale@dalemarkowitz.com',
    # Provide either the link to your github or to your website
    url='https://github.com/google/pyvisionproductsearch',
    download_url='https://github.com/google/pyvisionproductsearch/archive/v0.3.tar.gz',
    # Keywords that define your package best
    keywords=['google cloud', 'product search', 'vision', 'machine learning'],
    install_requires=[            # I get to this in a second
        'google-cloud-vision',
        'google-cloud-storage',
        'google-cloud-core',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
