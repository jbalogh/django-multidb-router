from setuptools import setup, find_packages


setup(
    name='django-multidb-router',
    version='0.5',
    description='Round-robin multidb router for Django.',
    long_description=open('README.rst').read(),
    author='Jeff Balogh',
    author_email='jbalogh@mozilla.com',
    url='http://github.com/jbalogh/multidb-router',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_requires=['Fabric', 'django-nose'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # I don't know what exactly this means, but why not?
        'Environment :: Web Environment :: Mozilla',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
