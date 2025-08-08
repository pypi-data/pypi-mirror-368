from setuptools import setup, find_packages

setup(
    name='lambda-cloud-cli',
    version='0.1.34',
    description='CLI tool for managing Lambda Cloud resources',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Taylor Gautreaux',
    author_email='you@example.com',
    url='https://github.com/yourusername/lambda-cloud-cli',
    license='MIT',
    packages=find_packages(),  # Finds lambda_cloud_cli/
    install_requires=[
        'typer',
        'requests',
        'shellingham',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'lambda-cli=lambda_cloud_cli.cli:app',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

