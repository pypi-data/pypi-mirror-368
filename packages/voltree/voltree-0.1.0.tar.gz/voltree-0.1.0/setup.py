from setuptools import setup, find_packages

setup(
    name="voltree",
    version="0.1.0",
    author="volttome",
    author_email="volttome@gmail.com",
    description="Create folder/file structures instantly using CLI commands",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/volttome/voltree",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "voltree=voltree.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console"
    ],
    python_requires=">=3.7",
)