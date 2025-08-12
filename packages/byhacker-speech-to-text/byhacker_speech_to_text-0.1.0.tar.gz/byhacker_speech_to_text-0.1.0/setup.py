from setuptools import setup, find_packages

setup(
    name="byhacker_speech_to_text", 
    version="0.1.0", 
    author="Romil Leuva",
    author_email="exmple@example.com",
    description="A speech-to-text package using Selenium browser listener",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/romil4648",
    packages=find_packages(),
    install_requires=[
        "selenium",
    ],
    python_requires=">=3.6",
)
