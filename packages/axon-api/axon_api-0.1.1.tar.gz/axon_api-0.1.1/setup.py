from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axon-api",
    version="0.1.1",
    author="Shane Bellone",
    author_email="axon@bellone.com",
    description="Zero-dependency WSGI framework with request batching and multipart streaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shanebellone/axon-api",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11", 
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
    ],
    packages=find_packages(),
    python_requires=">=3.10",
    license="MIT",
)
