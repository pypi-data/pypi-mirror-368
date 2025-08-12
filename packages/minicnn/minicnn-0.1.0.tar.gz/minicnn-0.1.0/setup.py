from setuptools import setup, find_packages

setup(
    name='MiniCNN',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'torch>=2.0.0',
    ],
    author='Your Name',
    author_email='your_email@example.com',
    description='Minimal, well-documented CNN models for image classification. Great for beginners!',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='>=3.8',
)