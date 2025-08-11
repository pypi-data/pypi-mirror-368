from setuptools import setup, find_packages


def get_requirements():
    """
    Your dependencies must be listed in a requirements.txt file inside the
    root directory.

    The comments will be ignored.
    """
    with open("requirements.txt", "r", encoding="UTF-8") as file:
        lines = list(map(lambda line: line.replace("\n", "").strip(), file.readlines()))
        valid_packages = list(filter(lambda line: not line.startswith("#"), lines))
        return valid_packages


def get_long_description():
    """
    Remember to updated README.md describing your project.

    It's going to be used on your Pypi page.
    """

    with open("README.md", "r", encoding="UTF-8") as file:
        return file.read()


setup(
    name="aer_plugin",
    version="0.0.2",
    install_requires=get_requirements(),
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Quantum Computing",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: System",
        "Topic :: System :: Hardware",
    ],
    url="https://github.com/Dpbm/aer-plugin",
    license="MIT",
    author="Dpbm",
    author_email="dpbm136@gmail.com",
    description="A quantum plugin for qiskit AER",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    include_package_data=True,
)
