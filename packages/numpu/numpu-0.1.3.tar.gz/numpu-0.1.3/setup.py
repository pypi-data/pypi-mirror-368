from setuptools import setup, find_packages

setup(
    name='numpu',                # the package name
    version='0.1.3',
    description='Quick chat shortcuts for g4f and HuggingFace models',
    author='aaaroo',
    author_email='you@example.com',
    packages=find_packages(),
    install_requires=[
        'g4f>=0.1.0',
        'huggingface_hub>=0.23.0'
    ],
    python_requires='>=3.7',
)
