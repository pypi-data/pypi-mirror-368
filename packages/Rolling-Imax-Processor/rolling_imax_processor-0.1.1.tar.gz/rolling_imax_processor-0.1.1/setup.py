from setuptools import setup, find_packages

setup(
    name='Rolling_Imax_Processor',
    version='0.1.1',  # version must be a string
    author='Akshar Singh Rawat, Dr Sadikul Islam, Dr M Muruganandam',  # quotes needed
    author_email='aksharrawat1@gmail.com',  # quotes needed
    description='This script processes raw intensity measurement data stored in a nested Year to Month to Day folder structure. It reads data in millimeters per second (mm/sec) from Excel files, calculates rolling maximum values for intensity classes, and outputs results in millimeters per minute (mm/min) for intensity classes I1 to I60.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
