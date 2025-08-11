from setuptools import setup, find_packages

setup(
    name='xlql',
    version='0.3.0',
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
)
