from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_datev',
    version='3.3.0',
    description='Datev wrapper from Salure',
    long_description='Datev wrapper from Salure',
    author='D&A Salure',
    author_email='support@salureconnnect.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2',
        'pandas>=1,<=3'
    ],
    zip_safe=False,
)
