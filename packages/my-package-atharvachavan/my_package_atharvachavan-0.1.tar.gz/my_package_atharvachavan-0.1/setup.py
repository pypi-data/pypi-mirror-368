
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='my_package_atharvachavan',   # Your unique PyPI name
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'nltk',
    ],
    long_description=description,
    long_description_content_type='text/markdown'
)

    