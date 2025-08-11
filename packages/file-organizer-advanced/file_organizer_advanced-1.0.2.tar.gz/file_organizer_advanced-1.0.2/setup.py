from setuptools import setup, find_packages
import pathlib

# Read README file for long description
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="file-organizer-advanced",  # Must be unique on PyPI
    version="1.0.2",
    description="A CLI tool to automatically organize files into categorized folders",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Vikram Mistry",
    author_email="mvikram43@gmail.com",  # replace with your email
    url="https://github.com/vikram-mistry/file-organizer",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "file-organizer-advanced=file_organizer.main:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        #"License :: OSI Approved :: MIT License",
    ],
)