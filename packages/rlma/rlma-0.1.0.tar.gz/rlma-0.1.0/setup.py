from setuptools import setup

setup(
    name='rlma',
    version='0.1.0',
    author='Francis Jemisiham Amofa',
    author_email='jemisihamamofa@gmail.com',
    description='Robust Linear Matching Algorithm (RLMA) for variable association detection',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/francisamofa/rlma',
    py_modules=['rlma'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'scikit-learn',
    ],
)
