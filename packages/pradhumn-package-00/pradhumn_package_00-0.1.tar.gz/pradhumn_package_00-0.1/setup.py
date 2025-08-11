from setuptools import setup, find_packages

setup(
    name='pradhumn_package_00',                  
    version='0.1',
    packages=find_packages(),           
    description='A package with a function that computes Q-values and uses matplotlib',
    author='pradhumn',
    author_email='pradhumn.nmims@gmail.com',
    python_requires='>=3.6',
    install_requires=[
        'matplotlib', 'random'                
    ],
)
