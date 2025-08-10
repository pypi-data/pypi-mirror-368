import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="random_container_with_url_info",
    version="0.0.2",
    author="Mateusz Konieczny",
    author_email="matkoniecz@tutanota.com",
    description="random_container_with_url_info",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/matkoniecz/random_container_with_url_info",
    packages=setuptools.find_packages(),
    license = "MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # for dependencies syntax see https://python-packaging.readthedocs.io/en/latest/dependencies.html
) 
