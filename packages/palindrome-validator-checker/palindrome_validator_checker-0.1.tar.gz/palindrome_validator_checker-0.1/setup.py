
from setuptools import setup, find_packages
with open('README.md', 'r') as f:
    desc = f.read()
setup(
    name='palindrome-validator-checker',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Your Name',
    description='A Python library to validate if a string is a palindrome.',
    python_requires='>=3.6',
)
