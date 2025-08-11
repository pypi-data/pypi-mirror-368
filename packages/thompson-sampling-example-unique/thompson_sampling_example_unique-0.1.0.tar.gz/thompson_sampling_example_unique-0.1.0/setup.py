
from setuptools import setup, find_packages

setup(
    name='thompson-sampling-example-unique', # Replace with a unique name
    version='0.1.0',
    description='A simple implementation of Thompson Sampling for the Multi-Armed Bandit problem.',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.6',
)
