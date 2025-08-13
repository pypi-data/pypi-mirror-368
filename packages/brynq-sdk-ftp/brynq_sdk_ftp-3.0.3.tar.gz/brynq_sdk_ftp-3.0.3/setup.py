from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_ftp',
    version='3.0.3',
    description='FTP wrapper from BrynQ',
    long_description='FTP wrapper from Brynq',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'brynq-sdk-brynq>=4,<5',
        'requests>=2,<=3',
        'paramiko>=2,<=4',
        'pysftp>0.2,<1',
        'tenacity>=8,<9'
    ],
    zip_safe=False,
)