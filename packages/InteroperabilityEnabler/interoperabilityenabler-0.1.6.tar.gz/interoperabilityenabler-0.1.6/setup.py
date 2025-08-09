from setuptools import setup, find_packages

setup(
    name="InteroperabilityEnabler",
    version="v0.1.6",
    author="Shahin ABDOUL SOUKOUR",
    author_email="abdoul-shahin.abdoul-soukour@inria.fr",
    description="Interoperability Enabler",
    long_description=open("README_package.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sedimark/InteroperabilityEnabler",
    license="",
    packages=find_packages(
        include=["InteroperabilityEnabler", "InteroperabilityEnabler.*"],
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["numpy", "pandas", "python-dateutil", "pytz", "six", "tzdata", "xlrd"],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    include_package_data=True,
)