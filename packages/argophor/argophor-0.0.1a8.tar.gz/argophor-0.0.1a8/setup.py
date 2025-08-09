from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="argophor",
    version="0.0.1a8",
    author="Muhammed Shafin P",
    author_email="hejhdiss@gmail.com",
    description="Argophor - detection and install helper tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hejhdiss/argophor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    license="Argophor License 1.0",
    license_files=('LICENSE',),
)
