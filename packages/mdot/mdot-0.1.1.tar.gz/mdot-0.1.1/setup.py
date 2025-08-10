from setuptools import setup, find_packages

setup(
    name="mdot",  # This will be the pip install name
    version="0.1.1",
    author="Parikshit Sonwane",
    author_email="parik.sonwane06@gmail.com",
    description="A simple CLI Morse Code encoder/decoder",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mdot=mdot.main:main"
        ]
    },
    python_requires=">=3.6",
)
