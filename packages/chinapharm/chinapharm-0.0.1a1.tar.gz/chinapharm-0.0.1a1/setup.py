from setuptools import setup, find_packages

setup(
    name="chinapharm",
    version="0.0.1a1",
    author="ChinaPharm Team",
    author_email="team@chinapharm.org",
    description="China pharmaceutical industry toolkit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chinapharm/chinapharm",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.3.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
