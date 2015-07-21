from distutils.core import setup

setup(
  name = 'cdn-it',
  packages = ['cdn_it'],
  version = '1.0.0',
  description = 'Quickly create an auto updating jsDelivr project',
  author = 'Graeme Yeates',
  author_email = 'megawac@gmail.com',
  url = 'https://github.com/megawac/cdn-it',
  download_url = 'https://github.com/megawac/cdn-it/tarball/v1.0.1',
  keywords = ['cdn', 'jsdelivr'], # arbitrary keywords
  classifiers = [],
  entry_points={
    'cdn_it': [
        'cdn-it = cdn_it:main'
    ]
  }
)