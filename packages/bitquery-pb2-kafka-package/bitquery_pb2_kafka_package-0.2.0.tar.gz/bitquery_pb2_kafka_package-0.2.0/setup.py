from setuptools import setup, find_packages

setup(
    name='bitquery-pb2-kafka-package',
    version='0.2.0',
    packages=find_packages(),
    author='Bitquery',
    author_email='divyasshree@bitquery.io',
    description='This package contains the pb2 files necessary to interact with Bitquery Kafka Protobuf messages',
    long_description=open("README.md", "r", encoding="utf-8").read(),  # Ensuring UTF-8 encoding
    long_description_content_type="text/markdown",  # Explicitly set Markdown format
    url='https://github.com/bitquery/streaming-protobuf-python', 
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
