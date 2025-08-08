from setuptools import setup, find_packages

# Read README for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Command-line interface for the Codicent API"

setup(
    name='codicent-cli',
    version='0.4.7',
    author='Johan Isaksson',
    author_email='johan@izaxon.com',
    description='Command-line interface for the Codicent API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/izaxon/codicent-cli',
    project_urls={
        'Bug Reports': 'https://github.com/izaxon/codicent-cli/issues',
        'Source': 'https://github.com/izaxon/codicent-cli',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='codicent cli api chat ai',
    py_modules=['app', 'auth'],
    python_requires='>=3.6',
    install_requires=[
        'rich',
        'codicent-py',
        'prompt_toolkit',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'codicent=app:main',
        ],
    },
)
