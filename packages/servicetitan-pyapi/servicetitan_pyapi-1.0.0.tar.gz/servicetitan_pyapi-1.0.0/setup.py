from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="servicetitan-pyapi",
    version="1.0.0",
    author="Brian Handrigan",
    author_email="brian@n90.co",
    description="A comprehensive Python client library for the ServiceTitan API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/n90-co/servicetitan-pyapi",
    project_urls={
        "Bug Reports": "https://github.com/n90-co/servicetitan-pyapi/issues",
        "Source": "https://github.com/n90-co/servicetitan-pyapi",
        "Documentation": "https://github.com/n90-co/servicetitan-pyapi#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock",
            "requests-mock",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "pandas>=1.4.0",
            "matplotlib>=3.5.0",
        ],
        "testing": [
            "pytest>=7.0.0",
            "pytest-mock",
            "requests-mock",
            "pytest-cov>=3.0.0",
            "pytest-xdist",
        ],
    },
    keywords="servicetitan api client hvac plumbing field-service crm",
    include_package_data=True,
    zip_safe=False,
)