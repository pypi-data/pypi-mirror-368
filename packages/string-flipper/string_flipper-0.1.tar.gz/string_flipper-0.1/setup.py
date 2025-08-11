
from setuptools import setup, find_packages
with open('README.md', 'r') as f:
    desc = f.read()
setup(
    name='string_flipper',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Your Name',
    description='A tiny Python library to flip (reverse) strings.',
    python_requires='>=3.6',
    url='https://pypi.org/project/string_flipper/',  # Optional
)
