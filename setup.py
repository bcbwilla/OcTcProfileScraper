from setuptools import setup, find_packages

setup(
    name="OcTcProfileScraper",
    version="0.1.0",
    description="Get player information from their profile on http://www.oc.tc",
    url="https://github.com/bcbwilla/OcTcProfileScraper",
    author="bcbwilla",
    license="MIT",
    install_requires=['beautifulsoup4'],
    packages=find_packages()
)
