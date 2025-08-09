# setup.py
from setuptools import setup, find_packages

setup(
    name='render9',
    version='0.0.111',
    description="Render9 OTP is a lightweight and easy-to-use Python package for sending OTP messages via the Render9 OTP API.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
    ],
)