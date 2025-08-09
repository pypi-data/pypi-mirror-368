from setuptools import setup, find_packages
import os

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='powerbanktau',
    version='0.2.1',
    description='Dask cluster utilities for HPC environments',
    long_description='A Python package providing utilities for managing Dask clusters on HPC systems with PBS/SLURM schedulers',
    packages=find_packages(),
    author='Nicolas Lynn',
    author_email='nicolaslynn@mail.tau.ac.il',
    license='BSD 2-clause',
    scripts=[os.path.join('powerbanktau/scripts', file) for file in os.listdir('powerbanktau/scripts')],
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Clustering',
    ],
)