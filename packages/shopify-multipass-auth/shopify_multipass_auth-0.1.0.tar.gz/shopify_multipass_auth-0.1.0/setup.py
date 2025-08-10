"""Setup configuration for shopify-multipass package."""

from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "docs" / "README.md").read_text()

# Read the requirements file
REQUIREMENTS = (HERE / "requirements.txt").read_text().strip().split("\n")

setup(
    name="shopify-multipass-auth",
    version="0.1.0",
    description="A Python library for generating Shopify multipass tokens for customer authentication",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/autonomous-tech/shopify-multipass-auth",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security :: Cryptography",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires=">=3.7",
    keywords="shopify multipass authentication ecommerce",
    project_urls={
        "Bug Reports": "https://github.com/autonomous-tech/shopify-multipass-auth/issues",
        "Source": "https://github.com/autonomous-tech/shopify-multipass-auth",
        "Documentation": "https://github.com/autonomous-tech/shopify-multipass-auth#readme",
    },
)
