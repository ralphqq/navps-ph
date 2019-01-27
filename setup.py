from setuptools import setup

setup(
    name='navps-ph',
    version='1.1.0',
    py_modules=['main'],
    include_package_data=True,
    install_requires=[
        'bs4',
        'Click',
        'lxml',
        'python-dateutil',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        navps=main:run
    ''',
)