from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="kocha",
    version="v1.0.0",
    description="Chat application for the terminal.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Daniel Schmitt",
    python_requires=">=3.6.0",
    license=license,
    packages=find_packages()
)
