from setuptools import setup, find_packages

setup(
    name='modmac',
    version='0.1.0',
    description='A simple command-line tool to format MAC addresses in standard styles.',
    author='Maksym Ototiuk',
    author_email='mac@masik.slmail.me', 
    url='https://github.com/Maksym-Ototiuk/macmod', 
    packages=find_packages(), 
    install_requires=[
        'pyperclip',
    ],
    entry_points={
        'console_scripts': [
            'mac = macmod.macmod:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
