from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dummypy",
    version="0.1.0",
    author="Mark Richardson",
    author_email="mrichardson82@gmail.com",
    description="DummyPy Analytics - Demo Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markrichardson/dummypy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy>=2.2",
        "scipy>=1.15",
        "pandas>=2.2",
        "attrs>=25.3",
        "matplotlib>=3.10",
        "seaborn>=0.13",
        "statsmodels>=0.14.0",
    ],
)
