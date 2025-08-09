from setuptools import setup, find_packages
import numpy as np
import matplotlib.pyplot as plt
import mne


setup(
    name="tnbsclean",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "mne",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",  # License name, not a dict
    license_files=["LICENSE"],  # Ensure LICENSE is included
)
