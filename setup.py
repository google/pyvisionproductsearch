from distutils.core import setup
setup(
  name = 'pyvisionproductsearch',
  packages = ['PYVISIONPRODUCTSEARCH'],
  version = '0.1',
  license='apache-2.0',
  description = 'Python Wrapper around the Google Vision Product Search API',
  author = 'Dale Markowitz',
  author_email = 'dale@dalemarkowitz.com',
  url = 'https://github.com/google/pyvisionproductsearch',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/google/pyvisionproductsearch/archive/v0.1.tar.gz',
  keywords = ['google cloud', 'product search', 'vision', 'machine learning'],   # Keywords that define your package best
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