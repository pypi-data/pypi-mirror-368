from setuptools import (
    setup,
    find_packages
)


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='locust_swarm_wrapper_lib',
    version='0.0.1',
    author='Cupcake_wrld',
    author_email='evilprog@yandex.ru',
    description='App for loading testing, wrapper for locust library',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent'
    ],
    keywords='files small console load_testing',
    python_requires='>=3.12'
)
