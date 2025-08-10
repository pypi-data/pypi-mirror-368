from setuptools import setup, find_packages

setup(
    name='vital-agent-container-sdk',
    version='0.1.12',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='Vital Agent Container SDK',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/vital-agent-container-python',
    packages=find_packages(exclude=["test"]),
    entry_points={

    },
    scripts=[

    ],
    package_data={
        '': ['*.pyi']
    },
    license='Apache License 2.0',
    install_requires=[
        'vital-ai-vitalsigns>=0.1.32',
        'vital-ai-aimp>=0.1.12',
        'httpx>=0.28.0',
        'python-json-logger>=2.0.7',
        'python-dotenv>=1.0.1',
        'uvicorn[standard]>=0.35.0',
        'fastapi>=0.116.0',
        'starlette>=0.36.3',
        'pyyaml>=6.0.1',
        'requests>=2.31.0'
    ],
    extras_require={
        'dev': [
            'build>=1.0.0',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
