from setuptools import setup, find_packages

# If you created README.md, you can include it as long description.
with open('README.md', 'r', encoding='utf-8') as f:
    description = f.read()

setup(
    name='explorex',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21'
    ],
    long_description=description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    description='Tiny action-selection helpers for demos.'
)
