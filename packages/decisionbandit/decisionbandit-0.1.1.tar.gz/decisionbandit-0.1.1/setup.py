from setuptools import setup, find_packages
 
setup(
    name='decisionbandit',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    author='Adit Punamiya',
    author_email='adit@gmail.com',
    description='A collection of exploration–exploitation strategies for reinforcement learning, including ε-greedy and related policies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    python_requires='>=3.8',
)