

import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='barter-auth',
    version='0.3.43',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    license='BSD',
    description='Barter authentication package',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/kabilovtoha/barter_auth',
    author='akatoha',
    author_email='kabilov2011@gmail.com',
    install_requires=[
        'Django>=3.2',
        'six>=1.15.0',
        'pydantic-settings>=2.1.0',
        'redis>=4.6.0',
        'pydantic>=1.10.9',
        'httpx>=0.24.1',
        'factory-boy>=3.2.1',
        'faker>=18.11.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)