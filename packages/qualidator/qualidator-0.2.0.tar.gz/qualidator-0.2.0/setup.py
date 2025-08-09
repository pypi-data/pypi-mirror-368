from setuptools import setup, find_packages

setup(
    name='qualidator',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'qualidator=qualidator.cli:cli',
        ],
    },
    author='Dima Frank',
    description='A lightweight data quality CLI tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
