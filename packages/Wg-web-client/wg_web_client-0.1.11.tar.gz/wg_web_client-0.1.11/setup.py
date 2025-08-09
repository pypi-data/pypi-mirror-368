from setuptools import setup, find_packages

setup(
    name='Wg_web_client',
    version='0.1.11',
    description='WireGuard automation client with async support using Selenium and aiohttp',
    author='Zurlex',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',
        'webdriver-manager>=4.0.0',
        'aiohttp>=3.8.0',
    ],
)
