from setuptools import setup, find_packages

setup(
    name="sportsipy-dashboard",
    version="0.1.0",
    description="Interactive web dashboard for sportsipy data exploration",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "sportsipy>=0.7.0",
        "dash>=2.14.0",
        "dash-mantine-components>=0.14.0",
        "dash-ag-grid>=31.0.0",
        "dash-iconify>=0.1.2",
        "pandas>=2.2.0",
        "numpy>=2.0.0",
        "openpyxl>=3.1.0",
        "pyarrow>=15.0.0",
        "lxml>=5.2.0",
        "nbformat>=5.9.0",
        "flask>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "sportsipy-dashboard=sportsipy_dashboard.app:main",
        ],
    },
)
