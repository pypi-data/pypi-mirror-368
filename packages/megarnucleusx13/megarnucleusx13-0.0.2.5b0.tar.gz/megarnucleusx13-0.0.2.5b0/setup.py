from setuptools import setup, find_packages

setup(
    name="megarnucleusx13",
    version="0.0.2.5b0",
    author="Tu Nombre",
    author_email="tuemail@example.com",
    description="MeganR Nucleus X13 - IA experimental en desarrollo",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/megarnucleusx13/",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
