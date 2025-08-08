from setuptools import setup, find_packages

VERSION="0.0.8"
DESCRIPTION="Pacote facilitador de criação de modelos"
LONG_DESCRIPTION="Esse pacote tem o objetivo de acelerar a criação de modelos de aprendizagem de máquina"
required_packages = [
    "pandas",
    "numpy",
    "scikit-learn",
    "imbalanced-learn",
    "optuna",
    "scikit-optimize",
    "catboost",
    "xgboost",
    "lightgbm",
    "tabulate",
]
setup(
	name="treinar_modelos_pns_2019",
	version=VERSION,
	author="Romario Gomes",
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	packages=find_packages(),
	install_requires=required_packages
)
