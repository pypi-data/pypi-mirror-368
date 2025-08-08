from setuptools import setup, find_packages

setup(
    name='lispy',
    version='0.0.1',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'my_command = lispy.module:main_func',
        ],
    },
)
