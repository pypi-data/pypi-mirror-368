from setuptools import setup, find_packages

setup(
    name='Rolling_Imax_Processor',
    version='0.1.2',  # version must be a string
    author='Akshar Singh Rawat, Dr Sadikul Islam, Dr M Muruganandam',  # quotes needed
    author_email='aksharrawat1@gmail.com',  # quotes needed
    description='Processes raw intensity data stored in a nested Year/Month/Day folder structure. Reads per-minute rainfall breakpoint data (mm/min) from Excel files named dd-mm-yyyy.xlsx. Calculates rolling maximum values for intensity classes I1 to I60 and outputs the results in mm/min.',
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
