from setuptools import setup, find_packages

setup(
    name="wb-writeupbuilder",
    version="1.0.2",
    description="Builds Writup with your input.",
    author="[Ph4nt01]",
    author_email="ph4nt0.84@gmail.com",
    url="https://github.com/Ph4nt01/WB-WriteupBuilder",
    packages=find_packages(),
    install_requires=[
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "wb=wb.cli:main"
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)
