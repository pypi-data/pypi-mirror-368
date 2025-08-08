from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vn-address-converter",
    version="0.1.3",
    author="Bao Nguyen",
    author_email="qbao.nguyen@gmail.com",
    description="A Python package for converting and normalizing Vietnamese addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nqbao/vn-address-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy",
            "build",
        ],
    },
)
