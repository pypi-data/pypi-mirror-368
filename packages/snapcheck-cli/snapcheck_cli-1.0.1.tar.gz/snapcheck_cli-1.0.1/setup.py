from setuptools import setup, find_packages

setup(
    name='snapcheck',
    version='0.1',
    description='SnapCheck - DevOps/MLOps auditing CLI tool',
    author='Goutham Yadav Ganta',
    py_modules=['main'],  # ✅ This is key since main.py is not inside a package
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pyyaml',
        'rich',
        'requests',
        'tabulate',
        'boto3',
        'kubernetes',
        'yarl',
        'markdown2',
        'matplotlib',
        'jinja2',
        'docker',
        'termcolor',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'snapcheck=main:cli',  # ✅ Use cli() as entrypoint
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)

