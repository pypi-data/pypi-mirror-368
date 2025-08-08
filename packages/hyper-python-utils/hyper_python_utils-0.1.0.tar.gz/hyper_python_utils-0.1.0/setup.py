"""
Legacy setup.py for backward compatibility.
Modern packaging uses pyproject.toml, but this provides compatibility for older tools.
"""

from setuptools import setup, find_packages

setup(
    name="hyper-python-utils",
    use_scm_version=False,
    version="0.1.0"
)