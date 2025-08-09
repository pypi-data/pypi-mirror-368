from setuptools import setup, find_packages

setup(
    name="dircom",
    version="1.0.0",
    author="Nelson Almeida",
    author_email="ncamilo.so@gmail.com",
    description="CLI para listar portas seriais (COM/USB) no Windows, Linux e macOS",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ncamilo/dircom",
    py_modules=["dircom"],
    install_requires=[
        "pyserial>=3.5"
    ],
    entry_points={
        "console_scripts": [
            "dircom=dircom:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
