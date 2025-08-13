from setuptools import setup, find_packages

setup(
    name='castleguard_sdk',
    version='0.21',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    author='Ravi Ramsaran',
    author_email='ravi.ramsaran@nextria.ca',
    description='A Python SDK for interacting with CastleGuard APIs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
    
