from setuptools import setup, find_packages

setup(
    name='noopy',
    version='0.10.0',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'my_command = noopy.module:main_func',
        ],
    },
)
