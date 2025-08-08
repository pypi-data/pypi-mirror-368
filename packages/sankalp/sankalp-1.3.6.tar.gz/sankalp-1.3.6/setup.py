from setuptools import setup, find_packages

setup(
    name='sankalp',
    version='1.3.6',  # Increment version for updates
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "sankalp": ["blue.mp3"],
    },
    install_requires=[
        'rich',
        'PyInquirer',
        'pygame',
        'windows-curses; platform_system=="Windows"',  # Fix curses issue on Windows
    ],
    entry_points={
        'console_scripts': [
            'sankalp = sankalp.cli:run_cli',  # Maps "sankalp" command to run_cli in cli.py
        ],
    },
    python_requires='>=3.6',
    author='Sankalp Shrivastava',
    author_email='1sankalpshrivastava@gmail.com',
    description='A CLI package for Sankalp Shrivastava',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/1sankalp',
)
