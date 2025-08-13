from setuptools import setup, find_packages

setup(
    name="byhacker_speech_to_text",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "selenium"
    ],
    author="Romil Leuva",
    author_email="example@example.com",
    description="A speech-to-text package using Selenium browser listener",
    url="https://github.com/romil4648/byhacker_speech_to_text",
)
