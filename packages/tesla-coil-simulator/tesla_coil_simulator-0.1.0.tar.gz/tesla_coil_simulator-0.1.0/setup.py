from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tesla-coil-simulator",
    version="0.1.0",
    author="Ricky Ding",
    author_email="e0134117@u.nus.edu",
    description="Physics simulator for DRSSTC (Dual Resonant Solid State Tesla Coils) with coupled RLC circuit analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TeslaCoilResearch/tesla-coil-simulator",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.8",
    license="MIT",
    keywords="tesla coil, DRSSTC, resonant circuit, RLC simulator, high voltage physics, electrical engineering, physics simulation, coupled resonators",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
)
