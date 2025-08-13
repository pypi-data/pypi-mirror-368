from setuptools import setup, find_packages

setup(
    name='devshakti-ai',  # ← Change this from 'shakti' to 'devshakti-ai'
    version='0.1.0',
    description='Python SDK for Shakti LLM API',
    author='Shivnath Tathe',
    author_email='sptathe2001@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)