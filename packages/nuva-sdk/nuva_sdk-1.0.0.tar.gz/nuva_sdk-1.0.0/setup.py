from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nuva-sdk",
    version="1.0.0",
    author="NUVA Team",
    author_email="contact@nuva.fr",
    description="Unified Vaccine Nomenclature (NUVA) Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nuva/nuva-libs",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "protobuf>=3.20.0",
        "requests>=2.25.0",
    ],
    keywords="vaccine, vaccination, nomenclature, healthcare, immunization",
    project_urls={
        "Bug Reports": "https://github.com/nuva/nuva-libs/issues",
        "Source": "https://github.com/nuva/nuva-libs",
        "Documentation": "https://nuva.fr/docs",
    },
)
