from setuptools import setup, find_packages

setup(
    name="emcee_rapper",
    version="1.0.0",
    description="A wrapper around emcee with plotting tools",
    author="Cat, Thomas, Anthony, Andres",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "corner",
        "matplotlib",
        "emcee",
        "scipy"
    ],
    python_requires=">=3.10",
)
