from setuptools import setup, find_packages
import os

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join('please_do_not_define', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

setup(
    name='please_do_not_define',
    version=about['__version__'],
    description='A Python library that prevents defining female-related names in code',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='13140752715@163.com',
    url='https://github.com/Locked-chess-official/please_do_not_define',
    packages=find_packages(include=['please_do_not_define', 'please_do_not_define.*']),
    install_requires=[],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    keywords='naming-conventions code-quality gender-neutral',
    project_urls={
        'Source': 'https://github.com/Locked-chess-official/please_do_not_define',
        'Bug Reports': 'https://github.com/Locked-chess-official/please_do_not_define/issues',
    },
    entry_points={
        'console_scripts': [
            'checkname=please_do_not_define.__main__:main',
        ],
    },
)
