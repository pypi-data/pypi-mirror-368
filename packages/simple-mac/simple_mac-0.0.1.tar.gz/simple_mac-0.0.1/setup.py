
from setuptools import setup

setup(
    name="simple-mac",  
    version="0.0.1",
    author="Harshil Bhatnagar", 
    author_email="harshilbhatnagar97@gmail.com",  
    description="An educational, non-secure MAC implementation using simple XOR.",
    py_modules=["simple_mac"],  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Education",
    ],
    python_requires=">=3.6",
)