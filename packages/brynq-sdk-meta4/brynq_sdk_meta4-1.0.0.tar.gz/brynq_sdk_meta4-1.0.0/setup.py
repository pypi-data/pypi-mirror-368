from setuptools import setup, find_namespace_packages

setup(
    name='brynq_sdk_meta4',
    version='1.0.0',
    description='Meta4 wrapper from BrynQ',
    author='BrynQ',
    author_email='support@brynq.com',
    packages=find_namespace_packages(include=['brynq_sdk*']),
    license='BrynQ License',
    install_requires=[
        'pandas>=1.5.0',
        'pandera>=0.10.0',
        'brynq-sdk-brynq>=4,<5',
        'brynq-sdk-functions>=2,<3',
        'brynq-sdk-sftp>=3,<4'
    ],
    zip_safe=False
)
