import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Backtester_Tushar",
    version="0.0.1",
    author="Tushar Sarkar",
    author_email="tusharsarkar866@gmail.com",
    description="Backtesting Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tusharsarkar3/Backtester_Tushar",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
