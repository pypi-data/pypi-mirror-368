from setuptools import setup, find_packages

setup(
    name='my_kegg_app',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='KEGG Reactions and EC Finder Web App',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'pandas',
        'requests',
        'biopython'
    ],
    entry_points={
        'console_scripts': [
            'run-kegg-app=my_kegg_app.__main__:main',
        ],
    },
    python_requires='>=3.7',
)
