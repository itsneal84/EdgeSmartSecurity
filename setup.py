from setuptools import find_packages, setup


setup(
    name='setup.py',
    version='1.0',
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    author='nealn',
    description='Edge Smart Security'
)
