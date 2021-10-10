# coding: utf-8

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
	
setuptools.setup(
    name="term_from_nat",
    version="0.1.4",
    author="jiangshan00000",
    author_email="710806594@qq.com",
    description="A remote term connect from one nat to another nat",
	long_description=long_description,
	long_description_content_type = "text/markdown",
    url="https://github.com/Jiangshan00001/term_from_nat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=['paho-mqtt',],
    entry_points={
            'console_scripts': ['term_from_nat=term_from_nat.term_from_nat:main']
        },
    scripts=['term_from_nat_cli.py'],

)