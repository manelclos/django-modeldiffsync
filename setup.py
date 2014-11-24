from setuptools import setup, find_packages


setup(
    name='django-modeldiffsync',
    version='0.1',
    description='Sync modeldiff information between two databases',
    long_description=open('README.md').read(),
    author='Manel Clos',
    author_email='manelclos@gmail.com',
    url='http://github.com/manelclos/django-modeldiffsync',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
