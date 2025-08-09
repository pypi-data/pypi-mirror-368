from setuptools import setup, find_packages

setup(
    name='pyxend',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click',
        'jinja2'
    ],
    entry_points={
        'console_scripts': [
            'pyxend=pyxend.cli:cli'
        ]
    },
    python_requires=">=3.8"
)
