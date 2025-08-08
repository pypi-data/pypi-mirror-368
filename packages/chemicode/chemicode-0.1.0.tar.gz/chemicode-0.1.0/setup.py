from setuptools import setup, find_packages

setup(
    name="chemicode",
    version="0.1.0",
    author="Prakritee Chakraborty",
    author_email="kriti.guitar@gmail.com",
    description="A C++-styled chemical programming language interpreter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "chemicode=chemicode.interpreter:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
