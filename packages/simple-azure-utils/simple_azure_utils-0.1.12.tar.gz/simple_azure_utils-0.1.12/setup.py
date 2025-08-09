from setuptools import setup, find_packages

VERSION = '0.1.12'
DESCRIPTION = 'A simple set of utilities for interacting with Azure'
LONG_DESCRIPTION = 'A simple set of utilities for interacting with Azure'

# Setting up
setup(
    name="simple_azure_utils",
    version=VERSION,
    author="Terrell Mack",
    author_email="terrell.mack@live.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "azure-storage-blob>=12.14.0",
        "azure-identity>=1.24.0",
        "azure-keyvault==4.2.0",
        "azure-appconfiguration==1.3.0",
        "azure-core==1.35.0"
    ],
        # add any additional packages

    keywords=['python', 'azure'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)