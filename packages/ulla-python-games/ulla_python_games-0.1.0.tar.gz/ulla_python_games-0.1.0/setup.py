from setuptools import setup, find_packages

setup(
    name='ulla_python_games',
    version='0.1.0',
    author='Afnan',
    author_email='afnan.ulla@synechron.com',
    description='A collection of Python games for learning and fun',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if needed
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)