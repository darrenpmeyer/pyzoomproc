from setuptools import setup

setup(
    name='pyzoomproc',
    version='0.1',
    py_modules=['pyzoomproc'],
    install_requires=[
        'Click','psutil'
    ],
    entry_points='''
        [console_scripts]
        pyzoomproc=pyzoomproc.__main__:main
    ''',
)