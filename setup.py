from setuptools import setup, find_packages

import antaresia

setup(
    name='antaresia',
    version=antaresia.__version__,
    download_url='https://github.com/asnelzin/antaresia',
    author=antaresia.__author__,
    author_email='asnelzin@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'antaresia = antaresia.__main__:main',
        ],
    }
)