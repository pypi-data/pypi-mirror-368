# setup.py

from setuptools import setup, find_packages

setup(
    name='searchmind',
    version='0.1.2',
    author='Niansuh',
    author_email='niansuhtech@gmail.com',
    description='A simple Python wrapper for the Snapzion Search API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-username/searchmind', # Replace with your repo URL
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)