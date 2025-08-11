from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="piyush-math-calculator",  # Name of your package
    version="0.1.0",
    author="Piyush Borakhade",  # Replace with your name
    author_email="your.email@example.com",  # Replace with your email
    description="A simple math utilities package for basic operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/piyushborakhade/piyush-math-calculator",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Add dependencies here if needed
        # e.g., "numpy>=1.19.0",
    ],
    entry_points={
        "console_scripts": [
            "mymath-demo=main:main",
        ],
    },
)
