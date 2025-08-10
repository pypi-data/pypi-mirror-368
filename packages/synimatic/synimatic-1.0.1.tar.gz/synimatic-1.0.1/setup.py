from setuptools import setup, find_packages

setup(
    name="synimatic",
    version="1.0.1",
    description="Simple and effective matplotlib animation wrapper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jonathan Ayalew",
    url="https://github.com/jonathan-4a/synimatic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=["matplotlib>=3.7.0", "tqdm>=4.66.5"],
    extras_require={"jupyter": ["ipython"]},
)
