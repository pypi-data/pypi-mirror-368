from setuptools import setup, find_packages

setup(
    name='file_golem',
    version='0.1.13',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'omegaconf',
        'filelock'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'file_io_main = file_io.main:main',
    #     ],
    # },
    author='Cameron Braunstein',
    author_email='your.email@example.com',
    description='A file i/o utility to handle complex projects with multiple datasets, project locations and calls to 3rd party codebases.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CameronBraunstein/file_golem',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)