from setuptools import setup, find_packages

setup(
    name="rlbandit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0"
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)
