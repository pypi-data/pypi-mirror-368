from setuptools import setup, find_packages

setup(
    name='autowebx',
    version='1.7.0',
    description='Added 22.do integration',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'functioner = autowebx.__init__:__get_function__',
        ],
    },

    install_requires=[
        'requests>=2.32.3',
        'beautifulsoup4>=4.13.4',
        'names>=0.3.0',
        'phonenumbers>=9.0.6',
        'colorama>=0.4.6',
        'art>=6.5',
        'multipledispatch>=1.0.0',
        'ntplib>=0.4.0'
    ]
)
