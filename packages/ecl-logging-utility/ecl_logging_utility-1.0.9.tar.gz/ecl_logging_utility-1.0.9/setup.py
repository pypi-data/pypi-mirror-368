from setuptools import setup, find_packages

setup(
    name="ecl-logging-utility",
    version="1.0.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "structlog>=23.1.0",
        "python-json-logger>=2.0.2",
        "opensearch-py==2.4.2",
    ],
    python_requires=">=3.8",
    description="Internal structured logging utility for ECL microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)