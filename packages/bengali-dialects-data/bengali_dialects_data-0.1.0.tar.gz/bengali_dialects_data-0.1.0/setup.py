from setuptools import setup, find_packages

setup(
    name='bengali-dialects-data',
    version='0.1.0',
    description='A language dataset for Bengali Local Language Translation for digital Inclusion.',
    author='Md Golam Kibriya',
    maintainer='Md. Shahidul Islam', # The Project PI
    url='https://www.uap-bd.edu/', # University URL as a placeholder
    packages=find_packages(),
    include_package_data=True,
    package_data={'data_collection': ['raw_data/*.csv']},
)