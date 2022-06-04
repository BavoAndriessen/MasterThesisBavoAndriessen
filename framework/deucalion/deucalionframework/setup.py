from setuptools import setup, find_packages

VERSION = '3.0.3'
DESCRIPTION = 'Framework for exposing prometheus metrics to anomaly detection models.'


setup(
    name='deucalion',
    version=VERSION,
    author='Bavo Andriessen',
    author_email='bavo.andriessen@gmail.com',
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['prometheus-client', 'requests', 'pyyaml', 'certifi', 'six', 'python_dateutil', 'urllib3', 'kubernetes']
)
