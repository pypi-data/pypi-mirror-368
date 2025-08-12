from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
    
setup(
    name='simple_gedcom',
    version='1.0.5',
    description='A Python module for reading and extracting data from GEDCOM files.',
    author='mcobtechnology',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcobtechnology/simple-gedcom",    
    license='GPLv2',
    keywords='python gedcom',
    packages=find_packages(),
    python_requires=">=3.6",
    extras_require={
        'test': ['pytest'],
    },    
)
