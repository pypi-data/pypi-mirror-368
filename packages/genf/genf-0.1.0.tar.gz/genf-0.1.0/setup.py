from setuptools import setup, find_packages

setup(
    name="genf",  # Nama paket di PyPI
    version="0.1.0",  # Versi awal
    author="marhaendev",
    author_email="marhaendev@gmail.com",
    description="Extract file names and contents from a directory",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://marhaendev.com",  # URL utama
    py_modules=["genf"],  # Modul Python
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'genf=genf:main',  # Membuat perintah `genf` di CLI
        ],
    },
)