from setuptools import setup, find_packages

setup(
    name="fhir_flex",
    version="2.0.0",
    author="Bhushan Varade",
    author_email="bvarade02@gmail.com",
    description="A flexible library to simplify and map FHIR Patient objects to custom JSON schemas.",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="fhir patient json healthcare flexible",
)


