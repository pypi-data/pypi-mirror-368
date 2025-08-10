from setuptools import setup, find_packages

setup(
    name="megarnucleusx13",
    version="0.0.1",
    author="Tu Nombre",
    description="MeganR Nucleus X13 - Mini IA en Python",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "megan=clip:main"
        ]
    },
)
