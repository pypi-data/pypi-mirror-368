from setuptools import setup, find_packages

setup(
    name='llm_optimizer',
    version='0.1.0',
    description='Optimize LLM outputs and track emissions',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Vijayalakshmi',
    author_email='viji814881@email.com',
    url='https://github.com/viji123450/llm_optimizer',  # <-- OPTIONAL: link to your repo
    license='MIT',  # <-- or any license you prefer
    packages=find_packages(),
    install_requires=[
        'torch',
        'transformers',
        'codecarbon',
        'evaluate',
        'numpy',
        'rouge_score',
        'nltk',
        'absl-py'
    ],
    entry_points={
        'console_scripts': [
            'llm-optimize=llm_optimizer.main:load_and_generate',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)