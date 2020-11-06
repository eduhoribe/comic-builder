import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = [req.strip() for req in fh.readlines()]

setuptools.setup(
    name="comic-builder",
    version="0.0.22",
    author="Eduwardo Horibe",
    author_email="eduhoribe@gmail.com",
    description="A tool to organize, merge and export comic pages into a ebook format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eduhoribe/comic-builder",
    packages=setuptools.find_packages(exclude=(
        'tests',
    )),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'comic-builder = comic_builder.__main__:main',
            'comic-metadata-injector = comic_metadata.metadata_injector:main',
            'comic-metadata-ejector = comic_metadata.metadata_ejector:main',
            'kindlegen_installer = kindlegen_installer.kindlegen_installer:main',
        ]
    },
)
