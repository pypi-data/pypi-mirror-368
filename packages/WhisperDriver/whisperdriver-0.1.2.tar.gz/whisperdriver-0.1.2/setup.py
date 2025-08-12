from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="WhisperDriver",
    version="0.1.2",
    description="Automation and API library for WhisperTrades.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Paul Nobrega",
    author_email="Paul@PaulNobrega.net",
    url="https://github.com/PaulNobrega/WhisperDriver",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
