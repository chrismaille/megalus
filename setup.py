from codecs import open
from os import path
from setuptools import setup, find_packages
from megalus import __version__


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'awscli',
    'awsebcli',
    'coverage',
    'datadog',
    'decorator',
    'docopt',
    'gitdb',
    'GitPython',
    'ipdb',
    'nose',
    'PyGithub',
    'python-memcached',
    'redis',
    'requests<=2.9.1',
    'slackweb',
    'unidecode',
    'colorama==0.3.7',
    'boto3',
    'pydocstyle',
    'pycodestyle'
]


setup(
    name='Meg-Tools',
    version=__version__,
    description='Dev tools for Megalus Web Applications',
    long_description=long_description,
    author='Chris Maillefaud',
    include_package_data=True,
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='aws deploy docker npm redis memcached bash',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'meg=megalus.run:start'
        ],
    },
)
