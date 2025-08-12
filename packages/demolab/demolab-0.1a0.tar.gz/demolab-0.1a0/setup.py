from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# 获取项目描述
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='demolab',
    version='0.1.a',
    description='A Flask web application for URL redirection and workspace management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/levindemo/demolab',
    author='levin',
    author_email='your.email@example.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='flask, url, redirect, workspace',
    packages=find_packages(include=['demolab', 'demolab.*']),
    python_requires='>=3.7, <4',
    install_requires=[
        'flask>=2.0.0',
        'requests>=2.26.0',
    ],
    entry_points={
        'console_scripts': [
            'demolab=demolab:main',
        ],
    },
    package_data={
        'demolab': ['templates/*.html', 'static/css/*.css'],
    },
    data_files=[('config', ['demolab/userconfig.json'])],
)
