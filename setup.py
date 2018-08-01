import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prymer",
    version="0.0.3",
    author="Zach Carlson",
    author_email="FxChiP@Gmail.com",
    description="prymer: Python-native data templating",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FxChiP/Prymer",
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        # I guess?
        "Topic :: Software Development :: Object Brokering"
    ),
)
