from setuptools import setup,find_packages
from setuptools.command.build_ext import build_ext
from flowpylib import __version__ as versionInfo
setup(
    name='flowpylib',
    version=versionInfo,
    description='Python Library for Transaction Cost Analysis and Market Simulation',
    author='Jialue Chen',
    author_email='jialuechen@outlook.com',
    url='https://github.com/jialuechen/flowpylib',
    packages=find_packages(),
    install_requires=[
        'ollama','pandas', 'matplotlib', 'plotly', 'bokeh', 'dash', 'flask', 'pybind11', 'numpy', 'geopandas', 'scikit-learn', 'textblob', 'requests','jax', 'web3'
    ],
    cmdclass={'build_ext': build_ext},
)

