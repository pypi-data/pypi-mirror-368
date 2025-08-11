from setuptools import setup, find_packages

setup(
    name="topsis-krishna",  # Better package name for PyPI
    version="1.0.1",  # Incremented version
    author="Krishna Arora",
    author_email="your.email@example.com",  # Update this with your actual email
    description="A Python implementation of the TOPSIS decision-making method",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/topsis-package",  # Add your repository URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:main",
        ],
    },
    python_requires=">=3.6",
    keywords="topsis, decision-making, multi-criteria, ranking, optimization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/topsis-package/issues",
        "Source": "https://github.com/yourusername/topsis-package",
        "Documentation": "https://github.com/yourusername/topsis-package#readme",
    },
)