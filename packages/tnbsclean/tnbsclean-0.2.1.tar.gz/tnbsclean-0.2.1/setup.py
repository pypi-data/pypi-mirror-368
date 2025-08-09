from setuptools import setup, find_packages

setup(
    name="tnbsclean",
    version="0.2.1",
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
