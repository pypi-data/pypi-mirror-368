from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as f:
    description = f.read()
setup(
    name='xlql',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
        "duckdb>=1.3.2",
        "questionary>=2.1.0",
        "tabulate>=0.9.0",
        "pandas>=2.3.1"
    ],
    entry_points={
        'console_scripts': [
            'xlql=xlql.cli:main',
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
