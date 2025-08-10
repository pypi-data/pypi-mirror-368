from setuptools import setup, find_packages

setup(
    name="sportManagement",
    version="0.1.0",
    description="a stupid and impractical sport managing package, dont download it lol",
    author="Aaron Ethan",
    author_email="AaronOriginal2009@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)