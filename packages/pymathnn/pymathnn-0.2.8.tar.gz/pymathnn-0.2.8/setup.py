from setuptools import setup, find_packages

setup(
    name="pymathnn",
    version="0.2.8",
    author="Daniele Frulla",
    author_email="daniele.frulla@newstechnology.eu",  
    description="Python module for mathematical operations, matrix manipulations and neural network utilities using NumPy",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="math numpy matrix neural network ai deep learning algebra cuda cupy transformer machine ",
    python_requires=">=3.7",
)
