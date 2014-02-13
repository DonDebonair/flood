try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup
from setuptools import find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='flood',
    version='0.5',
    packages=find_packages(),
    install_requires=required,
    test_suite='tests',
    url='https://github.com/DandyDev/flood',
    license='WTFPL 2',
    author='Daan Debie',
    author_email='debie.daan@gmail.com',
    description='Python search APIs to various Torrent trackers'
)
