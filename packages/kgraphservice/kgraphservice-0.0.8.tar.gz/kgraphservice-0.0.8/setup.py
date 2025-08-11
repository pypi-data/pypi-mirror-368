from setuptools import setup, find_packages

setup(
    name='kgraphservice',
    version='0.0.8',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='KGraph Service',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/kgraphservice',
    packages=find_packages(exclude=["test","vitalhome","test_data","docs"]),
    license='Apache License 2.0',
    scripts=[
        'bin/kgraphservice'
    ],
    install_requires=[
        'vital-ai-vitalsigns>=0.1.32',
        'vital-ai-domain>=0.1.7',
        'six==1.16.0',
        'pyyaml==6.0.2',
        'vital-ai-haley-kg>=0.1.24',
        'rdflib>=7.0.0',
        'SPARQLWrapper==2.0.0',
        'networkx>=3.3',
        'uvicorn[standard]>=0.27.0.post1',
        'fastapi>=0.109.2',
        'requests==2.32.3',
        'boto3>=1.35.36',
        'aioboto3>=13.2.0',
        'python-multipart>=0.0.12'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12'
)
