from setuptools import setup, find_packages


setup(
    name='django-multidb-router',
    version='0.6',
    description='Round-robin multidb router for Django.',
    long_description=open('README.rst').read(),
    author='Jeff Balogh',
    author_email='jbalogh@mozilla.com',
    url='https://github.com/jbalogh/django-multidb-router',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_requires=['django-nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
