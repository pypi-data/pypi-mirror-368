from setuptools import setup, find_packages

setup(
    name='ml_golem',
    version='0.1.10',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'file_golem',
        'torch',
        'accelerate',
        'tensorboard',
        'pandas'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'ml_lib_main = ml_lib.main:main',
    #     ],
    # },
    author='Cameron Braunstein',
    author_email='your.email@example.com',
    description='A description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CameronBraunstein/ml_golem',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)