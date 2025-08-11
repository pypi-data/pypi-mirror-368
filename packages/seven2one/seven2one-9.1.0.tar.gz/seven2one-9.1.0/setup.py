from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')
version = ''
with open(here / 'seven2one/__init__.py') as fp:
      while version == '':
            line = fp.readline()
            if (line.startswith("__version__")):
                  version = line.replace("__version__", "").replace("=", "").replace('"', "").replace("'", "").strip()
            if not line:
                  break

setup(name='seven2one',
      version=version,
      description='Functions to interact with the Seven2one TechStack',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://www.seven2one.de',
      author='Seven2one Informationssysteme GmbH',
      author_email='info@seven2one.de',
      license='MIT',
      license_files=('LICENSE',),
      packages=['seven2one', 'seven2one.utils', 'seven2one.logging_loki'],
      include_package_data=True,
      install_requires=[
        'pandas>=1.4.2,<2.0.0',
        'gql==3.0.0',
        'pytz==2024.1',
        'tzlocal==5.2',
        'pyperclip==1.9.0',
        'loguru==0.7.2',
        'pika==1.3.2',
        'requests==2.32.3',
        'requests_toolbelt==1.0.0',
        'requests_oauthlib==2.0.0',
        'rfc3339==6.2',
        'numpy==1.24.4',
        'setuptools==71.1.0',
      ],
      classifiers =[
            'Development Status :: 3 - Alpha',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            ],
      python_requires='>=3.8',
      zip_safe=False)