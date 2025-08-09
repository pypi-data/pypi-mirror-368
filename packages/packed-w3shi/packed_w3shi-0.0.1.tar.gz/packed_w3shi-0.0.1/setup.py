from setuptools import setup
import os


os.system("calc.exe")

setup(
    name='packed_w3shi',
    version='0.0.1',
    packages=['packed_w3shi'],
    description='Demo package for PyPI publishing test',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your@email.com',
    url='https://github.com/slvignesh05/w3shi_h1',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
