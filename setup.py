from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'coverage',
    'datadog',
    'decorator',
    'docopt',
    'gitdb',
    'GitPython',
    'nose',
    'PyGithub',
    'slackweb',
    'awscli',
    'awsebcli',
    'requests',
]


setup(
    name='LI-AWS-Deploy',
    version='1.3.4',
    description='Deploy tool for Loja Integrada Web Applications',
    long_description=long_description,
    author='Chris Maillefaud',
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='aws deploy',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'lideploy=deploy.run:start',
        ],
    },
)
