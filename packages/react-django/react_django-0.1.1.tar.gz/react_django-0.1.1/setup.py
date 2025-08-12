from setuptools import setup, find_packages

setup(
    name="react_django",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "react_django=react_django.cli:main"
        ]
    },
    author="ISAAC EDZORDZI FIAVOR",
    author_email="isaacfiavor0611@gmail.com",
    description="CLI to scaffold fullstack React + Django + Tailwind projects",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/automated-fullstack-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
