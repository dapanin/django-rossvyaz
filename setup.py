#!/usr/bin/env python
from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='django-rossvyaz',
    version='1.3.0',
    author='Ivan Petukhov',
    author_email='satels@gmail.com',
    packages=['django_rossvyaz', 'django_rossvyaz.management',
              'django_rossvyaz.management.commands',
              'django_rossvyaz.migrations'],
    url='https://github.com/satels/django-rossvyaz',
    download_url='https://github.com/satels/django-rossvyaz/zipball/master',
    license='MIT license',
    description='РосСвязь: Выписка из реестра Российской системы и плана нумерации - подготовленная таблица с очищенными регионами',
    long_description=long_description,
    include_package_data=True,
    package_data={
        'django_rossvyaz': ['templates/django_rossvyaz/*.html'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ],
)
