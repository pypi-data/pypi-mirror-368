from setuptools import setup, find_packages

setup(
    name="PySEMO",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "pycryptodome"
    ],
    description="TikTok signing library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Kameran",
    author_email="hh@gmail.com",
    license="MIT",
)