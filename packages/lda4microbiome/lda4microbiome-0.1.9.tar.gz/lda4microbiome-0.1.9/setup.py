from setuptools import setup, find_packages

setup(
    name='lda4microbiome',
    version='0.1.9',
    author='Peiyang Huo',
    author_email='peiyang.huo@kuleuven.be',
    description='A workflow for LDA analysis of microbiome data using MALLET',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.kuleuven.be/aida-lab/projects/LDA4Microbiome_Workflow',  # Update this to your URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'gensim',
        'little-mallet-wrapper',
        'plotly>=5.0.0',
        'scipy',
    ],
)

