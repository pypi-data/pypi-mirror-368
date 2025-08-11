import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pwdata", 
    version="0.5.4.dev2",
    author="LonxunQuantum",
    author_email="lonxun@pwmat.com",
    description="pwdata is a data pre-processing tool for MatPL, which can be used to extract features and labels. It also provides convenient interfaces for data conversion between different software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LonxunQuantum/pwdata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        "ase>=3.25.0",
        "ase-db-backends", 
        "lmdb", 
        "numpy", 
        "orjson", 
        "PyYAML", 
        "setuptools", 
        "tqdm", 
        "typing_extensions"
    ],
    entry_points={
        'console_scripts': [
            'pwdata = pwdata.main:main'
        ]
    }
)
