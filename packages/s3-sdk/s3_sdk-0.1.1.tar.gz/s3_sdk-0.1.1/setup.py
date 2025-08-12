from setuptools import setup, find_packages

setup(
    name='s3_sdk',
    version='0.1.1',
    packages=find_packages(),
    install_requires=['boto3>=1.26.0'],
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple SDK for interacting with AWS S3',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/s3_sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)