from setuptools import setup, find_packages

setup(
    name="topsis-Mridul",  # More appropriate name for PyPI
    version="1.0.0",
    author="Mridul Mahajan",
    author_email="mridulmahajan16@gmail.com",  # Update with your actual email
    description="A Python implementation of the TOPSIS decision-making method",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mridulmahajan04/Topsis_Package/",  # Update with your actual repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
        "Bug Reports": "https://github.com/mridulmahajan04/Topsis_Package/issues",
        "Source": "https://github.com/mridulmahajan04/Topsis_Package/",
    },
)
