import os
from setuptools import setup, find_packages

readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")

with open(readme_path, "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name='sam_url_cache',
    version='0.4',
    author='Sam Pomerantz',
    author_email='sam@sampomerantz.me',
    description='A simple URL caching library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    project_urls={
        'Source': 'https://github.com/SamPom100/sam-url-cache',
        'Portfolio': 'https://sampomerantz.me',
    }
)