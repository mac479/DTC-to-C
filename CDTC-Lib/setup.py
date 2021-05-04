from setuptools import find_packages, setup

setup(
    name='DTCTC',
    packages=find_packages(),
    version='1.2.2',
    description='Converts a SKLearn DTC model into executable c code. Also can create a test program to compile and test the exported code.',
    author='Myles Conlon'
)