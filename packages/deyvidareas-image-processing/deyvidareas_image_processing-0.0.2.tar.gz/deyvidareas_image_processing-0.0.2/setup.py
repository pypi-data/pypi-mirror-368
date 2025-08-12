from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="deyvidareas_image_processing", 
    version="0.0.2",
    author="DeyvidArêas",
    author_email="deyvidsilva.areas@gmail.com",
    description="My image processing program.",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deyvidareas/image_processing.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)