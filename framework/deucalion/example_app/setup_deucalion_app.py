from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Framework for exposing prometheus metrics to anomaly detection models.'

requirements = ['pandas', 'prometheus-client', 'requests', 'pyyaml', 'scikit-learn']

setup(
    name='deucalion',
    version=VERSION,
    author='Bavo Andriessen',
    author_email='bavo.andriessen@gmail.com',
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=requirements
)