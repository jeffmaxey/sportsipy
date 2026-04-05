from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('VERSION', 'r') as f:
    version = f.read()

setup(
    name='sportsipy',
    version=version,
    author='Robert Clark',
    author_email='robdclark@outlook.com',
    description='A free sports API written for python',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='MIT',
    url='https://github.com/roclark/sportsipy',
    packages=find_packages(),
    python_requires='>=3.10',
    keywords='stats sports api sportsipy machine learning',
    install_requires=[
        "numpy >= 2.0.0",
        "pandas >= 2.2.0",
        "pyquery >= 2.0.0",
        "requests >= 2.32.0"
    ],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
)
