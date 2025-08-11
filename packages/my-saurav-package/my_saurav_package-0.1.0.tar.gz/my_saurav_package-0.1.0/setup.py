from setuptools import setup, find_packages

setup(
    name='my_saurav_package',
    version='0.1.0',
    author='Saurav kr',
    author_email='sauravgff@gmail.com',
    description='A sample Python package',
)
packages=find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
