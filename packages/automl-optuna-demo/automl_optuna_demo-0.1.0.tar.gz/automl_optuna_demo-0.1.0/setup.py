
from setuptools import setup, find_packages

setup(
    name="automl_optuna_demo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "optuna",
        "scikit-learn"
    ],
)
