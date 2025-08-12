from setuptools import setup, find_packages

setup(
    name="genaimath",
    version="0.1.0",
    description="Advanced mathematical operations with arbitrary-precision arithmetic.",
    author="SoftwareApkDev",
    author_email="softwareapkdev2022@gmail.com",
    license="MIT",
    packages=find_packages(),
    py_modules=["main"],
    install_requires=[],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

