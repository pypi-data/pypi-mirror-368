from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='novalang',
    version='1.0.3',
    description='NovaLang - Cross-platform programming language. Write once, run everywhere.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='martinmaboya',
    author_email='martinmaboya@gmail.com',
    url='https://github.com/martinmaboya/novalang-vscode',
    packages=find_packages(),
    py_modules=[
        'main',
        'lexer', 
        'parser',
        'interpreter',
        'stdlib',
        'array_assign_node',
        'array_nodes',
        'for_node',
        'nova'
    ],
    entry_points={
        'console_scripts': [
            'novalang = main:main',
            'nova = nova:main'
        ]
    },
    install_requires=[
        'argparse>=1.4.0',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="programming-language cross-platform web mobile desktop interpreter compiler",
    project_urls={
        "Bug Reports": "https://github.com/martinmaboya/novalang-vscode/issues",
        "Source": "https://github.com/martinmaboya/novalang-vscode",
        "Documentation": "https://github.com/martinmaboya/novalang-vscode/wiki",
    }
)
