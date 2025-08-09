from setuptools import setup, find_packages

setup(
    name='multisat',
    version='1.0.1',
    author='Sujal Bandodkar',
    author_email='sujalbandodkar05@gmail.com',
    description='A Python library to convert, resample, and harmonize satellite imagery across different sources.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/multisat',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'rasterio>=1.3.0',
        'numpy>=1.20',
        'gdal>=3.7.0',
        'scikit-image>=0.19',
        'matplotlib>=3.3',
    ],
    include_package_data=True,
)
