from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='novalang',
    version="2.2.1",
    description='NovaLang - Universal Programming Language with Enhanced Parser and AUTO_MYSQL_BACKEND Support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='martinmaboya',
    author_email='martinmaboya@gmail.com',
    url='https://github.com/martinmaboya/novalang',
    packages=find_packages(),
    py_modules=[
        'main',
        'lexer', 
        'parser',
        'interpreter',
        'compiler',
        'nova_cli',
        'novalang_runtime',
        'novalang_auto_main',
        'stdlib',
        'array_assign_node',
        'array_nodes',
        'for_node',
        'nova',
        'simple_parser',
        'hybrid_parser',
        'enhanced_parser',
        'working_demo'
    ],
    entry_points={
        'console_scripts': [
            'novalang = novalang_runtime:main',
            'nova = novalang_runtime:main',
            'nova-cli = nova_cli:main',
            'nova-runtime = novalang_runtime:main',
            'novalang-lsp = novalang.lsp_server:main'
        ]
    },
    install_requires=[
        'argparse>=1.4.0',
        'dataclasses;python_version<"3.7"',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'database': [
            'psycopg2-binary>=2.8.0',  # PostgreSQL
            'pymongo>=4.0.0',          # MongoDB
            'redis>=4.0.0',            # Redis
            'elasticsearch>=8.0.0',    # Elasticsearch
            'neo4j>=5.0.0',            # Neo4j
            'cassandra-driver>=3.25.0', # Cassandra
            'influxdb-client>=1.30.0', # InfluxDB
        ],
        'all': [
            'pytest>=6.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'psycopg2-binary>=2.8.0',
            'pymongo>=4.0.0',
            'redis>=4.0.0',
            'elasticsearch>=8.0.0',
            'neo4j>=5.0.0',
            'cassandra-driver>=3.25.0',
            'influxdb-client>=1.30.0',
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords="programming-language database sql nosql mysql postgresql mongodb redis elasticsearch neo4j cassandra influxdb oracle sqlserver artificial-intelligence machine-learning blockchain cloud-native microservices enterprise universal-database orm jpa hibernate vector-database graph-database time-series search-engine compiler interpreter",
    project_urls={
        "Bug Reports": "https://github.com/martinmaboya/novalang/issues",
        "Source": "https://github.com/martinmaboya/novalang",
        "Documentation": "https://martinmaboya.github.io/novalang",
        "VS Code Extension": "https://marketplace.visualstudio.com/items?itemName=martinmaboya.novalang",
        "Language Server": "https://github.com/martinmaboya/novalang/tree/master/extensions/language-server",
    }
)
