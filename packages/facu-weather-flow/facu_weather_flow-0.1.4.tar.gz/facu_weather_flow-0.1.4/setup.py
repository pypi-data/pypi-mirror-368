from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='facu-weather-flow',
    version='0.1.4',
    description='ETL para extraer, transformar y cargar datos del clima en S3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter Facundo Vega',
    author_email='facundo.vega1234@gmail.com',
    url='https://github.com/facuvegaingenieer/weather-flow.git',
    packages=find_packages(include=["facu_weather_flow", "facu_weather_flow.*"]),
    install_requires=[
        'pandas',
        'boto3',
        'pyarrow',
        'python-dotenv',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'weatherflow = facu_weather_flow.main:main',
        ],
    },
    python_requires='>=3.8',
)