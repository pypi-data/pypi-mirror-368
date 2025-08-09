from setuptools import setup, find_packages

setup(
    name="pckgr",
    version="0.0.1",
    description="A package creation tool for Python projects.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nichola Walch",
    author_email="littler.compression@gmail.com",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={},
    install_requires=["numpy", "toml"],
    entry_points={
        "console_scripts": [
            "pckgr=pckgr.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
