from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="capture_hc",
    version="0.1.0",
    description="A simple, user-friendly Python client for sending events and traces to Honeycomb, with decorator support for timing and custom fields.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Amit Singh Sansoya",
    author_email="tusharamit@yahoo.com",
    maintainer="Amit Singh Sansoya",
    maintainer_email="tusharamit@yahoo.com",
    url="https://github.com/yourusername/capture_hc",  # Update with actual repo if available
    packages=find_packages(),
    install_requires=["libhoney"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
)
