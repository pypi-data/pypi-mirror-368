from setuptools import setup, find_packages

setup(
    name="NetVizCorpy",
    version="0.1.7",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "pycountry",
        "pycountry-convert",
        "pyvis",
        "seaborn",
        "matplotlib",
        "collections",

        # any other dependencies
    ],

    author="Zsofia Baruwa",
    author_email="zb78@kent.ac.uk",
    description="Visualise corporate relationships using WikiData in multi-level B2B networks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zb15/NetVizCorpy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)