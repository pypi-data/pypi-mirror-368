from setuptools import setup, find_packages
import pathlib

# قراءة README
here = pathlib.Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="PySEMO",
    version="0.5",
    packages=find_packages(include=["PySEMO", "PySEMO.*"]),
    include_package_data=True,
    install_requires=[
        "pycryptodome"
    ],
    description="TikTok signing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kameran",
    author_email="hh@gmail.com",
    license="MIT",
    python_requires=">=3.6",
)