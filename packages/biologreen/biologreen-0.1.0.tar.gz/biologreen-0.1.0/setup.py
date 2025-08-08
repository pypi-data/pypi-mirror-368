from setuptools import setup, find_packages

setup(
    name="biologreen",
    version="0.1.0",
    author="AtuhurraSolomon", 
    author_email="atuhurrasolomon47@gmail.com", 
    description="The official Python SDK for the Bio-Logreen Facial Authentication API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AtuhurraSolomon/biologreen-python-sdk", 
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "pydantic>=2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
