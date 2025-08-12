from setuptools import setup, find_packages

setup(
    name="raggae",
    version="0.0.1",
    author="Okan Yenigün",
    author_email="okanyenigun@gmail.com",
    description="A dummy placeholder package for raggae.",
    long_description="This is a placeholder package for raggae.",
    long_description_content_type="text/markdown",
    url="https://github.com/okanyenigun/raggae",
    packages=find_packages(),
    classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
)
