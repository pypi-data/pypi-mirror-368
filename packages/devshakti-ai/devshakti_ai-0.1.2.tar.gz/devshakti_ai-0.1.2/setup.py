from setuptools import setup, find_packages

# ADD THIS - Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='devshakti-ai',
    version='0.1.2',  # Bump the version
    description='Python SDK for Shakti LLM API - OpenAI compatible',
    long_description=long_description,  # ADD THIS
    long_description_content_type='text/markdown',  # ADD THIS
    author='Shivnath Tathe',
    author_email='sptathe2001@gmail.com',
    url='https://shakti-one.vercel.app',  # ADD THIS
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    keywords='shakti ai llm api sdk openai',  # ADD THIS
)