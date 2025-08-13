from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='my-nalog',
    version='0.1.1',
    author='S1qwy',
    author_email='amirhansuper75@gmail.com',
    description='Python client for lknpd.nalog.ru API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/S1qwy/my-nalog',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)