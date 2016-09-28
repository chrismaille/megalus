from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'deploy', 'requirements.txt')) as f:
    install_requires = [
        line
        for line in f
    ]


setup(
    name='LI-AWS-Deploy',
    version='1.0.3',
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
        'lideploy': [
            'deploy=run:start',
        ],
    },
)