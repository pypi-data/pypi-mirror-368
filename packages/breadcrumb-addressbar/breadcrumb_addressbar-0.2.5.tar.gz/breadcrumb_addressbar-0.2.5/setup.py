from setuptools import setup, find_packages  # type: ignore

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="breadcrumb-addressbar",
    version="0.2.4",
    author="scottlz0310",
    author_email="scott.lz0310@gmail.com",
    description=(
        "A breadcrumb-style address bar for PySide6/PyQt6 file managers "
        "with theme support"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scottlz0310/BreadcrumbAddressbar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.0.0",
        "qt-theme-manager>=0.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
    },
)
