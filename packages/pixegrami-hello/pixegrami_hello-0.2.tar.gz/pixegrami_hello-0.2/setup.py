from setuptools import setup, find_packages

setup(
    name="pixegrami_hello",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        #Add dependecies here.
        #e.g. 'numpy>=1.11.1'
    ],
    entry_points={
        "console_scripts":[
            "pixegrami_hello = pixegrami_hello:hello",
        ],
    },
)