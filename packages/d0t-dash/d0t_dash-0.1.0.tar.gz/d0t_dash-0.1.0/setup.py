from setuptools import setup, find_packages

setup(
    name="d0t-dash",
    version="0.1.0",
    author="Parikshit Sonwane",
    author_email="parik.sonwane06@gmail.com",
    description="A simple CLI Morse Code encoder/decoder",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dit-dah=dit_dah.cli:main"
        ]
    },
    python_requires=">=3.6",
)