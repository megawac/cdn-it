from distutils.core import setup

with open('requirements.txt') as f:
  requires = [x.strip() for x in f.readlines()]

setup(
  name = 'cdn-it',
  packages = ['cdn_it'],
  version = '1.0.8',
  description = 'Quickly create an auto updating jsDelivr project',
  author = 'Graeme Yeates',
  author_email = 'megawac@gmail.com',
  url = 'https://github.com/megawac/cdn-it',
  download_url = 'https://github.com/megawac/cdn-it/tarball/v1.0.8',
  keywords = ['cdn', 'jsdelivr'], # arbitrary keywords
  classifiers = [],
  install_requires = requires,
  entry_points={
    'console_scripts': [
        'cdn-it=cdn_it:main'
    ]
  }
)