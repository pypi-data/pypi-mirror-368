from setuptools import setup, find_packages

setup(
    name="steelopg",
    version="0.1.0",
    author="steeldev",
    author_email="toilet@smasher.com",
    description="a simple oxapay payment gateway helper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/steeldevlol/Steel-s-Oxapay-Payment-Gateway",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)