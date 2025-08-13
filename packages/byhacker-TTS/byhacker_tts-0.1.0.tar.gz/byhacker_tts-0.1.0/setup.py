from setuptools import setup, find_packages

setup(
    name="byhacker_TTS",
    version="0.1.0",
    description="A Selenium-based text-to-speech automation package.",
    author="Romil Leuva",
    author_email="exmple@gmail.com",
    packages=find_packages(),
    install_requires=[
        "selenium",
    ],
    python_requires='>=3.7',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
)
