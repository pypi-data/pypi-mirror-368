from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='track-flow',
    version='0.1.9',
    description='ETL para extraer, transformar y cargar datos de charts de spotify en S3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter Facundo Vega',
    author_email='facundo.vega1234@gmail.com',
    url='https://github.com/facuvegaingenieer/track-flow',
    license='MIT', 
    packages=find_packages(),
    install_requires=[
        'pandas',
        'boto3',
        'pyarrow',
        'python-dotenv',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'trackflow=track_flow.main:main',
        ],
    },
    python_requires='>=3.8',
    
    classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
],
)