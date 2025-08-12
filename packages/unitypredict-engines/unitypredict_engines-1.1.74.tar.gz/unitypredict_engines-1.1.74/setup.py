from setuptools import setup, find_packages
import os, sys


packageVersion = os.getenv("PyLibVersion", "0.0.1")
print ("Setting up package version: {}".format(packageVersion))


description = ""
with open("README.md", "r") as rdf:
    description = rdf.read()

print ("Possible packages: {}".format(find_packages()))

setup (
    name="unitypredict_engines",
    version=packageVersion,
    packages=find_packages(),
    install_requires=[
        "attr",
        "cattrs",
        "requests",
    ],
    entry_points = {          # this here is the magic that binds your function into a callable script
        'console_scripts': 
        [
            'unitypredict=unitypredict_engines.scripts:main'
        ],
    },
    description=" ",
    long_description=description,
    long_description_content_type="text/markdown",
    license=" ",
    url="https://unitypredict.com",
    author="UnityPredict"
)
