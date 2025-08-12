from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="clipd",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "clipd = clipd.main:app"
        ]
    },
    python_requires=">=3.8",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yadhnika Wakde",
    author_email="yadhnikawakde@gmail.com",
    url="https://github.com/SuzanTurner/clipd",
    project_urls={
        "Bug Tracker": "https://github.com/SuzanTurner/clipd/issues",
        "Documentation": "https://github.com/SuzanTurner/clipd#readme",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)
