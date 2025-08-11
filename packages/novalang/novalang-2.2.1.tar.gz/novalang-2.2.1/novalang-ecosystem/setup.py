from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="novalang",
    version="1.0.0",
    author="Martin Maboya",
    author_email="martinmaboya@gmail.com",
    description="NovaLang - The Full-Stack Programming Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martinmaboya/novalang",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "novalang=src.main:main",
            "nova=src.main:main",
            "novalang-lsp=extensions.language-server.novalang_lsp:main"
        ],
    },
)