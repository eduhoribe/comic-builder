import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="comic-builder-eduhoribe",
    version="0.0.1",
    author="Eduwardo Horibe",
    author_email="eduhoribe@gmail.com",
    description="A tool to organize, merge and export comic pages into a ebook format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eduhoribe/comic-builder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
